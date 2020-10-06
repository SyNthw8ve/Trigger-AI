from typing import Any, List, Tuple, Optional, Dict
import numpy as np
import faiss
import time

from scipy.spatial.distance import cosine
from scipy.spatial.distance import cdist

from trigger.models.match import Match

from trigger.train.cluster.gturbo.graph import Graph
from trigger.train.cluster.gturbo.node import Node
from trigger.train.cluster.gturbo.link import Link
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.Processor import Processor


class GTurbo(Processor):

    def __init__(self, epsilon_b: float, epsilon_n: float, lam: int, beta: float,
                 alpha: float, max_age: int, r0: float,
                 dimensions: int = 2, random_state: int = 42) -> None:

        self.graph = Graph()

        self.epsilon_b = epsilon_b
        self.epsilon_n = epsilon_n
        self.lam = lam
        self.beta = beta
        self.alpha = alpha
        self.max_age = max_age
        self.dimensions = dimensions
        self.r0 = r0

        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(dimensions))

        self.next_id = 2
        self.point_to_cluster = {}
        self.instances = {}
        self.tag_to_data = {}

        self.cycle = 0
        self.step = 1

        np.random.seed(random_state)

        node_1 = Node(np.random.rand(1, dimensions).astype(
            'float32')[0], 0, id=0, error_cycle=0, radius=r0)
        node_2 = Node(np.random.rand(1, dimensions).astype(
            'float32')[0], 0, id=1, error_cycle=0, radius=r0)

        self.graph.insert_node(node_1)
        self.graph.insert_node(node_2)

        self.index.add_with_ids(
            np.array([node_1.protype, node_2.protype]), np.array([0, 1]))

    def turbo_step(self, tag, instance):

        self.turbo_adapt(tag, instance)

        if self.step == self.lam - 1:

            self.turbo_increase()
            self.cycle += 1
            self.step = 0

        else:

            self.step += 1

    def create_node(self, q: Node, f: Node, radius: float) -> Node:

        r = Node(0.5*(q.protype + f.protype), 0,
                 self.next_id, self.cycle, radius)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def create_node_from_instance(self, instance, radius: float) -> Node:

        r = Node(instance, 0, self.next_id, self.cycle, radius)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def turbo_increase(self) -> None:

        q, f = self.graph.get_q_and_f()

        r = self.create_node(q, f, self.r0)

        link = self.graph.get_link(q, f)

        q.remove_neighbor(f)
        f.remove_neighbor(q)

        self.graph.remove_link(q, f)

        self.create_link(q, r)
        self.create_link(f, r)

        self.decrease_error(q)
        self.decrease_error(f)

        r.error = 0.5*(q.error + f.error)
        self.graph.update_heap()

    def get_best_match(self, instance) -> Tuple[Node, Node]:

        D, I = self.index.search(np.array([instance]).astype('float32'), 2)

        return (self.graph.get_node(I[0][0]), self.graph.get_node(I[0][1]))

    def increment_error(self, node: Node, value: float) -> None:

        self.fix_error(node)
        node.error = node.error * \
            (np.power(self.beta, self.lam - self.step)) + value

        self.graph.update_heap()

    def fix_error(self, node: Node) -> None:

        node.error = np.power(self.beta, self.lam *
                              (self.cycle - node.error_cycle))*node.error
        node.update_error_cycle(self.cycle)

    def update_prototype(self, v: Node, scale: float, instance) -> None:

        self.index.remove_ids(np.array([v.id]))

        v.protype += scale*(instance - v.protype)

        self.index.add_with_ids(np.array([v.protype]), np.array([v.id]))

    def distance(self, u, v) -> float:

        return cdist([u], [v], "euclidean")[0]

    def turbo_adapt(self, tag: str, instance):

        v, u = self.get_best_match(instance)

        if self.distance(v.protype, instance) <= v.radius:

            v.add_instance(tag)
            self.instances[tag] = instance

            self.point_to_cluster[tag] = v.id

            error_value = np.power(self.distance(
                v.protype, instance), 2)[0]

            self.increment_error(v, error_value)

            self.update_prototype(v, self.epsilon_b, instance)

            for node in v.topological_neighbors.values():

                self.update_prototype(node, self.epsilon_n, instance)

            self.age_links(v)

            if not self.graph.has_link(v, u):

                self.create_link(v, u)

            link = self.graph.get_link(v, u)
            link.renew()

            self.update_edges(v)
            self.update_nodes()

        else:

            r = self.create_node_from_instance(instance, self.r0)
            r.add_instance(tag)

            self.instances[tag] = instance
            self.point_to_cluster[tag] = r.id

            self.create_link(v, r)

    def decrease_error(self, v: Node) -> None:

        self.fix_error(v)

        v.error *= self.alpha
        self.graph.update_heap()

    def create_link(self, v: Node, u: Node) -> None:

        link = Link(v, u)

        self.graph.insert_link(v, u, link)

        v.add_neighbor(u)
        u.add_neighbor(v)

    def update_nodes(self) -> None:

        nodes_to_remove = []

        for node in self.graph.nodes.values():

            if len(node.topological_neighbors) == 0 and len(node.instances) == 0:

                nodes_to_remove.append(node)

        for node in nodes_to_remove:

            self.graph.remove_node(node)
            self.index.remove_ids(np.array([node.id]))

    def age_links(self, v: Node) -> None:

        for u in v.topological_neighbors.values():

            link = self.graph.get_link(v, u)

            link.fade()

    def update_edges(self, v: Node) -> None:

        links_to_remove = []

        for u in v.topological_neighbors.values():

            link = self.graph.get_link(v, u)

            if link.age > self.max_age:

                links_to_remove.append((v, u))

        for v, u in links_to_remove:

            v.remove_neighbor(u)
            u.remove_neighbor(v)

            self.graph.remove_link(v, u)

    def get_cluster(self, instance) -> int:

        return self.point_to_cluster.get(instance)

    def re_ignite(self, epsilon_b, lam, max_age, r0) -> "GTurbo":

        new_turbo = GTurbo(epsilon_b=epsilon_b, epsilon_n=self.epsilon_n, lam=lam, beta=self.beta,
                           alpha=self.alpha, max_age=max_age, r0=r0, dimensions=self.dimensions)

        for tag, instance in self.instances.items():

            new_turbo.turbo_step(tag, instance)

        return new_turbo

    def process(self, tag: str, instance: np.ndarray, custom_data: Any = None) -> None:

        self.turbo_step(tag, instance)
        self.tag_to_data[tag] = custom_data

    def update(self, tag: str, instance: np.ndarray, custom_data: Any = None) -> None:

        self.remove(tag)

        self.process(tag, instance, custom_data)

    def remove(self, tag: str) -> None:

        node_id = self.point_to_cluster.pop(tag)
        self.instances.pop(tag)
        self.tag_to_data.pop(tag)

        node = self.graph.get_node(node_id)
        node.remove_instance(tag)

    def get_cluster_by_tag(self, tag: str) -> Optional[int]:

        return self.point_to_cluster[tag]

    def get_custom_data_by_tag(self, tag: str) -> Optional[Any]:

        return self.tag_to_data[tag]

    def get_instances_and_tags_in_cluster(self, cluster_id: int) -> Tuple[List[np.ndarray], List[str]]:

        tags = [tag for tag, id in self.point_to_cluster.items() if id ==
                cluster_id]
        instances = [self.instances[tag] for tag in tags]

        return (instances, tags)

    def get_all_instances_with_tags(self) -> Tuple[List[np.ndarray], List[str]]:

        instances = [instance for instance in self.instances.values()]
        tags = [tag for tag in self.instances.keys()]

        return (instances, tags)

    def predict(self, instance: np.ndarray) -> int:

        return self.get_best_match(instance)[0].id

    def describe(self) -> Dict[str, Any]:

        return {
            "name": "GTurbo",
            "parameters": {
                "epsilon_b": self.epsilon_b,
                "epsilon_n": self.epsilon_n,
                "lam": self.lam,
                "beta": self. beta,
                "alpha": self.alpha,
                "max_age": self.max_age,
                "radius": self.r0
            }
        }

    def safe_file_name(self) -> str:

        return f"GTurbo = epsilon_b={self.epsilon_b};epsilon_n={self.epsilon_n};lam={self.lam};beta={self.beta};alpha={self.alpha};max_age={self.max_age};radius={self.r0}"

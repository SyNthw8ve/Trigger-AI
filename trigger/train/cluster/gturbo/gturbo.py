from typing import Any, List, Tuple
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

class GTurbo():

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
        self.instances = []

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

    def gng_step(self, instance: OpeningInstance):

        self.gng_adapt(instance)

        if self.step == self.lam - 1:

            self.gng_grow()
            self.cycle += 1
            self.step = 0

        else:

            self.step += 1

    def create_node(self, q: Node, f: Node, radius:float) -> Node:

        r = Node(0.5*(q.protype + f.protype), 0, self.next_id, self.cycle, radius)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def create_node_from_instance(self, instance, radius:float) -> Node:

        r = Node(instance, 0, self.next_id, self.cycle, radius)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def gng_grow(self) -> None:

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

    def gng_adapt(self, instance: OpeningInstance):

        v, u = self.get_best_match(instance.embedding)

        if self.distance(v.protype, instance.embedding) <= v.radius:
            
            v.add_instance(instance)
            self.instances.append(instance)

            self.point_to_cluster[instance] = v.id
            instance.cluster_index = v.id

            error_value = np.power(self.distance(v.protype, instance.embedding), 2)[0]

            self.increment_error(v, error_value)

            self.update_prototype(v, self.epsilon_b, instance.embedding)

            for node in v.topological_neighbors.values():

                self.update_prototype(node, self.epsilon_n, instance.embedding)

            self.age_links(v)

            if not self.graph.has_link(v, u):

                self.create_link(v, u)

            link = self.graph.get_link(v, u)
            link.renew()

            self.update_edges(v)
            self.update_nodes()

        else:

            r = self.create_node_from_instance(instance.embedding, self.r0)
            r.add_instance(instance)

            self.instances.append(instance)
            instance.cluster_index = r.id
            self.point_to_cluster[instance] = r.id

            self.create_link(v, r)
            self.create_link(u, r)

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

    def remove_data(self, instance: OpeningInstance):
        
        node = self.graph.get_node(instance.cluster_index)
        node.remove_instance(instance)

        if len(node.instances) == 0:

            self.graph.remove_node(node)
            self.index.remove_ids(np.array([node.id]))

    def get_cluster(self, instance) -> int:

        return self.point_to_cluster.get(instance)
from typing import Any, List, Tuple
import numpy as np
import faiss
import time

from trigger.train.cluster.gstream.graph import Graph
from trigger.train.cluster.gstream.node import Node
from trigger.train.cluster.gstream.link import Link
from util.stream.processor import Processor

from scipy.spatial.distance import cdist
from matplotlib import pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

class GNG(Processor):

    def __init__(self, epsilon_b: float, epsilon_n: float, lam: int, beta: float, 
                    alpha: float, lambda_2: float, max_age: float, off_max_age: int,
                    aging: str='counter', dimensions: int=2, nodes_per_cycle=1) -> None:

        self.graph = Graph()

        self.epsilon_b = epsilon_b
        self.epsilon_n = epsilon_n
        self.lam = lam
        self.beta = beta
        self.alpha = alpha
        self.max_age = max_age
        self.off_max_age = off_max_age
        self.aging = aging
        self.lambda_2 = lambda_2
        self.nodes_per_cycle = nodes_per_cycle

        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(dimensions))
        self.next_id = 2
        self.point_to_cluster = {}
        self.instances = []

        self.cycle = 0
        self.step = 1
    
        node_1 = Node(np.random.rand(1, dimensions).astype('float32')[0], 0, id=0, error_cycle=0)
        node_2 = Node(np.random.rand(1, dimensions).astype('float32')[0], 0, id=1, error_cycle=0)

        self.graph.insert_node(node_1)
        self.graph.insert_node(node_2)

        self.index.add_with_ids(np.array([node_1.protype, node_2.protype]), np.array([0, 1]))
    
    def process(self, instance):

        self.online_fase(instance)

    def online_fase(self, instance: Any) -> None:

        self.gng_adapt(instance)

        if self.step == self.lam - 1:
            
            self.gng_grow()
            self.cycle += 1
            self.step = 0

        else:
        
            self.step += 1

    def create_node(self, q: Node, f: Node) -> Node:

        r = Node(0.5*(q.protype + f.protype), 0, self.next_id, self.cycle)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def gng_grow(self) -> None:
       
        for i in range(self.nodes_per_cycle):

            q, f = self.graph.get_q_and_f()

            r = self.create_node(q, f)

            link = self.graph.get_link(q, f)

            q.remove_neighbor(f)
            f.remove_neighbor(q)

            self.graph.remove_link(q, f)

            self.create_link(q, r, self.aging)
            self.create_link(f, r, self.aging)

            self.decrease_error(q)
            self.decrease_error(f)

            r.error = 0.5*(q.error + f.error)
            self.graph.update_heap()

    def get_best_match(self, instance) -> Tuple[Node, Node]:

        D, I = self.index.search(np.array([instance]), 2)
        
        return (self.graph.get_node(I[0][0]), self.graph.get_node(I[0][1]))

    def increment_error(self, node: Node, value: float) -> None:

        self.fix_error(node)
        node.error = node.error*(np.power(self.beta, self.lam - self.step)) + value

        self.graph.update_heap()

    def fix_error(self, node: Node) -> None:

        node.error = np.power(self.beta, self.lam*(self.cycle - node.error_cycle))*node.error
        node.update_error_cycle(self.cycle)

    def update_prototype(self, v: Node, scale: float, instance) -> None:

        self.index.remove_ids(np.array([v.id]))

        v.protype += scale*(instance - v.protype)

        self.index.add_with_ids(np.array([v.protype]), np.array([v.id]))

    def gng_adapt(self, instance) -> None:

        v, u = self.get_best_match(instance)

        v.instances.append(instance)
        self.instances.append(instance)

        self.point_to_cluster[tuple(instance)] = v.id

        error_value = np.power(cdist([v.protype],
                               [instance], "euclidean")[0], 2)[0]

        self.increment_error(v, error_value)

        self.update_prototype(v, self.epsilon_b, instance)

        for node in v.topological_neighbors.values():

            self.update_prototype(node, self.epsilon_n, instance)

        self.age_links(v)

        if not self.graph.has_link(v, u):

            self.create_link(v, u, self.aging)

        link = self.graph.get_link(v, u)
        link.renew()

        self.update_edges(v, False)
        self.update_nodes()

    def decrease_error(self, v: Node) -> None:

        self.fix_error(v)

        v.error *= self.alpha
        self.graph.update_heap()

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

            link.fade(lambda_2=self.lambda_2)

    def update_edges(self, v: Node, offline: bool) -> None:

        links_to_remove = []
        
        for u in v.topological_neighbors.values():

            link = self.graph.get_link(v, u)

            if (not offline and link.age > self.max_age) or (offline and link.age > self.off_max_age):

                links_to_remove.append((v, u))

        for v, u in links_to_remove:

            v.remove_neighbor(u)
            u.remove_neighbor(v)

            self.graph.remove_link(v, u)  

    def create_link(self, v: Node, u: Node, age_type: str) -> None:

        link = Link(v, u, age_type)

        self.graph.insert_link(v, u, link)

        v.add_neighbor(u)
        u.add_neighbor(v)

    def plot2D(self, path):

        seen = []
        plt.clf()

        for v in self.graph.nodes.values():

            v_inst_X = [v.protype[0]]
            v_inst_Y = [v.protype[1]]

            for instance in v.instances:
            
                v_inst_X.append(instance[0])
                v_inst_Y.append(instance[1])

            plt.scatter(v_inst_X, v_inst_Y, edgecolors='black')
        
        for v in self.graph.nodes.values():

            for u in v.topological_neighbors.values():

                    if ((u, v) not in seen) and ((v, u) not in seen):

                        plt.plot([v.protype[0], u.protype[0]], [v.protype[1], u.protype[1]], 'r')
                        seen.append((v, u))
            
            plt.plot(v.protype[0], v.protype[1], 'or')

        plt.savefig(path)

    def plot3D(self, path):

        seen = []
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for v in self.graph.nodes.values():

            v_inst_X = [v.protype[0]]
            v_inst_Y = [v.protype[1]]
            v_inst_Z = [v.protype[2]]

            for instance in v.instances:
            
                v_inst_X.append(instance[0])
                v_inst_Y.append(instance[1])
                v_inst_Z.append(instance[2])

            ax.scatter(v_inst_X, v_inst_Y, v_inst_Z)
        
        for v in self.graph.nodes.values():

            for u in v.topological_neighbors.values():

                    if ((u, v) not in seen) and ((v, u) not in seen):

                        ax.plot([v.protype[0], u.protype[0]], [v.protype[1], u.protype[1]],
                                    [v.protype[2], u.protype[2]], 'r')
                        seen.append((v, u))
            
            ax.plot([v.protype[0]], [v.protype[1]], [v.protype[2]], 'or')

        plt.show()
        plt.savefig(path)
        plt.clf()


    def get_cluster(self, instance) -> int:

        return self.point_to_cluster.get(tuple(instance))

    def offline_fase(self):

        self.graph.partial_reset()
    
        for instance in self.instances:

            v, u = self.get_best_match(instance)

            v.instances.append(instance)

            self.point_to_cluster[tuple(instance)] = v.id

            self.update_prototype(v, self.epsilon_b, instance)

            for node in v.topological_neighbors.values():

                self.update_prototype(node, self.epsilon_n, instance)

            self.age_links(v)

            if not self.graph.has_link(v, u):

                self.create_link(v, u, 'counter')

            link = self.graph.get_link(v, u)
            link.renew()

            self.update_edges(v, True)

        self.offline_node_update()
        self.offline_link_update()

    def offline_node_update(self):

        to_remove = []

        for node in self.graph.nodes.values():

            if len(node.instances) == 0:

                to_remove.append(node)

        for node in to_remove:

            for u in node.topological_neighbors.values():

                u.remove_neighbor(node)
                self.graph.remove_link(node, u)

            self.graph.remove_node(node)
            self.index.remove_ids(np.array([node.id]))

    def offline_link_update(self):

        creation_time = time.time()

        for link in self.graph.links.values():

            link.age = 0
            link.aging = 'time'
            link.creation_time = creation_time
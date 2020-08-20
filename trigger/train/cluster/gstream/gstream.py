from typing import Any, List, Tuple
import numpy as np
import faiss

from trigger.train.cluster.gstream.graph import Graph
from trigger.train.cluster.gstream.node import Node
from trigger.train.cluster.gstream.link import Link

from scipy.spatial.distance import cdist
from matplotlib import pyplot as plt 

class GStream:

    def __init__(self, vector_size: int, alpha1: float, alpha2: float, beta: float, error_decrease: float):

        self.graph = Graph()
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.beta = beta
        self.error_decrease = error_decrease
        self.cycle = 0

        node_1 = Node(np.random.rand(1, vector_size)[0], 0, 0)
        node_2 = Node(np.random.rand(1, vector_size)[0], 0, 0)
        node_1.topological_neighbors.append(node_2)
        node_2.topological_neighbors.append(node_1)

        self.graph.insert_node(node_1)
        self.graph.insert_node(node_2)

        self.is_first_pass = True

    def got_data(self, instances: List[Any]) -> None:

        if self.is_first_pass:

            self.first_pass(instances)
            self.is_first_pass = False

        else:
            self.other_pass(instances)

    def first_pass(self, instances: List[Any]) -> None:

        for instance in instances:

            bmu1, bmu2 = self.get_best_match(instance)

            self.cluster(instance, bmu1, bmu2)

        self.apply_deltas()

    def other_pass(self, instances: List[Any]) -> None:

        for instance in instances:

            bmu1, bmu2 = self.get_best_match(instance)

            if False:  # ∥xi − bmu1∥ > bmu1∥.delta:

                pass

            else:

                self.cluster(instance, bmu1, bmu2)

    def cluster(self, instance, bmu1: Node, bmu2: Node) -> None:

        self.cycle += 1

        bmu1.instances.append(instance)

        bmu1.error += np.power(cdist([bmu1.protype],
                               [instance], "euclidean")[0], 2)[0]

        bmu1.protype += self.alpha1*(instance - bmu1.protype)

        for node in bmu1.topological_neighbors:

            node.protype += self.alpha2*(instance - node.protype)

        self.update_edges()

        if self.cycle % self.beta == 0:

            for i in range(0, 3):

                self.create_nodes()

        self.do_fadding()

        self.decrease_error()

    def apply_deltas(self) -> None:

        for node in self.graph.nodes:

            node.delta = 0

            if len(node.instances) != 0:

                distances = cdist([node.protype], node.instances, "euclidean")[0]
            
                node.delta = max(distances)

    def do_fadding(self) -> None:
        pass

    def decrease_error(self) -> None:

        for node in self.graph.nodes:

            node.error *= self.error_decrease

    def update_edges(self) -> None:
        pass

    def create_nodes(self) -> None:

        q, f = self.graph.get_q_and_f()

        r = Node(0.5*(q.protype + f.protype), 0.5*(q.error + f.error), 0)

        r.topological_neighbors.append(q)
        r.topological_neighbors.append(f)

        q.topological_neighbors.append(r)
        f.topological_neighbors.append(r)

        q.topological_neighbors.remove(f)
        f.topological_neighbors.remove(q)

        self.graph.nodes.append(r)


    def get_best_match(self, instance) -> Tuple[Node, Node]:

        centers = [node.protype for node in self.graph.nodes]

        distances = cdist([instance], centers, "euclidean")[0]

        top_results = np.argpartition(-distances, range(2))[0:2]

        return (self.graph.nodes[top_results[0]], self.graph.nodes[top_results[1]])

class GNG:

    def __init__(self, epsilon_b: float, epsilon_n: float, lam: int, beta: float, alpha: float, max_age: int, vector_size: int) -> None:

        self.graph = Graph()
        self.epsilon_b = epsilon_b
        self.epsilon_n = epsilon_n
        self.lam = lam
        self.beta = beta
        self.alpha = alpha
        self.max_age = max_age
        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(vector_size))
        self.next_id = 2

        self.cycle = 0
        self.step = 1
    
        node_1 = Node(np.random.rand(1, vector_size).astype('float32')[0], 0, 0, id=0, error_cycle=0)
        node_2 = Node(np.random.rand(1, vector_size).astype('float32')[0], 0, 0, id=1, error_cycle=0)

        self.graph.insert_node(node_1)
        self.graph.insert_node(node_2)

        self.index.add_with_ids(np.array([node_1.protype, node_2.protype]), np.array([0, 1]))
    
    def lambda_fase(self, instances: List[Any]) -> None:

        for instance in instances:

            self.gng_adapt(instance)

            if self.step == self.lam - 1:
               
                self.gng_grow()
                self.cycle += 1
                self.step = 0

            else:
            
                self.step += 1

    def create_node(self, q: Node, f: Node) -> Node:

        r = Node(0.5*(q.protype + f.protype), 0, 0, self.next_id, self.cycle)
        self.next_id += 1

        self.graph.insert_node(r)
        self.index.add_with_ids(np.array([r.protype]), np.array([r.id]))

        return r

    def gng_grow(self) -> None:
       
        q, f = self.graph.get_q_and_f()

        r = self.create_node(q, f)

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

        error_value = np.power(cdist([v.protype],
                               [instance], "euclidean")[0], 2)[0]

        self.increment_error(v, error_value)

        self.update_prototype(v, self.epsilon_b, instance)

        for node in v.topological_neighbors.values():

            self.update_prototype(node, self.epsilon_n, instance)

        if not self.graph.has_link(v, u):

            self.create_link(v, u)

        link = self.graph.get_link(v, u)
        link.renew()

        self.update_edges(v)

    def decrease_error(self, v: Node) -> None:

        self.fix_error(v)

        v.error *= self.alpha
        self.graph.update_heap()

    def update_edges(self, v: Node) -> None:

        links_to_remove = []
        nodes_to_remove = []

        for u in v.topological_neighbors.values():

            link = self.graph.get_link(v, u)

            link.fade()

            if link.age > self.max_age:

                links_to_remove.append((v, u))

        for v, u in links_to_remove:

            v.remove_neighbor(u)
            u.remove_neighbor(v)

            self.graph.remove_link(v, u)

        for node in self.graph.nodes.values():

            if len(node.topological_neighbors) == 0:

                nodes_to_remove.append(node)
                
        for node in nodes_to_remove:

            self.graph.remove_node(node)
            self.index.remove_ids(np.array([node.id]))

    def create_link(self, v: Node, u: Node) -> None:

        link = Link(v, u)

        self.graph.insert_link(v, u, link)

        v.add_neighbor(u)
        u.add_neighbor(v)

    def plot(self):

        centers = [node.protype for node in self.graph.nodes.values()]

        X_g = [ data[0] for data in centers ]
        Y_g = [ data[1] for data in centers ]

        seen = []

        for v in self.graph.nodes.values():

            v_inst_X = [v.protype[0]]
            v_inst_Y = [v.protype[1]]

            for instance in v.instances:
            
                v_inst_X.append(instance[0])
                v_inst_Y.append(instance[1])

            plt.scatter(v_inst_X, v_inst_Y, edgecolors='black')
            #plt.plot(v_inst_X, v_inst_Y, 'or')

        for v in self.graph.nodes.values():

            for u in v.topological_neighbors.values():

                    if ((u, v) not in seen) and ((v, u) not in seen):

                        plt.plot([v.protype[0], u.protype[0]], [v.protype[1], u.protype[1]], 'r')
                        seen.append((v, u))
            
            plt.plot([v.protype[0]], [v.protype[1]], 'or')

        plt.savefig('plot.png')
        
        
    



    
from typing import Any, List, Tuple
import numpy as np

from trigger.train.cluster.gstream.graph import Graph
from trigger.train.cluster.gstream.node import Node
from trigger.train.cluster.gstream.link import Link

from scipy.spatial.distance import cdist
from matplotlib import pyplot as plt 
from celluloid import Camera

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

    def __init__(self, epsilon_b: float, epsilon_n: float, lam: int, beta: float, alpha: float, max_age: int, h_t: float, h_p: float, vector_size: int) -> None:

        self.graph = Graph()
        self.epsilon_b = epsilon_b
        self.epsilon_n = epsilon_n
        self.lam = lam
        self.beta = beta
        self.alpha = alpha
        self.max_age = max_age
        self.h_t = h_t
        self.h_p = h_p

        self.cycle = 1
        self.camera = camera

        node_1 = Node(np.random.rand(1, vector_size)[0] + 10, 0, 0)
        node_2 = Node(np.random.rand(1, vector_size)[0] + 10, 0, 0)

        self.graph.insert_node(node_1)
        self.graph.insert_node(node_2)

    def lambda_fase(self, instances: List[Any]) -> None:

        for instance in instances:

            self.plot()
            self.gng_adapt(instance)

            if self.cycle % self.lam == 0:
               
                self.create_node()

            self.cycle += 1

        self.plot()

    def create_node(self) -> None:

        q, f = self.graph.get_q_and_f()

        r = Node(0.5*(q.protype + f.protype), 0, 0)

        link = self.graph.get_link(q, f)

        q.topological_neighbors.remove(f)
        f.topological_neighbors.remove(q)

        self.graph.links.remove(link)

        self.create_link(q, r)
        self.create_link(f, r)

        self.decrease_error(q)
        self.decrease_error(f)

        r.error = 0.5*(q.error + f.error)

        self.graph.nodes.append(r)

    def get_best_match(self, instance) -> Tuple[Node, Node]:

        centers = [node.protype for node in self.graph.nodes]
        node_distance = []

        for node in self.graph.nodes:

            distance = cdist([instance], [node.protype], "euclidean")[0][0]
            node_distance.append((node, distance))

        node_distance = sorted(node_distance, key=lambda node: node[1])

        return (node_distance[0][0], node_distance[1][0])

    def gng_adapt(self, instance) -> None:

        v, u = self.get_best_match(instance)

        v.instances.append(instance)

        v.error += np.power(cdist([v.protype],
                               [instance], "euclidean")[0], 2)[0]

        v.protype += self.epsilon_b*(instance - v.protype)

        for node in v.topological_neighbors:

            node.protype += self.epsilon_n*(instance - node.protype)

        if not self.graph.has_link(v, u):

            self.create_link(v, u)

        link = self.graph.get_link(v, u)
        link.renew()

        self.update_edges(v)

        self.decrease_all_err()

    def decrease_error(self, v: Node) -> None:

        v.error *= self.alpha

    def decrease_all_err(self) -> None:

        for node in self.graph.nodes:

            node.error *= self.beta

    def update_edges(self, v: Node) -> None:

        for u in v.topological_neighbors:

            link = self.graph.get_link(v, u)

            link.fade()

            if link.age > self.max_age:

                v.topological_neighbors.remove(u)
                u.topological_neighbors.remove(v)

                self.graph.links.remove(link)

        for node in self.graph.nodes:

            if len(node.topological_neighbors) == 0:

                self.graph.nodes.remove(node)

    def create_link(self, v: Node, u: Node) -> None:

        link = Link(v, u)

        self.graph.insert_link(link)

        v.topological_neighbors.append(u)
        u.topological_neighbors.append(v)

    def plot(self):

        centers = [node.protype for node in self.graph.nodes]

        X_g = [ data[0] for data in centers ]
        Y_g = [ data[1] for data in centers ]

        seen = []

        for v in self.graph.nodes:

            v_inst_X = [v.protype[0]]
            v_inst_Y = [v.protype[1]]

            for instance in v.instances:
            
                v_inst_X.append(instance[0])
                v_inst_Y.append(instance[1])

            plt.scatter(v_inst_X, v_inst_Y, edgecolors='black')

        for v in self.graph.nodes:

            for u in v.topological_neighbors:

                    if ((u, v) not in seen) and ((v, u) not in seen):

                        plt.plot([v.protype[0], u.protype[0]], [v.protype[1], u.protype[1]], 'b')
                        seen.append((v, u))

        self.camera.snap()

    def animate(self):

        animation = self.camera.animate()
        animation.save('animation.mp4')
        
        
    



    
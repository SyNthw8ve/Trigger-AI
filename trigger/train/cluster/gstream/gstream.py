from typing import Tuple
import numpy as np

from trigger.train.cluster.gstream.graph import Graph
from trigger.train.cluster.gstream.node import Node

from scipy.spatial.distance import cdist


class GStream:

    def __init__(self, vector_size, alpha1, alpha2, beta, error_decrease):

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

    def got_data(self, instances):

        if self.is_first_pass:

            self.first_pass(instances)
            self.is_first_pass = False

        else:
            self.other_pass(instances)

    def first_pass(self, instances):

        for instance in instances:

            bmu1, bmu2 = self.get_best_match(instance)

            self.cluster(instance, bmu1, bmu2)

        self.apply_deltas()

    def other_pass(self, instances):

        for instance in instances:

            bmu1, bmu2 = self.get_best_match(instance)

            if False:  # ∥xi − bmu1∥ > bmu1∥.delta:

                pass

            else:

                self.cluster(instance, bmu1, bmu2)

    def cluster(self, instance, bmu1, bmu2):

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

    def apply_deltas(self):

        for node in self.graph.nodes:

            node.delta = 0

            if len(node.instances) != 0:

                distances = cdist([node.protype], node.instances, "euclidean")[0]
            
                node.delta = max(distances)
        
    def do_fadding(self):
        pass

    def decrease_error(self):
        
        for node in self.graph.nodes:

            node.error *= self.error_decrease

    def update_edges(self):
        pass

    def create_nodes(self) -> Node:
        
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

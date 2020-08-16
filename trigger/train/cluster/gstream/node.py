
from typing import List


class Node:

    def __init__(self, protype, error: float, delta: float) -> None:

        self.protype = protype
        self.error = error
        self.delta = delta
        self.topological_neighbors: List[Node] = []
        self.instances = []

    def add_neighbor(self, neighbor: "Node") -> None:

        self.topological_neighbors.append(neighbor)

    def add_instance(self, instance) -> None:

        self.instances.append(instance)
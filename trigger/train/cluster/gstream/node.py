from typing import List, Dict

class Node:

    def __init__(self, protype, error: float, delta: float, id: int) -> None:

        self.protype = protype
        self.error = error
        self.delta = delta
        self.topological_neighbors: Dict[int, "Node"] = {}
        self.instances = []
        self.id = id

    def add_neighbor(self, neighbor: "Node") -> None:

        self.topological_neighbors[neighbor.id] = neighbor

    def add_instance(self, instance) -> None:

        self.instances.append(instance)

    def remove_neighbor(self, neighbor: "Node") -> None:

        self.topological_neighbors.pop(neighbor.id)
import time
import numpy as np

from typing import List, Dict

class Node:

    def __init__(self, protype, error: float, id: int, error_cycle: int) -> None:

        self.protype = protype
        self.error = error
        self.topological_neighbors: Dict[int, "Node"] = {}
        self.instances: List[Instance] = []
        self.error_cycle = error_cycle
        self.id = id

    def __lt__(self, other: "Node"):

        return self.error > other.error

    def add_neighbor(self, neighbor: "Node") -> None:

        self.topological_neighbors[neighbor.id] = neighbor

    def add_instance(self, instance) -> None:

        self.instances.append(instance)

    def remove_neighbor(self, neighbor: "Node") -> None:

        self.topological_neighbors.pop(neighbor.id)

    def update_error_cycle(self, cycle: int) -> None:

        self.error_cycle = cycle

    def partial_reset(self):

        self.instances = []
        self.topological_neighbors = {}

class Node:

    def __init__(self, protype, error, delta):

        self.protype = protype
        self.error = error
        self.delta = delta
        self.topological_neighbors = []
        self.instances = []

    def add_neighbor(self, neighbor):

        self.topological_neighbors.append(neighbor)

    def add_instance(self, instance):

        self.instances.append(instance)
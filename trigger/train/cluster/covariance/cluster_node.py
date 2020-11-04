import numpy as np

class ClusterNode:

    def __init__(self, id, instance, initial_std) -> None:

        self.id = id
        self.cov_matrix = np.cov([instance])
        self.std = initial_std
        self.mean = instance
        self.instances = [instance]

    def add_instance(self, instance) -> None:

        self.instances.append(instance)
        self.cov_matrix = np.cov(self.instances)
        self.mean = np.mean(self.instances, axis=0)

        std_vector = np.std(self.instances, axis=0)

        self.std = np.linalg.norm(std_vector)
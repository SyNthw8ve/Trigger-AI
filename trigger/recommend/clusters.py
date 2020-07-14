import random
from typing import List, Set, Dict, NamedTuple, Tuple, Optional

import numpy

from trigger.models.user import User
from trigger.models.opening import Opening
from trigger.recommend import smart
from trigger.recommend.opening_transformer import OpeningTransformer, OpeningPoint


class ClusterInstance(NamedTuple):
    opening: Opening
    point: OpeningPoint
    cluster_number: int


class Cluster(NamedTuple):
    number: int
    instances: List[ClusterInstance]


def _same_id(cluster_instance: ClusterInstance, opening: Opening) -> bool:
    return cluster_instance.opening.entityId == opening.entityId


def _get_representative_of_cluster(cluster: Cluster):
    return cluster.instances[0]


class Clusters:
    def __init__(self, opening_transformer: OpeningTransformer) -> None:
        self.opening_transformer = opening_transformer
        self.cluster_dict: Dict[int, Cluster] = {}

    def find(self, opening: Opening) -> Optional[ClusterInstance]:
        for number, cluster in self.cluster_dict.items():
            maybe_found = next(
                (cluster_instance for cluster_instance in cluster.instances if _same_id(cluster_instance, opening)),
                None)
            if maybe_found is not None:
                return maybe_found

        return None

    def remove_opening(self, opening: Opening) -> None:
        cluster_instance = self.find(opening)

        if cluster_instance is not None:
            self._remove_instance(cluster_instance)

    def _remove_instance(self, cluster_instance: ClusterInstance) -> None:
        self.cluster_dict.get(cluster_instance.cluster_number).instances.remove(cluster_instance)

    def opening_change(self, opening: Opening) -> None:
        self.remove_opening(opening)
        self.add_opening(opening)

    def _all_instances(self) -> List[ClusterInstance]:
        return [
            instance
            for cluster in self.cluster_dict.values()
            for instance in cluster.instances
        ]

    def add_opening(self, opening: Opening) -> ClusterInstance:
        point = self.opening_transformer.transform(opening)
        # This is clearly how it's meant to work :D

        min_distance_for_new_cluster = 0.5

        all_instances = self._all_instances()

        distances = [(instance.cluster_number, smart.opening_distance(instance.opening, instance.point, opening, point)) for
                     instance in all_instances]

        ordered_distances = sorted(distances, key=lambda e: e[1])

        should_create_new_cluster = \
            len(ordered_distances) == 0 or ordered_distances[0][1] > min_distance_for_new_cluster

        cluster = 0

        if should_create_new_cluster:
            cluster = len(self.cluster_dict)
            self.cluster_dict[cluster] = Cluster(cluster, [])
        else:
            cluster = ordered_distances[0][0]

        cluster_instance = ClusterInstance(opening, point, cluster)
        self.cluster_dict[cluster].instances.append(cluster_instance)

        return cluster_instance

    def representatives(self) -> List[ClusterInstance]:
        return [_get_representative_of_cluster(cluster) for number, cluster in self.cluster_dict.items()]

    def get_cluster(self, number: int) -> Cluster:
        return self.cluster_dict[number]

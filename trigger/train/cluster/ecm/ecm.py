from typing import Any, Dict, List, Optional, Tuple

import numpy

from trigger.train.cluster.Processor import Processor
from scipy.spatial.distance import cdist, euclidean, cosine

import numpy as np

from enum import Enum

from util.metrics.matches import similarity_metric


class Cluster:
    def __init__(self, tag: str, center: numpy.ndarray, custom: Any, index: int) -> None:
        self.center = center
        self.radius = 0
        self.tag_to_instance: Dict[str, numpy.ndarray] = {
            tag: center
        }
        self.tag_to_custom: Dict[str, numpy.ndarray] = {
            tag: custom
        }
        self.index = index

    def _get_farthest(self, instance: numpy.ndarray, n: int) -> List[Tuple[str, float]]:
        tags_and_distances = [(tag, euclidean(instance, _instance)) for tag, _instance in self.tag_to_instance.items()]
        tags_and_distances.sort(key=lambda td: td[1], reverse=True)
        return tags_and_distances[:n]

    def add_radius(self, tag: str, instance: numpy.ndarray, custom: Any) -> None:
        self.tag_to_instance[tag] = instance
        self.tag_to_custom[tag] = custom

    def _adapt(self, distance: float, instance: numpy.ndarray):
        direction = instance - self.center
        self.radius = distance / 2
        self.center = instance - (direction / np.linalg.norm(direction)) * self.radius

    def add_threshold(self, distance: float, tag: str, instance: numpy.ndarray, custom: Any) -> None:
        self.add_radius(tag, instance, custom)
        self._adapt(distance, instance)

    def update_radius(self, tag: str, instance: numpy.ndarray, custom: Any) -> None:
        self.tag_to_instance[tag] = instance
        self.tag_to_custom[tag] = custom

    def update_threshold(self, distance: float, tag: str, instance: numpy.ndarray, custom: Any) -> None:
        self.update_radius(tag, instance, custom)
        self._adapt(distance, instance)

    def remove(self, tag: str) -> None:
        instance = self.tag_to_instance[tag]

        farthest, second = self._get_farthest(instance, 2)

        del self.tag_to_instance[tag]
        del self.tag_to_custom[tag]

        if farthest is not None and farthest[0] == tag and second is not None:
            self._adapt(second[1], self.tag_to_instance[second[0]])

    def delta_score(self):
        if len(self.tag_to_instance) == 1:
            node_similarities = [1.0]

        else:
            node_similarities = [
                similarity_metric(test_instance, compare_instance)
                for i, test_instance in enumerate(list(self.tag_to_instance.values())[:-1])
                for compare_instance in list(self.tag_to_instance.values())[i + 1:]
            ]

        sim_mean = np.mean(node_similarities)
        sim_std = np.std(node_similarities)

        node_dispersion = sim_std / sim_mean

        return (node_dispersion - 1) / (np.power(5, 0.5) / 5)


class SearchResultType(Enum):
    RADIUS = 1
    THRESHOLD = 2
    OUTSIDE = 3


class ECM(Processor):

    def __init__(self, distance_threshold: float) -> None:
        self.clusters: List[Cluster] = []
        self.distance_threshold = distance_threshold
        self.did_first_add = False
        self.tag_to_cluster: Dict[str, int] = {}
        self.tag_to_instance: Dict[str, tuple] = {}

    @property
    def instances(self) -> List[tuple]:
        return list(self.tag_to_instance.values())

    def update(self, tag: str, instance: numpy.array, custom_data: Any = None) -> None:
        result, (index, distance) = self._search_index_and_distance(instance)
        old_index = self.get_cluster_by_tag(tag)
        cluster = self.clusters[old_index]

        if result == SearchResultType.OUTSIDE:
            cluster.remove(tag)

            cluster = Cluster(tag, instance, custom_data, len(self.clusters))
            self.clusters.append(cluster)
            return

        elif result == SearchResultType.RADIUS:
            if index == old_index:
                cluster.update_radius(tag, instance, custom_data)
            else:
                cluster.remove(tag)
                cluster = self.clusters[index]
                cluster.add_radius(tag, instance, custom_data)

        elif result == SearchResultType.THRESHOLD:
            if index == old_index:
                cluster.update_threshold(distance, tag, instance, custom_data)
            else:
                cluster.remove(tag)
                cluster = self.clusters[index]
                cluster.add_threshold(distance, tag, instance, custom_data)

    def remove(self, tag: str) -> None:
        index = self.get_cluster_by_tag(tag)
        cluster = self.clusters[index]
        del self.tag_to_cluster[tag]
        del self.tag_to_instance[tag]
        cluster.remove(tag)

    def get_cluster_by_tag(self, tag: str) -> Optional[int]:
        return self.tag_to_cluster.get(tag, None)

    def get_instances_and_tags_in_cluster(self, cluster_id: int) -> Tuple[List[numpy.array], List[str]]:
        tag_to_instance = self.clusters[cluster_id].tag_to_instance
        return list(tag_to_instance.values()), list(tag_to_instance.keys())

    def get_all_instances_with_tags(self) -> Tuple[List[numpy.array], List[str]]:
        tags = []
        instances = []
        for cluster in self.clusters:
            c_instances, c_tags = self.get_instances_and_tags_in_cluster(cluster.index)
            tags.extend(c_tags)
            instances.extend(c_instances)
        return instances, tags

    def process(self, tag: str, instance: numpy.array, custom_data: Any = None) -> None:
        if not self.did_first_add:
            cluster = Cluster(tag, instance, custom_data, len(self.clusters))

            self.clusters.append(cluster)

            self.tag_to_cluster[tag] = cluster.index
            self.tag_to_instance[tag] = tuple(instance)

            self.did_first_add = True
            return

        search_result, (index, distance) = self._search_index_and_distance(instance)

        if search_result == SearchResultType.RADIUS:
            cluster = self.clusters[index]
            cluster.add_radius(tag, instance, custom_data)

            self.tag_to_cluster[tag] = index
            self.tag_to_instance[tag] = tuple(instance)

        elif search_result == SearchResultType.THRESHOLD:
            cluster = self.clusters[index]
            cluster.add_threshold(distance, tag, instance, custom_data)

            self.tag_to_cluster[tag] = index
            self.tag_to_instance[tag] = tuple(instance)

        elif search_result == SearchResultType.OUTSIDE:
            cluster = Cluster(tag, instance, custom_data, len(self.clusters))

            self.clusters.append(cluster)

            self.tag_to_cluster[tag] = cluster.index
            self.tag_to_instance[tag] = tuple(instance)

    def _search_index_and_distance(self, instance: Any) -> \
            Tuple[SearchResultType, Tuple[Optional[int], Optional[int]]]:

        centers = [cluster.center for cluster in self.clusters]

        distances = cdist(
            np.array([instance]),
            np.array(centers),
            'euclidean'
        )[0]

        radiuses = [cluster.radius for cluster in self.clusters]

        diffs = distances - radiuses

        possible_indexes = np.where(diffs <= 0)[0]

        possible = distances[possible_indexes]

        min_index = None if possible.size == 0 else possible_indexes[possible.argmin()]

        if min_index is not None:
            return SearchResultType.RADIUS, (min_index, distances[min_index])

        distances_plus_radiuses = np.add(distances, radiuses)
        lowest_distance_and_radius_index = np.argmin(distances_plus_radiuses)
        lowest_distance_and_radius = distances_plus_radiuses[lowest_distance_and_radius_index]

        if lowest_distance_and_radius > 2 * self.distance_threshold:
            return SearchResultType.OUTSIDE, (lowest_distance_and_radius_index, lowest_distance_and_radius)

        else:
            return SearchResultType.THRESHOLD, (lowest_distance_and_radius_index, lowest_distance_and_radius)

    def describe(self) -> Dict[str, Any]:
        """
        This describes this clustering algorithm's parameters
        """

        return {
            "name": "ECM",
            "parameters": {
                "distance threshold": self.distance_threshold
            }
        }

    def safe_file_name(self) -> str:
        return f"ECM = distance_threshold={self.distance_threshold}"

    def predict(self, instance: Any) -> Optional[int]:
        # FIXME: What should predict do in this case?
        if not self.did_first_add:
            return None

        search_result, (index, distance) = self._search_index_and_distance(instance)

        # FIXME: What should predict do in this case?
        if search_result == SearchResultType.OUTSIDE:
            return index

        elif search_result == SearchResultType.THRESHOLD:
            return index

        elif search_result == SearchResultType.RADIUS:
            return index

    def get_custom_data_by_tag(self, tag: str) -> Optional[Any]:
        # TODO: We assume the tag exists?
        index = self.get_cluster_by_tag(tag)
        return self.clusters[index].tag_to_custom.get(tag, None)

    def get_instance_by_tag(self, tag: str) -> Optional[numpy.ndarray]:
        return self.tag_to_instance.get(tag, None)

    def compute_cluster_score(self):
        node_scores = []

        for cluster in self.clusters:
            node_dispersion_delta = cluster.delta_score()
            node_delta = np.power(node_dispersion_delta, 2)

            node_score = np.exp(-(node_delta)) * np.log(len(cluster.tag_to_instance))
            node_scores.append(node_score)

        return np.sum(node_scores)

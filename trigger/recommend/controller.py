from typing import List, Optional

from trigger.models.user import User
from trigger.models.Match import Match
from trigger.recommend import smart

from trigger.recommend.clusters import Clusters
from trigger.recommend.user_transformer import UserTransformer
from trigger.recommend.opening_transformer import OpeningTransformer


class Controller:
    def __init__(self, cluster: Clusters, user_transformer: UserTransformer, ) -> None:
        self.clusters = cluster
        self.user_transformer = user_transformer

    def user_matches(self, user: User, highest_distance: float = 0.5) -> List[Match]:
        # very complex stuff

        good_clusters = []
        representatives = self.clusters.representatives()
        user_point = self.user_transformer.transform(user)

        for cluster_instance in representatives:

            distance = smart.user_distance(user, user_point, cluster_instance.opening, cluster_instance.point)

            if distance > highest_distance:
                continue

            good_clusters.append(cluster_instance.cluster_number)

        matches = []

        for cluster_number in good_clusters:
            cluster_instances = self.clusters.get_cluster(cluster_number).instances
            for cluster_instance in cluster_instances:

                distance = smart.user_distance(user, user_point, cluster_instance.opening, cluster_instance.point)
                if distance > highest_distance:
                    continue

                matches.append(Match(user, distance, cluster_instance.opening))

        return matches

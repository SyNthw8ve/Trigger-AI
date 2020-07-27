from typing import List
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine

from trigger.models.match import Match

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance

import numpy as np

class KCluster:

    def __init__(self, nClusters: int = 2, instances: List[OpeningInstance] = []):

        self.cluster = KMeans(n_clusters=nClusters, random_state=314)
        self.instances = instances

    def train(self):

        X = np.array([opening.embedding for opening in self.instances])

        self.cluster.fit(X)

        for label_, instance in zip(self.cluster.labels_, self.instances):

            instance.cluster_index = label_

    def _predict(self, instance: UserInstance) -> int:

        clusterIndex = self.cluster.predict([instance.embedding])

        return clusterIndex[0]

    def _computeScore(self, userInstance: UserInstance, openingInstance: OpeningInstance) -> float:

        return 1 - cosine(userInstance.embedding, openingInstance.embedding)

    def getOpenings(self, instance: UserInstance) -> List[Match]:

        clusterIndex = self._predict(instance)

        openingsOfInterest = [openingInstance for openingInstance in self.instances if openingInstance.cluster_index == clusterIndex]

        return [Match(instance.user, self._computeScore(instance, openingInstance), openingInstance.opening) for openingInstance in openingsOfInterest]

import logging
import os
from typing import List

from tests.ecm_tests import test_ecm
from trigger.models.match import Match
from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.matches import computeScore
from util.readers.setup_reader import DataInitializer
from tests.gng_test import test_gng
from tests.ecm_tests import test_ecm

from trigger.train.cluster.gturbo.gturbo import GTurbo

users_path = './examples/openings_users_softskills_confirmed/users'
openings_path = './examples/openings_users_softskills_confirmed/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

def getOpenings(id: int, user: UserInstance, openings: List[OpeningInstance], threshold: float) -> List[Match]:

    openingsOfInterest = [
        openingInstance for openingInstance in openings if openingInstance.cluster_index == id]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openingsOfInterest
            if computeScore(user, openingInstance) >= threshold]


if __name__ == "__main__":

    test_gng()

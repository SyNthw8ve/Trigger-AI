import os
import pprint
import logging
import json

from typing import List, Tuple

from trigger.models.Match import Match

from trigger.models.opening import Opening
from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.user import User

from trigger.recommend import smart
from trigger.recommend.controller import Controller
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningTransformer
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

from trigger.recommend.user_transformer import UserTransformer

from util.readers.reader import DataReaderOpenings, DataReaderUsers
from util.json_util.json_converter import user_to_json, opening_to_json
from util.metrics.metrics import eval_cluster, computeScore

from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.gstream.gstream import GNG
from trigger.train.cluster.birch.birch import Birch

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'

def getOpenings(id: int, user: UserInstance, openings: List[OpeningInstance], threshold: float) -> List[Match]:

    openingsOfInterest = [
        openingInstance for openingInstance in openings if openingInstance.cluster_index == id]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openingsOfInterest
            if computeScore(user, openingInstance) >= threshold]

if __name__ == "__main__":

    users_path = 'users_instances'
    openings_path = 'openings_instances'

    users_instances = []
    users_instances_path = os.path.join(instances_path, users_path)

    openings_instances = []
    openings_instances_path = os.path.join(
        instances_path, openings_path)

    if os.path.exists(users_instances_path):

        logging.info("Users instances file found. Loading...")
        users_instances = UserInstance.load_instances(users_instances_path)

    else:

        embedder = SentenceEmbedder()

        logging.info("Users instances file not found. Reading Users...")
        users_files = [os.path.join(users_path, f) for f in os.listdir(
            users_path) if os.path.isfile(os.path.join(users_path, f))]

        users = []
        for user_file in users_files:

            users += DataReaderUsers.populate(filename=user_file)

        logging.info("Creating instances...")
        users_instances = [UserInstance(user, embedder) for user in users]

        logging.info(f"Saving instances to {users_instances_path}...")
        UserInstance.save_instances(users_instances_path, users_instances)

        logging.info("Saved")

    logging.info("Users instances complete.")

    if os.path.exists(openings_instances_path):

        logging.info("Openings instances file found. Loading...")
        openings_instances = OpeningInstance.load_instances(
            openings_instances_path)

    else:

        embedder = SentenceEmbedder()

        logging.info("Openings instances file not found. Reading Openings...")
        openings_files = [os.path.join(openings_path, f) for f in os.listdir(
            openings_path) if os.path.isfile(os.path.join(openings_path, f))]

        openings = []
        for opening_file in openings_files:

            openings += DataReaderOpenings.populate(filename=opening_file)

        logging.info("Creating instances...")
        openings_instances = [OpeningInstance(
            opening, embedder) for opening in openings]

        logging.info(f"Saving instances to {openings_instances_path}...")
        OpeningInstance.save_instances(
            openings_instances_path, openings_instances)

        logging.info("Saved")

    logging.info("Openings instances complete.")

    logging.info("GNG Testing")



    """ gng = GNG(epsilon_b=0.001,
              epsilon_n=0,
              lam=5,
              beta=0.9995,
              alpha=0.95,
              max_age=10,
              off_max_age=10,
              lambda_2=0.2,
              nodes_per_cycle=1,
              dimensions=1024,
              index_type='L2')

    for opening_instance in openings_instances:

        gng.online_fase(opening_instance.embedding)
        opening_instance.cluster_index = gng.get_cluster(
            opening_instance.embedding)

    results = {'scores': str(eval_cluster(gng)), 'user_matches': []}
    user_matches = []

    for user_instance in users_instances:

        cluster_id = gng.predict(user_instance.embedding)
        matches = getOpenings(cluster_id, user_instance,
                              openings_instances, 0.5)

        user_result = user_to_json(user_instance.user, matches)
        user_matches.append(user_result)

    results['user_matches'] = user_matches

    with open('quality_l2_avg_norm.json', 'w') as f:

        json.dump(results, f) """

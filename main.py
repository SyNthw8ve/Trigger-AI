import os
import pprint
import logging
import json

from typing import List, Tuple
from scipy.spatial.distance import cosine

from sklearn.metrics import silhouette_score, calinski_harabasz_score

from trigger.models.match import Match

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
from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.gstream.gstream import GNG
from trigger.train.cluster.birch.birch import Birch

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'

def computeScore(userInstance: UserInstance, openingInstance: OpeningInstance) -> float:

    return 1 - cosine(userInstance.embedding, openingInstance.embedding)

def getOpenings(id: int, user: UserInstance, openings: List[OpeningInstance], threshold: float) -> List[Match]:

    openingsOfInterest = [
        openingInstance for openingInstance in openings if openingInstance.cluster_index == id]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openingsOfInterest
            if computeScore(user, openingInstance) >= threshold]

def eval_cluster(gng: GNG) -> Tuple[float, float]:

    X = gng.instances
    labels = []

    for x in X:

        labels.append(gng.get_cluster(x))

    return (silhouette_score(X, labels), calinski_harabasz_score(X, labels))

def eval_birch(birch: Birch) -> Tuple[float, float]:

    X = birch.instances
    labels = []

    for x in X:

        labels.append(birch.index_of_cluster_containing(x))

    return (silhouette_score(X, labels), calinski_harabasz_score(X, labels))


if __name__ == "__main__":

    users_instances = []
    users_instances_path = os.path.join(instances_path, 'users_instances')

    openings_instances = []
    openings_instances_path = os.path.join(
        instances_path, 'openings_instances')

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

    gng = GNG(epsilon_b=0.001,
              epsilon_n=0,
              lam=5,
              beta=0.9995,
              alpha=0.95,
              max_age=10,
              off_max_age=10,
              lambda_2=0.2,
              nodes_per_cycle=3,
              dimensions=1024)

    for opening_instance in openings_instances:

        gng.online_fase(opening_instance.embedding)
        opening_instance.cluster_index = gng.get_cluster(
            opening_instance.embedding)

    print(eval_cluster(gng))
    
    for user_instance in users_instances:

        cluster_id = gng.predict(user_instance.embedding)

        matches = getOpenings(cluster_id, user_instance, openings_instances, 0.5)
        pprint.pprint(matches)

    logging.info("Birch Testing")

    birch = Birch(threshold=7, branching_factor=50)

    for opening_instance in openings_instances:

        birch.add(opening_instance.embedding)
        opening_instance.cluster_index = birch.index_of_cluster_containing(opening_instance.embedding)

    print(eval_birch(birch))

    for user_instance in users_instances:

        cluster_id = birch.index_of_cluster_containing(user_instance.embedding)

        matches = getOpenings(cluster_id, user_instance, openings_instances, 0.5)
        
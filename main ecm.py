import os
import pprint
import logging
import json

from typing import List, Tuple
from scipy.spatial.distance import cosine

from sklearn.metrics import silhouette_score, calinski_harabasz_score

from trigger.models.match import Match

from trigger.models.opening import Opening
from trigger.models.user import User

from util.readers.reader import DataReaderOpenings, DataReaderUsers
from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.ecm.ecm import ECM
from trigger.train.cluster.birch.birch import Birch

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'

Clusterer = ECM


def computeScore(userInstance: UserInstance, openingInstance: OpeningInstance) -> float:

    return 1 - cosine(userInstance.embedding, openingInstance.embedding)


def getOpenings(id: int, user: UserInstance, openings: List[OpeningInstance], threshold: float) -> List[Match]:

    openingsOfInterest = [
        openingInstance for openingInstance in openings if openingInstance.cluster_index == id]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openingsOfInterest
            if computeScore(user, openingInstance) >= threshold]


def eval_cluster(gng: Clusterer) -> Tuple[float, float]:

    X = gng.instances
    labels = []

    for i, x in enumerate(X):
        label = gng.get_cluster_by_tag(str(i))
        labels.append(label)

    return (silhouette_score(X, labels), calinski_harabasz_score(X, labels))


def eval_birch(birch: Birch) -> Tuple[float, float]:

    X = birch.instances
    labels = []

    for x in X:

        labels.append(birch.index_of_cluster_containing(x))

    return (silhouette_score(X, labels), calinski_harabasz_score(X, labels))


def quality_metric(user: User, opening: OpeningInstance):

    u_h = set(user.hardSkills)
    u_s = set(user.softSkills)

    o_h = set(opening.hardSkills)
    o_s = set(opening.softSkills)

    if len(o_h) == 0:
        HS_s = 0

    else:
        HS_s = len(o_h.intersection(u_h))/len(o_h)

    if len(o_s) == 0:
        SS_s = 0

    else:
        SS_s = len(o_s.intersection(u_s))/len(o_s)

    Mq = 0.6*HS_s + 0.4*SS_s

    return Mq


def opening_to_json(opening: Opening):

    return {'hard_skills': opening.hardSkills, 'soft_skills': opening.softSkills}


def user_to_json(user: User, matches: List[Match]):

    user_json = {'name': user.name, 'hard_skills': user.hardSkills,
                 'soft_skills': user.softSkills, 'matches': []}

    user_matches = []

    for match in matches:

        quality = quality_metric(user, match.opening)
        real_score = 0.5*(match.score + quality)

        user_match = {'score': str(match.score), 'quality':  str(
            quality), 'real_score': str(real_score), 'opening': opening_to_json(match.opening)}

        user_matches.append(user_match)

    user_matches = sorted(
        user_matches, key=lambda match: match['score'], reverse=True)

    user_json['matches'] = user_matches

    return user_json


if __name__ == "__main__":

    users_instances = []
    users_instances_path = os.path.join(
        instances_path, 'no_ss_users_instances')

    openings_instances = []
    openings_instances_path = os.path.join(
        instances_path, 'no_ss_openings_instances')

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

    params_list = [
        (0.001,),
        (0.005,),
        (0.010,),
        (0.020,),
        (0.050,),
        (0.1,),
        (0.2,),
        (0.5,),
        (1,),
        (1.2,),
        (1.5,),
        (1.5,),
    ]

    for params in params_list:

        print(params)

        gng = ECM(*params)

        for i, opening_instance in enumerate(openings_instances):

            gng.process(str(i), opening_instance.embedding)
            opening_instance.cluster_index = gng.get_cluster_by_tag(str(i))

        print(len(gng.clusters))

        results = {'algorithm': gng.describe(), 'scores': str(
            eval_cluster(gng)), 'user_matches': []}
        user_matches = []

        print("Users")

        for user_instance in users_instances:
            cluster_id = gng.predict(user_instance.embedding)

            matches = getOpenings(cluster_id, user_instance,
                                  openings_instances, 0.5)

            user_result = user_to_json(user_instance.user, matches)
            user_matches.append(user_result)

        results['user_matches'] = user_matches

        with open(os.path.join(results_path, f'no_softskills/{gng.safe_file_name()}.json'), 'w') as f:

            json.dump(results, f)

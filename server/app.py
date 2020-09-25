from server.database.opening_model import OpeningModel
from trigger.models.server_match import ServerMatch
from flask import Flask
from rq import Queue
from scipy.spatial.distance import cosine
from server.database.user_model import UserModel
from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.cluster.gstream.gstream import GNG
import os
from typing import Any, List
import pymongo
import redis
import time

import json
import sys
from pathlib import Path

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance

sys.path.append(str(Path('.').absolute().parent))
sys.path.append(str(Path('..').absolute().parent))

app = Flask(__name__)

clusterer = GNG(epsilon_b=0.001,
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

sentence_embedder = SentenceEmbedder()

score_to_be_match = 0.5

config_path = "server/config.json"

with open(config_path) as f:
    config = json.load(f)

# FIXME: when using mongodb+srv:// URIs for host it needs to have dnspython
client = pymongo.MongoClient(config["database_host"])
database = client[config["database"]]

# TODO: Add quality score


def calculate_score(user_instance: Any, opening_instance: Any) -> float:
    return 1 - cosine(user_instance, opening_instance)

# TODO: Add quality score


def calculate_matches(user_id: str, user_instance: UserInstance) -> List[ServerMatch]:
    would_be_cluster_id = clusterer.predict(user_instance.embedding)

    instances, tags = clusterer.get_instances_and_tags_in_cluster(would_be_cluster_id)

    matches = [
        ServerMatch(
            user_id,
            calculate_score(user_instance.embedding, instance),
            tag
        )
        for instance, tag in zip(instances, tags)
    ]

    good_matches = [
        match
        for match in matches
        if match.score > score_to_be_match
    ]

    return good_matches


@app.route('/user_match/<user_id>', methods=['POST'])
def compute_user_matches(user_id: str):
    user = UserModel.get_user_data(user_id, database)

    # TODO: cache user instance?
    matches = calculate_matches(user_id, UserInstance(user, sentence_embedder))

    UserModel.insert_user_matches(user_id, database, matches)
    return str(matches)


@app.route('/user_match/<user_id>', methods=['PUT'])
def update_user_matches(user_id: str):
    user = UserModel.get_user_data(user_id, database)

    # TODO: cache user instance?
    matches = calculate_matches(user_id, UserInstance(user, sentence_embedder))

    UserModel.update_user_matches(user_id, database, matches)
    return str(matches)


@app.route('/opening/<opening_id>', methods=['POST'])
def insert_opening_to_cluster(opening_id: str):
    opening = OpeningModel.get_opening(opening_id, database)
    # FIXME: always online here?
    clusterer.online_fase(
        opening_id, OpeningInstance(opening, sentence_embedder).embedding)
    return "Ok"


@app.route('/opening/<opening_id>', methods=['PUT'])
def update_opening(opening_id: str):
    opening = OpeningModel.get_opening(opening_id, database)
    clusterer.update(opening_id, OpeningInstance(opening, sentence_embedder).embedding)
    return "Ok"


@app.route('/opening/<opening_id>', methods=['DELETE'])
def remove_opening_from_cluster(opening_id: str):
    clusterer.remove(opening_id)
    return "Ok"

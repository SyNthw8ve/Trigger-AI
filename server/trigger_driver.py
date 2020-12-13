from server.trigger_BE import notify_BE
from server.database.server_score import ServerScore
from typing import Dict, List

import numpy
import pymongo

from server.database.apply_scores_model import ApplyScoresModel
from server.database.server_matches_model import ServerMatchesModel
from server.database.opening_model import OpeningModel
from server.database.user_model import UserModel
from trigger.models.opening import Opening
from trigger.models.user import User
from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.input_transformer import SentenceEmbedder

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.matches import similarity_metric, quality_metric, real_metric

import logging


def calculate_scores(user: User, embedding1: numpy.ndarray, opening: Opening, embedding2: numpy.ndarray):
    similarity = similarity_metric(embedding1, embedding2)
    quality = quality_metric(user, opening)
    # FIXME: Don't hardcode
    final = real_metric(similarity_weight=.5, similarity_score=similarity, quality_weight=.5, quality_score=quality)
    return { 
        "similarity_score": similarity, 
        "quality_score": quality, 
        "final_score": final,  
    }

logger = logging.getLogger('trigger_driver')
logger.setLevel(logging.INFO)

class TriggerDriver:

    def __init__(self, sentence_embedder: SentenceEmbedder,
                 config: Dict,
                 processor: Processor):
        self.processor = processor
        self.config = config
        self.sentence_embedder = sentence_embedder

    def connect(self) -> pymongo.MongoClient:
        # FIXME: when using mongodb+srv:// URIs for host it needs to have dnspython
        client = pymongo.MongoClient(self.config["database_host"])
        return client

    def init_processor(self) -> "TriggerDriver":
        logger.info("Initializing processor")

        with self.connect() as client:
            database = client[self.config["database"]]

            for opening in OpeningModel.get_all_openings(database):
                logger.info("Inserting into cluster %s", opening)
                opening_instance = OpeningInstance(opening, self.sentence_embedder)
                self.processor.process(opening.entityId, opening_instance.embedding, opening_instance.opening)

        return self

    def calculate_matches_of_user(self, user_id: str, user_instance: UserInstance) -> List[ServerScore]:

        would_be_cluster_id = self.processor.predict(user_instance.embedding)
        instances, tags = self.processor.get_instances_and_tags_in_cluster(would_be_cluster_id)
        openings = [self.processor.get_custom_data_by_tag(tag) for tag in tags]

        scores = [
            ServerScore(
                user_id=user_id,
                opening_id=opening_id,
                **calculate_scores(user_instance.user, user_instance.embedding, opening, instance),
            )
            for opening, instance, opening_id in zip(openings, instances, tags)
        ]

        print(scores)

        matches = [
            score
            for score in scores
            # FIXME: Don't hardcode
            if score.final_score >= 0.0
        ]

        print(matches)

        return matches

    def compute_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)
            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            logger.info("Did matches for user with id %s: %s", user_id, matches)

            ids = ServerMatchesModel.insert_server_matches(database, matches)
            # FIXME: maybe send the ids?

            notify_BE(f"user_created/{user_id}", self.config["backend_flask_endpoint"])

    def compute_user_score(self, user_id: str, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]
            user = UserModel.get_user_data(user_id, database)
            user_instance = UserInstance(user, self.sentence_embedder)

            opening = self.processor.get_custom_data_by_tag(opening_id)
            embedding = self.processor.get_instance_by_tag(opening_id)

            score = ServerScore(
                user_id=user_id,
                opening_id=opening_id,
                **calculate_scores(user, user_instance.embedding, opening, embedding)
            )

            print(score)
            print(score.user_id)
            print(score.opening_id)
            
            score_id = ApplyScoresModel.insert_apply_score(database, score)

            if score_id is None:
                #FIXME: Exception so RQ can retry?
                # raise Exception
                return
            
            notify_BE(f"user_score/{score_id}", self.config["backend_flask_endpoint"])
            
            logger.info("Score between user with id %s: and opening with id %s has been calculated", user_id, opening_id)

    def update_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)
            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            # FIXME: The servermatches disappear when the user/opening changes?
            ServerMatchesModel.delete_user_server_matches(database, user_id)
            ServerMatchesModel.insert_server_matches(database, matches)
            
            notify_BE(f"user_updated/{user_id}", self.config["backend_flask_endpoint"])
            
            logger.info("Update matches for user with id %s: %s", user_id, matches)

    def insert_opening_to_cluster(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            opening = OpeningModel.get_opening(opening_id, database)
            opening_instance = OpeningInstance(opening, self.sentence_embedder)

            self.processor.process(opening_id, opening_instance.embedding, opening_instance.opening)

            logger.info("Added opening with id %s", opening_id)

    def update_opening(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]
            opening = OpeningModel.get_opening(opening_id, database)
            opening_instance = OpeningInstance(opening, self.sentence_embedder)

            self.processor.update(opening_id, opening_instance.embedding)

    def remove_opening_from_cluster(self, opening_id: str):
        self.processor.remove(opening_id)

    def sweep(self):
        # TODO How to do this? Update everyone? Have another endpoint to register an update?

        with self.connect() as client:
            database = client[self.config["database"]]
            users = UserModel.get_all_users_data(database)

            for user in users:
                pass

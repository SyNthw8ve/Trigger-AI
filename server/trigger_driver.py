from typing import Dict, List

import numpy
import pymongo

from server.database.opening_model import OpeningModel
from server.database.user_model import UserModel
from trigger.models.opening import Opening
from trigger.models.server_match import ServerMatch
from trigger.models.user import User
from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.input_transformer import SentenceEmbedder

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.matches import similarity_metric, quality_metric, real_metric


def calculate_score(user: User, embedding1: numpy.ndarray, opening: Opening, embedding2: numpy.ndarray):
    similarity = similarity_metric(embedding1, embedding2)
    quality = quality_metric(user, opening)
    # FIXME: Don't hardcode
    return real_metric(similarity_weight=.5, similarity_score=similarity, quality_weight=.5, quality_score=quality)


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
        print("Initializing processor")

        with self.connect() as client:
            database = client[self.config["database"]]

            for opening in OpeningModel.get_all_openings(database):
                print("Inserting into cluster", opening)
                opening_instance = OpeningInstance(opening, self.sentence_embedder)
                self.processor.process(opening.entityId, opening_instance.embedding, opening_instance.opening)

        return self

    def calculate_matches_of_user(self, user_id: str, user_instance: UserInstance) -> List[ServerMatch]:

        would_be_cluster_id = self.processor.predict(user_instance.embedding)
        instances, tags = self.processor.get_instances_and_tags_in_cluster(would_be_cluster_id)
        openings = [self.processor.get_custom_data_by_tag(tag) for tag in tags]

        matches = [
            ServerMatch(
                user_id,
                calculate_score(user_instance.user, user_instance.embedding, opening, instance),
                opening_id
            )
            for opening, instance, opening_id in zip(openings, instances, tags)
        ]

        good_matches = [
            match
            for match in matches
            # FIXME: Don't hardcode
            if match.score > 0.5
        ]

        return good_matches

    def compute_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)

            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            print(f"Did matches for user: {user_id}: {matches}")

            UserModel.insert_user_matches(user_id, database, matches, self.config["backend_matches_endpoint"])

    def compute_user_score(self, user_id: str, opening_id: str) -> ServerMatch:
        with self.connect() as client:
            database = client[self.config["database"]]
            user = UserModel.get_user_data(user_id, database)
            user_instance = UserInstance(user, self.sentence_embedder)

            opening = self.processor.get_custom_data_by_tag(opening_id)
            embedding = self.processor.get_instance_by_tag(opening_id)

            return ServerMatch(user_id, calculate_score(user, user_instance.embedding, opening, embedding), opening_id)

    def update_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)

            # TODO: cache user instance?
            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            UserModel.update_user_matches(user_id, database, matches, self.config["backend_matches_endpoint"])
            print(f"Updated matches: {matches}")

    def insert_opening_to_cluster(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            opening = OpeningModel.get_opening(opening_id, database)

            opening_instance = OpeningInstance(opening, self.sentence_embedder)

            self.processor.process(opening_id, opening_instance.embedding, opening_instance.opening)

            print(f"Opening {opening_id} added!")

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

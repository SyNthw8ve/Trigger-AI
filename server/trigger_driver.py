from typing import Dict, List, Any

import pymongo

from server.database.opening_model import OpeningModel
from server.database.user_model import UserModel
from server.score_calculator import ScoreCalculator
from trigger.models.server_match import ServerMatch
from trigger.train.cluster.gstream.gstream import GNG
from trigger.train.transformers.input_transformer import SentenceEmbedder

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance

Clusterer = GNG

class TriggerDriver:

    def __init__(self, sentence_embedder: SentenceEmbedder,
                 config: Dict,
                 score_to_be_match: float,
                 score_calculator: ScoreCalculator,
                 clusterer: Clusterer):
        self.score_calculator = score_calculator
        self.clusterer = clusterer
        # FIXME: Should this be in the clusterer?
        self.tag_to_opening_instance: Dict[str, OpeningInstance] = {}
        self.score_to_be_match = score_to_be_match
        self.config = config
        self.sentence_embedder = sentence_embedder

    def connect(self) -> pymongo.MongoClient:
        # FIXME: when using mongodb+srv:// URIs for host it needs to have dnspython
        client = pymongo.MongoClient(self.config["database_host"])
        return client

    def init_clusterer(self) -> "TriggerDriver":
        print("Initializing clusterer")

        with self.connect() as client:
            database = client[self.config["database"]]

            for opening in OpeningModel.get_all_openings(database):
                print("Inserting into cluster", opening)
                opening_instance =  OpeningInstance(opening, self.sentence_embedder)
                self.clusterer.online_fase(opening.entityId, opening_instance.embedding)
                self.tag_to_opening_instance[opening.entityId] = opening_instance

        return self

    def calculate_matches_of_user(self, user_id: str, user_instance: UserInstance) -> List[ServerMatch]:

        would_be_cluster_id = self.clusterer.predict(user_instance.embedding)
        _, tags = self.clusterer.get_instances_and_tags_in_cluster(would_be_cluster_id)
        opening_instances = [self.tag_to_opening_instance[opening_id] for opening_id in tags]

        matches = [
            ServerMatch(
                user_id,
                self.score_calculator.calculate(user_instance, opening_instance),
                opening_id
            )
            for opening_instance, opening_id in zip(opening_instances, tags)
        ]

        good_matches = [
            match
            for match in matches
            if match.score > self.score_to_be_match
        ]

        return good_matches


    def compute_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)

            print("Passed")

            # TODO: cache user instance?
            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            print("Matches")

            print(self.clusterer.get_all_instances_with_tags())
            print()
            print(user)
            print()
            print(f"Did matches for user: {user_id}: {matches}")

            UserModel.insert_user_matches(user_id, database, matches, self.config["backend_matches_endpoint"])


    def compute_user_score(self, user_id: str, opening_id: str) -> ServerMatch:
        with self.connect() as client:
            print("connected")
            database = client[self.config["database"]]
            user = UserModel.get_user_data(user_id, database)
            print("get_user_data")
            # TODO: cache user instance?
            user_instance = UserInstance(user, self.sentence_embedder)

            opening_instance = self.tag_to_opening_instance[opening_id]
            print("ServerMatch")

            return ServerMatch(user_id, self.score_calculator.calculate(user_instance, opening_instance),opening_id)


    def update_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)

            # TODO: cache user instance?
            matches = self.calculate_matches_of_user(user_id, UserInstance(user, self.sentence_embedder))

            UserModel.update_user_matches(user_id, database, matches, self.config["backend_matches_endpoint"])

            print(self.clusterer.get_all_instances_with_tags())
            print()
            print(user)
            print()
            print(f"Updated matches: {matches}")


    def insert_opening_to_cluster(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            opening = OpeningModel.get_opening(opening_id, database)

            opening_instance = OpeningInstance(opening, self.sentence_embedder)

            # FIXME: always online here?
            self.clusterer.online_fase(opening_id, opening_instance.embedding)
            self.tag_to_opening_instance[opening_id] = opening_instance

            print(f"Opening {opening_id} added!")
            print(self.clusterer.get_all_instances_with_tags())



    def update_opening(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]
            opening = OpeningModel.get_opening(opening_id, database)
            opening_instance = OpeningInstance(opening, self.sentence_embedder)

            self.clusterer.update(opening_id, opening_instance.embedding)
            self.tag_to_opening_instance[opening_id] = opening_instance


    def remove_opening_from_cluster(self, opening_id: str):
        self.clusterer.remove(opening_id)
        self.tag_to_opening_instance.pop(opening_id)


    def sweep(self):
        with self.connect() as client:
            database = client[self.config["database"]]
            users = UserModel.get_all_users_data(database)

            for user in users:
                # TODO does this make sense?
                self.update_user_matches(user.id)
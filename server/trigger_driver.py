from trigger.scoring import TriggerScoring
from trigger.trigger_interface import TriggerInterface
from server.trigger_BE import notify_BE
from server.database.server_score import ServerScore
from typing import Dict, List, Sequence, cast
from typing_extensions import Final

import pymongo

from server.database.apply_scores_model import ApplyScoresModel
from server.database.server_matches_model import ServerMatchesModel
from server.database.opening_model import OpeningModel
from server.database.user_model import UserModel
from trigger.models.opening import Opening
from trigger.models.user import User

import logging

logger = logging.getLogger('trigger_driver')
logger.setLevel(logging.INFO)

class TriggerDriver:

    def __init__(
        self,
        interface: TriggerInterface,
        config: Dict
    ):
        self.interface: Final[TriggerInterface] = interface
        self.config = config

    def connect(self) -> pymongo.MongoClient:
        # FIXME: when using mongodb+srv:// URIs for host it needs to have dnspython
        client = pymongo.MongoClient(self.config["database_host"])
        return client

    def init_processor(self) -> "TriggerDriver":
        logger.info("Initializing processor")

        with self.connect() as client:
            database = client[self.config["database"]]
            for opening in OpeningModel.get_all_openings(database):
                instance = self.interface.try_create_instance_from_value("opening", opening)
                if instance is not None:
                    self.interface.add(opening.entityId, instance)
                else:
                    logger.error("No transformer for key='opening'")


        return self

    def calculate_matches_of_user(self, user_id: str, user: User) -> Sequence[ServerScore]:

        instance = self.interface.try_create_instance_from_value("user", user)
        if instance is None:
            logger.error("No transformer for key='user'")
            return []

        matches = cast(Sequence[TriggerScoring], self.interface.get_matches_for(instance))

        score_objects = [
            ServerScore(
                user_id=user_id,
                opening_id=match.scored_tag,
                similarity_score=match.similarity_score,
                quality_score=match.quality_score,
                final_score=match.score,
            )
            for match in matches
        ]

        return score_objects

    def compute_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)
            matches = self.calculate_matches_of_user(user_id, user)

            logger.info("Did matches for user with id %s: %s", user_id, matches)

            ids = ServerMatchesModel.insert_server_matches(database, matches)
            # FIXME: maybe send the ids?

        print("notifying back end", f"user_created/{user_id}")
        notify_BE(f"user_created/{user_id}", self.config["backend_endpoint"])

    def compute_user_score(self, user_id: str, opening_id: str):

        with self.connect() as client:
            database = client[self.config["database"]]
            user = UserModel.get_user_data(user_id, database)

            instances = self.interface.get_instances_by_tag([opening_id])

            if len(instances) == 0:
                logger.warn("no opening with id %s", opening_id)
                return

            opening_instance = instances[0]

            user_instance = self.interface.try_create_instance_from_value("user", user)

            if user_instance is None:
                logger.error("No transformer for key='user'")
                return

            scoring = cast(TriggerScoring, self.interface.calculate_scoring_between_instances(user_instance, opening_instance))
            scoring.scored_tag = opening_id

            score = ServerScore(
                user_id=user_id,
                opening_id=scoring.scored_tag,
                similarity_score=scoring.similarity_score,
                quality_score=scoring.quality_score,
                final_score=scoring.score,
            )

            score_id = ApplyScoresModel.insert_apply_score(database, score)

            if score_id is None:
                #FIXME: Exception so RQ can retry?
                # raise Exception
                return
            
        logger.info("Score between user with id %s: and opening with id %s has been calculated", user_id, opening_id)
        notify_BE(f"user_score/{score_id}", self.config["backend_endpoint"])


    def update_user_matches(self, user_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            user = UserModel.get_user_data(user_id, database)
            matches = self.calculate_matches_of_user(user_id, user)

            # FIXME: The servermatches disappear when the user/opening changes?
            ServerMatchesModel.delete_user_server_matches(database, user_id)
            ServerMatchesModel.insert_server_matches(database, matches)
            
        logger.info("Update matches for user with id %s: %s", user_id, matches)
        notify_BE(f"user_updated/{user_id}", self.config["backend_endpoint"])
            

    def insert_opening_to_cluster(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]

            opening = OpeningModel.get_opening(opening_id, database)

            opening_instance = self.interface.try_create_instance_from_value("opening", opening)
            
            if opening_instance is None:
                logger.error("No transformer for key='opening'")
                return

            # if len(self.interface.get_instances_by_tag([opening_id])) != 0:
            #     logger.error("Trying to add an opening with id %s, but it already exists")
            #     return

        self.interface.add(opening_id, opening_instance)
        logger.info("Added opening with id %s", opening_id)

    def update_opening(self, opening_id: str):
        with self.connect() as client:
            database = client[self.config["database"]]
            opening = OpeningModel.get_opening(opening_id, database)

            opening_instance = self.interface.try_create_instance_from_value("opening", opening)
            if opening_instance is None:
                logger.error("No transformer for key='opening'")
                return

            instances = self.interface.get_instances_by_tag([opening_id])
            
            if len(instances) == 0:
                logger.warn("no opening with id %s", opening_id)
                return

        self.interface.add(opening_id, instances[0])

    def remove_opening_from_cluster(self, opening_id: str):
        self.interface.remove(opening_id)

    def sweep(self):
        # TODO How to do this? Update everyone? Have another endpoint to register an update?

        with self.connect() as client:
            database = client[self.config["database"]]
            users = UserModel.get_all_users_data(database)

            for user in users:
                pass

from pymongo.collection import Collection
from pymongo.uri_parser import parse_userinfo

from trigger.models.hardskill import Hardskill
from trigger.models.server_match import ServerMatch
from trigger.models.server_user import ServerUser
from trigger.models.softskill import Softskill
from trigger.models.user import User

from server import database

from typing import Any, List
from pymongo.database import Database

import requests

from server.database.names import hardskills_collection_name, softskills_collection_name, matches_collection_name

from pymongo.mongo_client import MongoClient
from trigger.models.match import Match

from bson.objectid import ObjectId
from bson.dbref import DBRef

class UserModel:

    collection_name = "users"

    @staticmethod
    def transform_user_data(user_from_db: Any, db: Database) -> ServerUser:
        softskills = []
        key = "softSkills"

        if key in user_from_db:
            softskills_collection = db[softskills_collection_name]
            for ss_ref in user_from_db[key]:
                softskill_from_db = softskills_collection.find_one({"_id": ObjectId(ss_ref['softskillId'])})
                softskills.append(Softskill(name=softskill_from_db["name"], score=0))

        hardskills = []
        key = "hardSkills"

        if key in user_from_db:
            hardskills_collection = db[hardskills_collection_name]
            for hs_ref in user_from_db[key]:
                hardskill_from_db = hardskills_collection.find_one({"_id": ObjectId(hs_ref)})
                hardskills.append(Hardskill(name=hardskill_from_db["name"]))

        return ServerUser (
            name = user_from_db['name'],
            softSkills = softskills,
            hardSkills = hardskills,
            id = str(user_from_db['_id'])
        )

    @staticmethod
    def get_user_data(user_id: str, db: Database) -> ServerUser:
        users_collection = db[UserModel.collection_name]
        user_from_db = users_collection.find_one({"_id": ObjectId(user_id)})
        return UserModel.transform_user_data(user_from_db, db)
        

    @staticmethod
    def get_all_users_data(db: Database) -> List[ServerUser]:
        users_collection = db[UserModel.collection_name]
        users_from_db = users_collection.find({})

        return [ 
            UserModel.transform_user_data(user_from_db, db)
            for user_from_db
            in users_from_db
        ]


    @staticmethod
    def is_super_match(_database: Database, match: ServerMatch):
        # TODO: Implement this
        # FIXME: Is this here? Or in nest ?
        user_likes_project = False
        manager_likes_user = False
        return user_likes_project and manager_likes_user

    @staticmethod
    def insert_user_matches(user_id: str, _database: Database, matches: List[ServerMatch], backend_endpoint: str):
        UserModel._insert_user_matches_impl(user_id, _database, matches)
        UserModel.notify_did_matches(user_id, "user_created", backend_endpoint)

    @staticmethod
    def _insert_user_matches_impl(user_id: str, _database: Database, matches: List[ServerMatch]):
        matches_collection = _database[matches_collection_name]

        match_documents = [
            {
                "type": "opening",
                "user": ObjectId(user_id),
                "matching": ObjectId(match.opening_id_string),
                "superMatch": UserModel.is_super_match(_database, match),
                "score": match.score
            }
            for match in matches
        ]

        if len(match_documents) == 0:
            return

        matches_collection.insert_many(match_documents)

    @staticmethod
    def update_user_matches(user_id: str, _database: Database, matches: List[ServerMatch], backend_endpoint: str):
        matches_collection = _database[matches_collection_name]

        # FIXME: This would mean it's possible for a match to disapear if the user/opening change
        matches_collection.delete_many(
            { "user": ObjectId(user_id) }
        )

        UserModel._insert_user_matches_impl(user_id, _database, matches)
        UserModel.notify_did_matches(user_id, "user_updated", backend_endpoint)

    @staticmethod
    def notify_did_matches(user_id: str, restricted_endpoint: str, backend_endpoint: str):

        # sending post request and saving response as response object 
        r = requests.post(url = f"{backend_endpoint}/{restricted_endpoint}/{user_id}", data = {})
        print(r) 

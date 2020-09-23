from pymongo.collection import Collection

from trigger.models.hardskill import Hardskill
from trigger.models.server_match import ServerMatch
from trigger.models.softskill import Softskill
from trigger.models.user import User

from server import database

from typing import List
from pymongo.database import Database


from server.database.names import hardskills_collection_name, softskills_collection_name, matches_collection_name

from pymongo.mongo_client import MongoClient
from trigger.models.match import Match

from bson.objectid import ObjectId
from bson.dbref import DBRef

class UserModel:

    collection_name = "users"

    @staticmethod
    def get_user_data(user_id: str, db: Database) -> User:
        users_collection = db[UserModel.collection_name]
        user_from_db = users_collection.find_one({"_id": ObjectId(user_id)})

        softskills = []
        key = "softSkills"

        if key in user_from_db:
            softskills_collection = db[softskills_collection_name]
            for ss_ref in user_from_db[key]:
                softskill_from_db = softskills_collection.find_one({"_id": ObjectId(ss_ref)})
                softskills.append(Softskill(name=softskill_from_db["name"], score=0))

        hardskills = []
        key = "hardSkills"

        if key in user_from_db:
            hardskills_collection = db[hardskills_collection_name]
            for hs_ref in user_from_db[key]:
                hardskill_from_db = hardskills_collection.find_one({"_id": ObjectId(hs_ref)})
                hardskills.append(Hardskill(name=hardskill_from_db["name"]))

        return User(user_from_db["name"], softskills, hardskills)

    @staticmethod
    def is_super_match(_database: Database, match: ServerMatch):
        # TODO: Implement this
        user_likes_project = False
        manager_likes_user = False
        return user_likes_project and manager_likes_user

    @staticmethod
    def insert_user_matches(user_id: str, _database: Database, matches: List[ServerMatch]):
        UserModel._insert_user_matches_impl(user_id, _database, matches)

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

        matches_collection.insert_many(match_documents)

    @staticmethod
    def update_user_matches(user_id: str, _database: Database, matches: List[ServerMatch]):
        matches_collection = _database[matches_collection_name]

        matches_collection.delete_many(
            { "user": ObjectId(user_id) }
        )

        UserModel._insert_user_matches_impl(user_id, _database, matches)

from trigger.models.hardskill import Hardskill
from trigger.models.softskill import Softskill
from trigger.models.user import User

from server import database

from typing import List
from pymongo.database import Database


from server.database.names import hardskills_collection_name, softskills_collection_name

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

        return User(user_from_db["name"], softskills, hardskills, [])

    @staticmethod
    def insert_user_matches(user_id: str, matches: List[Match]):

        pass

    @staticmethod
    def update_user_matches(user_id: str, matches: List[Match]):

        pass




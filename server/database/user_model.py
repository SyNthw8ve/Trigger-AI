from trigger.models.user import User
from typing import Any, List

from bson.objectid import ObjectId
from pymongo.database import Database

from server.database.names import hardskills_collection_name, softskills_collection_name
from trigger.models.hardskill import Hardskill
from trigger.models.softskill import Softskill


class UserModel:
    collection_name = "users"

    @staticmethod
    def transform_user_data(user_from_db: Any, db: Database) -> User:
        softskills = []
        key = "softSkills"

        if key in user_from_db:
            softskills_collection = db[softskills_collection_name]
            for ss_ref in user_from_db[key]:
                softskill_from_db = softskills_collection.find_one({"_id": ObjectId(ss_ref['softskillId'])})
                softskills.append(Softskill(name=softskill_from_db["name"]))

        hardskills = []
        key = "hardSkills"

        if key in user_from_db:
            hardskills_collection = db[hardskills_collection_name]
            for hs_info in user_from_db[key]:
                _id = hs_info["hardskillId"] 
                hardskill_from_db = hardskills_collection.find_one({"_id": ObjectId(_id)})
                hardskills.append(Hardskill(name=hardskill_from_db["name"]))

        name = user_from_db['name'] if 'name' in user_from_db else '?' 

        return User(
            name=name,
            softSkills=softskills,
            hardSkills=hardskills
        )

    @staticmethod
    def get_user_data(user_id: str, db: Database) -> User:
        users_collection = db[UserModel.collection_name]
        user_from_db = users_collection.find_one({"_id": ObjectId(user_id)})
        return UserModel.transform_user_data(user_from_db, db)

    @staticmethod
    def get_all_users_data(db: Database) -> List[User]:
        users_collection = db[UserModel.collection_name]
        users_from_db = users_collection.find({})

        return [
            UserModel.transform_user_data(user_from_db, db)
            for user_from_db
            in users_from_db
        ]
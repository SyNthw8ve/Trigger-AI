from typing import Any, List
from bson.objectid import ObjectId
from pymongo.database import Database

from server.database.names import softskills_collection_name, hardskills_collection_name
from trigger.models.hardskill import Hardskill
from trigger.models.opening import Opening
from trigger.models.softskill import Softskill


class OpeningModel:
    collection_name = "openings"

    @staticmethod
    def transform_opening_data(opening: Any, database: Database) -> Opening:
        softskills = []
        key = "softskills"

        if key in opening:
            softskills_collection = database[softskills_collection_name]
            for ss_ref in opening[key]:
                softskill_from_db = softskills_collection.find_one({"_id": ObjectId(ss_ref)})
                softskills.append(Softskill(name=softskill_from_db["name"]))

        hardskills = []
        key = "hardskills"

        if key in opening:
            hardskills_collection = database[hardskills_collection_name]
            for hs_ref in opening[key]:
                hardskill_from_db = hardskills_collection.find_one({"_id": ObjectId(hs_ref)})
                hardskills.append(Hardskill(name=hardskill_from_db["name"]))

        return Opening(str(opening["_id"]), hardskills, softskills)

    @staticmethod
    def get_opening(opening_id: str, database: Database) -> Opening:
        openings_collection = database[OpeningModel.collection_name]
        opening_from_db = openings_collection.find_one({"_id": ObjectId(opening_id)})
        return OpeningModel.transform_opening_data(opening_from_db, database)

    @staticmethod
    def get_all_openings(database: Database) -> List[Opening]:
        openings_collection = database[OpeningModel.collection_name]
        openings_from_db = openings_collection.find({})

        return [
            OpeningModel.transform_opening_data(opening_from_db, database)
            for opening_from_db
            in openings_from_db
        ]

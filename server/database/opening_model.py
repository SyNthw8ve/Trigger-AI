from bson.objectid import ObjectId
from pymongo.database import Database

from server.database.names import softskills_collection_name, hardskills_collection_name, languages_collection_name
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.opening import Opening
from trigger.models.softskill import Softskill


class OpeningModel:

    collection_name = "openings"

    @staticmethod
    def get_opening(opening_id: str, database: Database) -> Opening:
        openings_collection = database[OpeningModel.collection_name]
        opening_from_db = openings_collection.find_one({"_id": ObjectId(opening_id)})

        softskills = []
        key = "softskills"

        if key in opening_from_db:
            softskills_collection = database[softskills_collection_name]
            for ss_ref in opening_from_db[key]:
                softskill_from_db = softskills_collection.find_one({"_id": ObjectId(ss_ref)})
                softskills.append(Softskill(name=softskill_from_db["name"], score=0))

        hardskills = []
        key = "hardskills"

        if key in opening_from_db:
            hardskills_collection = database[hardskills_collection_name]
            for hs_ref in opening_from_db[key]:
                hardskill_from_db = hardskills_collection.find_one({"_id": ObjectId(hs_ref)})
                hardskills.append(Hardskill(name=hardskill_from_db["name"]))

        # TODO: Do we need area?
        area = ""
        key = "area"
        if key in opening_from_db:
            area = opening_from_db[key]

        # TODO: Do we need sector?
        sector = ""
        key = "sector"
        if key in opening_from_db:
            sector = opening_from_db[key]

        # TODO: Do we need languages here?
        languages = []
        key = "languages"
        if key in opening_from_db:
            languages_collection = database[languages_collection_name]
            for l_ref in opening_from_db[key]:
                language_from_db = languages_collection.find_one({"_id": ObjectId(l_ref)})
                languages.append(Language(name=language_from_db["name"]))

        # TODO: Do we need entityId here?
        return Opening(opening_id, sector, area, languages, hardskills, softskills)
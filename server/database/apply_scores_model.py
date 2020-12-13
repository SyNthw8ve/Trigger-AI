from typing import Optional

import mongoengine
from server.database.server_score import ServerScore

from bson.objectid import ObjectId
from pymongo.database import Database

from server.database.names import apply_scores_collection_name


class ApplyScoresModel:
    collection_name = apply_scores_collection_name

    @staticmethod
    def insert_apply_score(_database: Database, score: ServerScore) -> Optional[ObjectId]:

        collection = _database[ApplyScoresModel.collection_name]
        return collection.insert_one(score.to_mongo()).inserted_id
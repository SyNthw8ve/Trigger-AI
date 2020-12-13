from server.database.server_score import ServerScore
from typing import Any, List

from bson.objectid import ObjectId
from pymongo.database import Database

from server.database.names import matches_collection_name


class ServerMatchesModel:
    collection_name = matches_collection_name

    @staticmethod
    def insert_server_matches(_database: Database, matches: List[ServerScore]):

        if len(matches) == 0:
            return []

        matches_collection = _database[ServerMatchesModel.collection_name]

        match_documents = [
            match.to_mongo()
            for match in matches
        ]

        return matches_collection.insert_many(match_documents).inserted_ids

    @staticmethod
    def delete_user_server_matches(_database: Database, user_id_string: str):

        matches_collection = _database[matches_collection_name]

        matches_collection.delete_many(
            {"user_id": ObjectId(user_id_string)}
        )

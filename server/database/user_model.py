import pymongo

from typing import List
from trigger.models.Match import Match

class UserModel():

    @staticmethod
    def get_user_data(user_id: str, db):

        pass

    @staticmethod
    def insert_user_matches(user_id: str, matches: List[Match]):

        pass

    @staticmethod
    def update_user_matches(user_id: str, matches: List[Match]):

        pass




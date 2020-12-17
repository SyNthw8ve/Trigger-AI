import pickle
from typing import List
import numpy
from ..models.user import User


class UserInstance:

    def __init__(self, user: User, embedding: numpy.ndarray):
        self.user = user
        self.embedding = embedding

    @staticmethod
    def save_instances(filename: str, instances: List["UserInstance"]) -> None:

        with open(filename, 'wb') as file:

            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename: str) -> List["UserInstance"]:
        
        with open(filename, 'rb') as file:
            
            users_instances: List["UserInstance"] = pickle.load(file)
            return users_instances
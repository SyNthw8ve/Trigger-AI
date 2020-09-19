import pymongo
import redis
import time

from rq import Queue
from flask import Flask

app = Flask(__name__)

@app.route('/user_match/<user_id>', methods=['POST'])
def compute_user_matches(user_id):

    pass

@app.route('/user_match/<user_id>', methods=['PUT'])
def update_user_matches(user_id):

    pass

@app.route('/opening/<opening_id>', methods=['POST'])
def insert_opening_to_cluster(opening_id):

    pass

@app.route('/opening/<opening_id>', methods=['PUT'])
def update_opening(opening_id):

    pass

@app.route('/opening/<opening_id>', methods=['DELETE'])
def remove_opening_from_cluster(opening_id):

    pass

if __name__ == "__main__":

    client = pymongo.MongoClient('localhost', 27017)

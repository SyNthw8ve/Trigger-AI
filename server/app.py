import sys
from pathlib import Path

from flask import Flask
from redis import Redis
from rq import Queue

from server.jobs import on_compute_user_matches, on_compute_user_score, on_update_user_matches, \
    on_insert_opening_to_cluster, on_update_opening, on_remove_opening_from_cluster

app = Flask(__name__)

processing = Queue(connection=Redis())


@app.route('/user_match/<user_id>', methods=['POST'])
def compute_user_matches(user_id: str):
    job = processing.enqueue(on_compute_user_matches, args=[user_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/score/<user_id>/<opening_id>', methods=['POST'])
def compute_user_score(user_id: str, opening_id: str):
    job = processing.enqueue(on_compute_user_score, args=[user_id, opening_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/user_match/<user_id>', methods=['PUT'])
def update_user_matches(user_id: str):
    job = processing.enqueue(on_update_user_matches, args=[user_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['POST'])
def insert_opening_to_cluster(opening_id: str):
    job = processing.enqueue(on_insert_opening_to_cluster, args=[opening_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['PUT'])
def update_opening(opening_id: str):
    job = processing.enqueue(on_update_opening, args=[opening_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['DELETE'])
def remove_opening_from_cluster(opening_id: str):
    job = processing.enqueue(on_remove_opening_from_cluster, args=[opening_id])

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"

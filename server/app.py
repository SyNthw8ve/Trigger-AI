from flask import Flask

import rq_dashboard

from server.jobs import on_compute_user_matches, on_compute_user_score, on_update_user_matches, \
    on_insert_opening_to_cluster, on_update_opening, on_remove_opening_from_cluster

def create_app():
    app = Flask(__name__)

    app.config.from_object(rq_dashboard.default_settings)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    from .jobs import rq
    rq.init_app(app)

    # more here..
    return app

app = create_app()

@app.route('/user_match/<user_id>', methods=['POST'])
def compute_user_matches(user_id: str):
    job = on_compute_user_matches.queue(user_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/score/<user_id>/<opening_id>', methods=['POST'])
def compute_user_score(user_id: str, opening_id: str):
    job = on_compute_user_score.queue(user_id, opening_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/user_match/<user_id>', methods=['PUT'])
def update_user_matches(user_id: str):
    job = on_update_user_matches.queue(user_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['POST'])
def insert_opening_to_cluster(opening_id: str):
    job = on_insert_opening_to_cluster.queue(opening_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['PUT'])
def update_opening(opening_id: str):
    job = on_update_opening.queue(opening_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"


@app.route('/opening/<opening_id>', methods=['DELETE'])
def remove_opening_from_cluster(opening_id: str):
    job = on_remove_opening_from_cluster.queue(opening_id)

    if job:
        return "Scheduled"
    else:
        return "Failure to Schedule"

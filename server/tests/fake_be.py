from flask import Flask

our_flask = Flask(__name__)


@our_flask.route('/flask/user_created/<user_id>', methods=['POST'])
def user_created(user_id):
    print(user_id)
    with open('test_calculate_matches', 'w') as file:
        return ""


@our_flask.route('/flask/user_score/<score_id>', methods=['POST'])
def user_score(score_id):
    print(score_id)
    with open('test_calculate_score', 'w') as file:
        return ""

@our_flask.route('/flask/user_updated/<user_id>', methods=['POST'])
def user_updated(user_id):
    print(user_id)
    with open('test_user_updated', 'w') as file:
        return ""

our_flask.run(host='0.0.0.0', port=3000)
import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

from sklearn.metrics import silhouette_score, calinski_harabasz_score

from trigger.train.cluster.gstream.gstream import GNG


class GNGParameterEnvironment(py_environment.PyEnvironment):

    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=11, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype=np.float64, name='scores'
        )

        self._state = GNG(epsilon_b=0.001,
                          epsilon_n=0,
                          lam=5,
                          beta=0.9995,
                          alpha=0.95,
                          max_age=10,
                          off_max_age=10,
                          lambda_2=0.2,
                          nodes_per_cycle=1,
                          dimensions=1024,
                          index_type='L2')

        self.Sst = 0
        self.CHst = 0

        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = GNG(epsilon_b=0.001,
                          epsilon_n=0,
                          lam=5,
                          beta=0.9995,
                          alpha=0.95,
                          max_age=10,
                          off_max_age=10,
                          lambda_2=0.2,
                          nodes_per_cycle=1,
                          dimensions=1024,
                          index_type='L2')
        self._episode_ended = False
        return ts.restart(np.array([0, 0], dtype=np.float))

    def _step(self, action):

        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        # Make sure episodes don't go on forever.
        if action == 0:
            
            self._state.lam += 0

        elif action == 1:

            self._state.lam += 1

        elif action == 2:

            if self._state.lam >= 2:

                self._state.lam -= 1

        elif action == 3:

            self._state.epsilon_b += 0

        elif action == 4:

            self._state.epsilon_b += 0.001

        elif action == 5:

            if self._state.epsilon_b >= 0.001:

                self._state.epsilon_b -= 0.001

        elif action == 6:

            self._state.nodes_per_cycle += 0

        elif action == 7:

            self._state.nodes_per_cycle += 1

        elif action == 8:

            if self._state.nodes_per_cycle > 0:

                self._state.nodes_per_cycle -= 1

        elif action == 9:

            self._state.max_age += 0

        elif action == 10:

            self._state.max_age += 1

        elif action == 11:

            if self._state.max_age > 0:

                self._state.max_age -= 1

        else:
            raise ValueError('`action` should be 0 or 1.')

        results = eval_cluster(self._state)
        Ss = results[0]
        CHs = results[1]

        if Ss < 0:

            self._episode_ended = True
            return ts.termination(np.array([Ss, CHs], dtype=np.float), 0)

        elif Ss > self.Sst:

            self.Sst = Ss
            self.CHst = CHs

            return ts.transition(
                np.array([Ss, CHs], dtype=np.float), reward=0.5, discount=1.0)

        elif Ss < self.Sst:

            self.Sst = Ss
            self.CHst = CHs

            return ts.transition(
                np.array([Ss, CHs], dtype=np.float), reward=-1.0, discount=1.0)

        else:

            self.Sst = Ss
            self.CHst = CHs

            return ts.transition(
                np.array([Ss, CHs], dtype=np.float), reward=0.0, discount=1.0)


def eval_cluster(gng: GNG):

    X = gng.instances
    labels = []
    Ss = 0
    CHs = 0

    for x in X:

        labels.append(gng.get_cluster(x))

    try:
        Ss = silhouette_score(X, labels)
    
    except:
        Ss = 0

    try:
        CHs = calinski_harabasz_score(X, labels)

    except:
        CHs = 0

    return np.array([Ss, CHs], dtype=np.float)

def apply_action(self, action: int):

    switcher = {
        0: self.treat_lambda(0),
        1: self.treat_lambda(1),
        2: self.treat_lambda(-1),
        3: self.treat_learning_rate(0),
        4: self.treat_learning_rate(0.001),
        5: self.treat_learning_rate(-0.001),
        6: self.treat_nodes_cycle(0),
        7: self.treat_nodes_cycle(1),
        8: self.treat_nodes_cycle(-1),
        9: self.treat_link_age(0),
        10: self.treat_link_age(10),
        11: self.treat_link_age(-10),
    }

    switcher[action]

def treat_lambda(self, increment):

    if increment < 0 and self._state.lam > abs(increment):

        self._state.lam += increment

    else:

        self._state.lam += increment

def treat_learning_rate(self, increment):

    if increment < 0 and self._state.epsilon_b > abs(increment):

        self._state.epsilon_b += increment

    else:

        self._state.epsilon_b += increment

def treat_nodes_cycle(self, increment):

    if increment < 0 and self._state.nodes_per_cycle > abs(increment):

        self._state.nodes_per_cycle += increment

    else:

        self._state.nodes_per_cycle += increment

def treat_link_age(self, increment):

    if increment < 0 and self._state.max_age > abs(increment):

        self._state.max_age += increment

    else:

        self._state.max_age += increment
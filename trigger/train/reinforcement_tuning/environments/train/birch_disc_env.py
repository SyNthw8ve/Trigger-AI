import tensorflow as tf
import numpy as np
import copy

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

from sklearn.metrics import silhouette_score, calinski_harabasz_score

from trigger.train.cluster.birch.birch import Birch
from trigger.train.reinforcement_tuning.util.cluster_metrics import eval_cluster

class BirchDiscreteEnvironment(py_environment.PyEnvironment):

    def __init__(self, initial_threshold: float, initial_branching: int, dimension: int, instances):

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=9, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype=np.float64, name='scores'
        )

        self._state = Birch(threshold=initial_threshold,
                            branching_factor=initial_branching)


        self.initial_threshold = initial_threshold
        self.initial_branching = initial_branching

        self.instances = instances
        self.iterator_instances = iter(self.instances[1:])

        self.Sst = 0.0
        self.CHst = 0.0

        self._state.add(self.instances[0])

        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):

        self._state = Birch(threshold=self.initial_threshold,
                            branching_factor=self.initial_branching)

        self._state.add(self.instances[0])

        self.Sst = 0.0
        self.CHst = 0.0
        self.iterator_instances = iter(self.instances[1:])

        self._episode_ended = False
        return ts.restart(np.array([self.Sst, self.CHst], dtype=np.float))

    def _take_action(self, action):

        if action == 0:

            self._state.adapt(
                self._state.threshold + 0.05, self._state.branching_factor)

        elif action == 1:

            if self._state.threshold >= 0.1:

                self._state.adapt(
                    self._state.threshold - 0.05, self._state.branching_factor)

        elif action == 2:

            self._state.adapt(
                self._state.threshold, self._state.branching_factor + 5)

        elif action == 3:

            if self._state.branching_factor >= 10:

                self._state.adapt(
                    self._state.threshold, self._state.branching_factor - 5)

        elif action == 4:

            self._state.threshold += 0

        elif action == 5:

            self._state.branching_factor += 0

        elif action == 6:

            self._state.adapt(
                self._state.threshold + 0.05, self._state.branching_factor + 5)

        elif action == 7:

            if self._state.branching_factor >= 10:

                self._state.adapt(
                    self._state.threshold + 0.05, self._state.branching_factor - 5)

        elif action == 8:

            if self._state.threshold >= 0.1:

                self._state.adapt(
                    self._state.threshold - 0.05, self._state.branching_factor + 5)

        elif action == 9:

            if self._state.branching_factor >= 10 and self._state.threshold >= 0.1:

                self._state.adapt(
                    self._state.threshold - 0.05, self._state.branching_factor - 5)

        else:
            raise ValueError('`action` should be between 0 and 9.')

    def _compute_rewards(self, Ss, CHs):

        try:

            if Ss > self.Sst:
                reward = 2.0

            elif Ss < self.Sst:
                reward = -1.0

            else:
                reward = -0.5

            self.Sst = Ss
            self.CHst = CHs
            self._state.add(next(self.iterator_instances))

            return ts.transition(
                np.array([Ss, CHs], dtype=np.float), reward=reward, discount=1.0)

        except StopIteration:

            self._episode_ended = True
            return ts.termination(np.array([Ss, CHs], dtype=np.float), 0)

    def _step(self, action):

        if self._episode_ended:

            return self.reset()

        self._take_action(action)

        updated_metrics = eval_cluster(self._state)

        Ss = updated_metrics['ss']
        CHs = updated_metrics['chs']

        return self._compute_rewards(Ss, CHs)
import tensorflow as tf
import numpy as np
import copy

from trigger.train.reinforcement_tuning.util.cluster_metrics import eval_cluster

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

from trigger.train.cluster.birch.birch import Birch

class BirchContinuousEnvironment(py_environment.PyEnvironment):

    def __init__(self, initial_threshold: float, initial_branching: int, dimension: int, instances):

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype='float32', minimum=-1, maximum=1, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(dimension,), dtype='float32', name='scores'
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

        observation = np.mean(
            self._state.model.subcluster_centers_, axis=0, dtype='float32')

        self._episode_ended = False
        return ts.restart(observation)

    def _take_action(self, action):

        new_threshold = self._state.threshold
        new_branching = self._state.branching_factor

        if self._state.threshold + action[0] > 0:

            new_threshold += action[0]

        if self._state.branching_factor + int(round(action[1]*5)) > 1:

            new_branching += int(round(action[1]*5))

        self._state.adapt(new_threshold, new_branching)

    def _compute_rewards(self, Ss, CHs):

        observation = np.mean(
            self._state.model.subcluster_centers_, axis=0, dtype='float32')

        reward = 0

        if Ss == self.Sst or CHs == self.CHst:

            reward = -0.2

        else:

            delta_ss = Ss - self.Sst
            delta_ch = CHs - self.CHst

            if max(CHs, self.CHst) == 0:
                delta_ch = 0

            else:
                delta_ch = delta_ch / (CHs + self.CHst)

            self.Sst = Ss
            self.CHst = CHs

            reward = delta_ch + delta_ss

        try:

            self._state.add(next(self.iterator_instances))

            return ts.transition(observation, reward=reward, discount=1.0)

        except StopIteration:

            self._episode_ended = True
            return ts.termination(observation, reward)

    def _step(self, action):

        if self._episode_ended:

            return self.reset()

        self._take_action(action)

        updated_metrics = eval_cluster(self._state)

        Ss = updated_metrics['ss']
        CHs = updated_metrics['chs']
        
        return self._compute_rewards(Ss, CHs)

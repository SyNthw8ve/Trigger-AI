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
from trigger.train.reinforcement_tuning.util.cluster_metrics import eval_cluster

from trigger.train.cluster.birch.birch import Birch

class OnlineBirchContinuosEnvironment(py_environment.PyEnvironment):

    def __init__(self, birch: Birch, dimension: int):

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype='float32', minimum=-1, maximum=1, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(dimension,), dtype=np.float64, name='scores'
        )

        self._state = birch

        first_metrics = eval_cluster(birch)

        self.Sst = first_metrics['ss']
        self.CHst = first_metrics['chs']

        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):

        observation = np.mean(
            self._state.model.subcluster_centers_, axis=0, dtype="float32")

        return ts.restart(observation)

    def _step(self, action):

        new_threshold = self._state.threshold
        new_branching = self._state.branching_factor

        if self._state.threshold + action[0] > 0:

            new_threshold += action[0]

        if self._state.branching_factor + int(round(action[1]*5)) > 1:

            new_branching += int(round(action[1]*5))

        self._state.adapt(new_threshold, new_branching)

        updated_metrics = eval_cluster(self._state)

        Ss = updated_metrics['ss']
        CHs = updated_metrics['chs']

        return self._compute_rewards(Ss, CHs)

    def _compute_rewards(self, Ss, CHs):
        
        observation = np.mean(
            self._state.model.subcluster_centers_, axis=0, dtype="float32")

        delta_ss = Ss - self.Sst
        delta_ch = CHs - self.CHst

        if max(CHs, self.CHst) == 0:
            delta_ch = 0

        else:
            delta_ch = delta_ch / max(CHs, self.CHst)

        self.Sst = Ss
        self.CHst = CHs

        reward = delta_ch + delta_ss

        if reward == 0:
            reward = -0.5

        return ts.transition(
            observation, reward=reward, discount=1.0)
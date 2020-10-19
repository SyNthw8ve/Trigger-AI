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

from trigger.train.cluster.gturbo.gturbo import GTurbo


class TurboContinuousEnvironment(py_environment.PyEnvironment):

    def __init__(self, initial_epsilon_b, initial_lambda, initial_max_age, initial_radius,
                 dimension, instances):

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(4,), dtype='float32', minimum=-1, maximum=1, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(2*dimension,), dtype='float32', name='scores'
        )

        self._state = GTurbo(epsilon_b=initial_epsilon_b, epsilon_n=0.0, lam=initial_lambda, beta=0.995, alpha=0.95,
                             max_age=initial_max_age, r0=initial_radius, dimensions=dimension)

        self.initial_epsilon_b = initial_epsilon_b
        self.initial_lambda = initial_lambda
        self.initial_max_age = initial_max_age
        self.initial_radius = initial_radius
        self.dimension = dimension

        self.instances = instances

        self.Sst = 0.0
        self.CHst = 0.0

        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _observe_state(self):

        mean_center = np.mean(
            [node.prototype for node in self._state.graph.nodes.values()], axis=0, dtype='float32')

        var_center = np.var(
            [node.prototype for node in self._state.graph.nodes.values()], axis=0, dtype='float32')

        observation = np.concatenate((mean_center, var_center))

        return observation

    def _reset(self):

        self._state = GTurbo(epsilon_b=self.initial_epsilon_b, epsilon_n=0.0, lam=self.initial_lambda,
                             beta=0.995, alpha=0.95, max_age=self.initial_max_age,
                             r0=self.initial_radius, dimensions=self.dimension)

        self.Sst = 0.0
        self.CHst = 0.0
        self.iterator_instances = iter(self.instances)

        observation = self._observe_state()

        self._episode_ended = False
        return ts.restart(observation)

    def _take_action(self, action):

        new_epsilon_b = self._state.epsilon_b
        new_lambda = self._state.lam
        new_max_age = self._state.max_age
        new_radius = self._state.r0

        if self._state.epsilon_b + action[0] > 0:

            new_epsilon_b += action[0]

        if self._state.lam + int(round(action[1]*5)) > 1:

            new_lambda += int(round(action[1]*5))

        if self._state.max_age + int(round(action[2]*5)) > 1:

            new_max_age += int(round(action[2]*5))

        if self._state.r0 + action[3] > 0:

            new_radius += action[3]

        self._state = self._state.re_ignite(
            new_epsilon_b, new_lambda, new_max_age, new_radius)

    def _compute_rewards(self, Ss, CHs):

        observation = self._observe_state()

        reward = 0

        if Ss == self.Sst or CHs == self.CHst:

            reward = -0.2

        else:

            delta_ss = Ss - self.Sst
            delta_ch = CHs - self.CHst

            if max(CHs, self.CHst) == 0:
                delta_ch = 0

            else:
                delta_ch = delta_ch / max(CHs, self.CHst)

            self.Sst = Ss
            self.CHst = CHs

            reward = delta_ch + delta_ss

        try:

            next_instance = next(self.iterator_instances)

            self._state.turbo_step(next_instance.opening.entityId, next_instance.embedding)

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

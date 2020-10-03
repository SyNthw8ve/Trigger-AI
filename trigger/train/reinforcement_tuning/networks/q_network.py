import tensorflow as tf
import numpy as np
import os
import logging

from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.policies import random_tf_policy
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common
from tf_agents.policies import policy_saver

from trigger.train.cluster.birch.birch import Birch

class QNetwork():

    def __init__(self, environment_train, environment_eval, learning_rate=1e-3):

        self.train_env = tf_py_environment.TFPyEnvironment(environment_train)
        self.eval_env = tf_py_environment.TFPyEnvironment(environment_eval)

        fc_layer_params = (100,)

        q_net = q_network.QNetwork(
            self.train_env.observation_spec(),
            self.train_env.action_spec(),
            fc_layer_params=fc_layer_params)

        optimizer = tf.compat.v1.train.AdamOptimizer(
            learning_rate=learning_rate)

        self.global_step = tf.compat.v1.train.get_or_create_global_step()

        self.agent = dqn_agent.DqnAgent(
            self.train_env.time_step_spec(),
            self.train_env.action_spec(),
            q_network=q_net,
            optimizer=optimizer,
            td_errors_loss_fn=common.element_wise_squared_loss,
            train_step_counter=self.global_step)

        self.agent.initialize()

    def train(self, policy_name, num_iterations=20000, initial_collect_steps=1000,
              collect_steps_per_iteration=1, replay_buffer_max_length=100000, batch_size=64,
              log_interval=200, num_eval_episodes=10, eval_interval=1000, tempdir='./tf_policy'):

        random_policy = random_tf_policy.RandomTFPolicy(self.train_env.time_step_spec(),
                                                        self.train_env.action_spec())

        replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            data_spec=self.agent.collect_data_spec,
            batch_size=self.train_env.batch_size,
            max_length=replay_buffer_max_length)

        logging.info("Pre-collecting data")

        self._collect_data(self.train_env, random_policy,
                           replay_buffer, steps=initial_collect_steps)

        dataset = replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=batch_size,
            num_steps=2).prefetch(3)

        iterator = iter(dataset)

        self.agent.train = common.function(self.agent.train)

        self.agent.train_step_counter.assign(0)

        avg_return = self._compute_avg_return(
            self.eval_env, self.agent.policy, num_eval_episodes)
        returns = [avg_return]

        logging.info("Training...")

        checkpoint_dir = os.path.join(tempdir, 'checkpoint/q_net')
        train_checkpointer = common.Checkpointer(
            ckpt_dir=checkpoint_dir,
            max_to_keep=1,
            agent=self.agent,
            policy=self.agent.policy,
            replay_buffer=replay_buffer,
            global_step=self.global_step
        )

        for _ in range(num_iterations):

            for _ in range(collect_steps_per_iteration):
                self._collect_step(
                    self.train_env, self.agent.collect_policy, replay_buffer)

            experience, unused_info = next(iterator)
            train_loss = self.agent.train(experience).loss

            step = self.agent.train_step_counter.numpy()

            if step % log_interval == 0:
                logging.info('step = {0}: loss = {1}'.format(step, train_loss))

            if step % eval_interval == 0:

                train_checkpointer.save(self.global_step)

                avg_return = self._compute_avg_return(
                    self.eval_env, self.agent.policy, num_eval_episodes)
                logging.info('step = {0}: Average Return = {1}'.format(
                    step, avg_return))
                returns.append(avg_return)

        self._save_policy(policy_name, tempdir)

    def _compute_avg_return(self, environment, policy, num_episodes=10):

        total_return = 0.0
        for _ in range(num_episodes):

            time_step = environment.reset()
            episode_return = 0.0

            while not time_step.is_last():
                action_step = policy.action(time_step)
                time_step = environment.step(action_step.action)
                episode_return += time_step.reward
            total_return += episode_return

        avg_return = total_return / num_episodes
        return avg_return.numpy()[0]

    def _collect_step(self, environment, policy, buffer):
        
        time_step = environment.current_time_step()
        action_step = policy.action(time_step)
        next_time_step = environment.step(action_step.action)
        traj = trajectory.from_transition(
            time_step, action_step, next_time_step)

        buffer.add_batch(traj)

    def _collect_data(self, env, policy, buffer, steps):
        for _ in range(steps):
            self._collect_step(env, policy, buffer)

    def _save_policy(self, policy_name, tempdir):

        policy_dir = os.path.join(tempdir, policy_name)

        logging.info(f"Saving policy to {policy_dir}")

        tf_policy_saver = policy_saver.PolicySaver(self.agent.policy)

        tf_policy_saver.save(policy_dir)

        logging.info(f"Policy {policy_name} saved to {policy_dir}")

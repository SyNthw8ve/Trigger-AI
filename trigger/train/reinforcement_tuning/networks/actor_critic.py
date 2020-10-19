import tensorflow as tf
import numpy as np
import reverb
import logging
import os

from tf_agents.agents.ddpg import critic_network
from tf_agents.agents.sac import sac_agent
from tf_agents.agents.sac import tanh_normal_projection_network
from tf_agents.experimental.train import actor
from tf_agents.environments import tf_py_environment
from tf_agents.experimental.train import learner
from tf_agents.experimental.train import triggers
from tf_agents.experimental.train.utils import spec_utils
from tf_agents.experimental.train.utils import strategy_utils
from tf_agents.experimental.train.utils import train_utils
from tf_agents.metrics import py_metrics
from tf_agents.utils import common
from tf_agents.networks import actor_distribution_network
from tf_agents.policies import greedy_policy
from tf_agents.policies import py_tf_eager_policy
from tf_agents.policies import random_py_policy
from tf_agents.policies import policy_saver
from tf_agents.replay_buffers import reverb_replay_buffer
from tf_agents.replay_buffers import reverb_utils

class ActorCriticNetwork():

    def __init__(self, collect_env, eval_env, 
                 critic_learning_rate=3e-4, actor_learning_rate=3e-4, alpha_learning_rate=3e-4, 
                 target_update_tau=0.005, target_update_period=1, gamma=0.9, reward_scale_factor=1.0,
                 actor_fc_layer_params=(256, 256), critic_joint_fc_layer_params=(256, 256),
                 use_tpu=False, use_gpu=True):

        self.collect_env = collect_env
        self.eval_env = eval_env

        strategy = strategy_utils.get_strategy(tpu=False, use_gpu=True)

        observation_spec, action_spec, time_step_spec = (
            spec_utils.get_tensor_specs(collect_env))

        with strategy.scope():
            critic_net = critic_network.CriticNetwork(
                (observation_spec, action_spec),
                observation_fc_layer_params=None,
                action_fc_layer_params=None,
                joint_fc_layer_params=critic_joint_fc_layer_params,
                kernel_initializer='glorot_uniform',
                last_kernel_initializer='glorot_uniform')

        with strategy.scope():
            actor_net = actor_distribution_network.ActorDistributionNetwork(
                observation_spec,
                action_spec,
                fc_layer_params=actor_fc_layer_params,
                continuous_projection_net=(
                    tanh_normal_projection_network.TanhNormalProjectionNetwork))

        with strategy.scope():
        
            self.global_step = tf.compat.v1.train.get_or_create_global_step()

            self.tf_agent = sac_agent.SacAgent(
                time_step_spec,
                action_spec,
                actor_network=actor_net,
                critic_network=critic_net,
                actor_optimizer=tf.compat.v1.train.AdamOptimizer(
                    learning_rate=actor_learning_rate),
                critic_optimizer=tf.compat.v1.train.AdamOptimizer(
                    learning_rate=critic_learning_rate),
                alpha_optimizer=tf.compat.v1.train.AdamOptimizer(
                    learning_rate=alpha_learning_rate),
                target_update_tau=target_update_tau,
                target_update_period=target_update_period,
                td_errors_loss_fn=tf.math.squared_difference,
                gamma=gamma,
                reward_scale_factor=reward_scale_factor,
                train_step_counter=self.global_step)

            self.tf_agent.initialize()

    def train(self, policy_name, num_iterations=20000, log_interval=200, num_eval_episodes=10,
              eval_interval=1000, policy_save_interval=1000, tempdir='./tf_policy',
              initial_collect_steps=1000, collect_steps_per_iteration=1, 
              replay_buffer_capacity=100000, batch_size=64):

        rate_limiter = reverb.rate_limiters.SampleToInsertRatio(
        samples_per_insert=3.0, min_size_to_sample=3, error_buffer=3.0)

        table_name = 'uniform_table'
        table = reverb.Table(
            table_name,
            max_size=replay_buffer_capacity,
            sampler=reverb.selectors.Uniform(),
            remover=reverb.selectors.Fifo(),
            rate_limiter=reverb.rate_limiters.MinSize(1))

        reverb_server = reverb.Server([table])

        reverb_replay = reverb_replay_buffer.ReverbReplayBuffer(
            self.tf_agent.collect_data_spec,
            sequence_length=2,
            table_name=table_name,
            local_server=reverb_server)

        checkpoint_dir = os.path.join(tempdir, 'checkpoints/ac')
        train_checkpointer = common.Checkpointer(
            ckpt_dir=checkpoint_dir,
            max_to_keep=1,
            agent=self.tf_agent,
            policy=self.tf_agent.policy,
            replay_buffer=reverb_replay,
            global_step=self.global_step
        )

        dataset = reverb_replay.as_dataset(
        sample_batch_size=batch_size, num_steps=2).prefetch(50)

        def experience_dataset_fn(): return dataset

        tf_eval_policy = self.tf_agent.policy
        eval_policy = py_tf_eager_policy.PyTFEagerPolicy(
            tf_eval_policy, use_tf_function=True)

        tf_collect_policy = self.tf_agent.collect_policy
        collect_policy = py_tf_eager_policy.PyTFEagerPolicy(
            tf_collect_policy, use_tf_function=True)

        random_policy = random_py_policy.RandomPyPolicy(
            self.collect_env.time_step_spec(), self.collect_env.action_spec())

        rb_observer = reverb_utils.ReverbAddTrajectoryObserver(
            reverb_replay.py_client,
            table_name,
            sequence_length=2,
            stride_length=1)

        initial_collect_actor = actor.Actor(
            self.collect_env,
            random_policy,
            self.global_step,
            steps_per_run=initial_collect_steps,
            observers=[rb_observer])

        initial_collect_actor.run()

        env_step_metric = py_metrics.EnvironmentSteps()
        collect_actor = actor.Actor(
            self.collect_env,
            collect_policy,
            self.global_step,
            steps_per_run=1,
            metrics=actor.collect_metrics(10),
            summary_dir=os.path.join(tempdir, learner.TRAIN_DIR),
            observers=[rb_observer, env_step_metric])

        eval_actor = actor.Actor(
            self.eval_env,
            eval_policy,
            self.global_step,
            episodes_per_run=num_eval_episodes,
            metrics=actor.eval_metrics(num_eval_episodes),
            summary_dir=os.path.join(tempdir, 'eval'),
        )

        saved_model_dir = os.path.join(tempdir, learner.POLICY_SAVED_MODEL_DIR)

        learning_triggers = [
            triggers.PolicySavedModelTrigger(
                saved_model_dir,
                self.tf_agent,
                self.global_step,
                interval=policy_save_interval),
            triggers.StepPerSecondLogTrigger(self.global_step, interval=1000),
        ]

        agent_learner = learner.Learner(
            tempdir,
            self.global_step,
            self.tf_agent,
            experience_dataset_fn,
            triggers=learning_triggers)

        def get_eval_metrics():
            eval_actor.run()
            results = {}
            for metric in eval_actor.metrics:
                results[metric.name] = metric.result()
            return results

        metrics = get_eval_metrics()

        def log_eval_metrics(step, metrics):
            eval_results = (', ').join(
                '{} = {:.6f}'.format(name, result) for name, result in metrics.items())
            logging.info('step = {0}: {1}'.format(step, eval_results))

        log_eval_metrics(0, metrics)

        self.tf_agent.train_step_counter.assign(0)

        avg_return = get_eval_metrics()["AverageReturn"]
        returns = [avg_return]

        for _ in range(num_iterations):
            
            collect_actor.run()
            loss_info = agent_learner.run(iterations=1)

            step = agent_learner.train_step_numpy

            if eval_interval and step % eval_interval == 0:
                metrics = get_eval_metrics()
                log_eval_metrics(step, metrics)
                returns.append(metrics["AverageReturn"])

            if log_interval and step % log_interval == 0:
                logging.info(f"Saving checkpoint at {step} steps...")

                train_checkpointer.save(self.global_step)

                logging.info('step = {0}: loss = {1}'.format(
                    step, loss_info.loss.numpy()))

        self._save_policy(policy_name, tempdir)

        rb_observer.close()
        reverb_server.stop()

    def _save_policy(self, policy_name, tempdir):

        policy_dir = os.path.join(tempdir, policy_name)

        logging.info(f"Saving policy to {policy_dir}")

        tf_policy_saver = policy_saver.PolicySaver(self.tf_agent.policy)

        tf_policy_saver.save(policy_dir)

        logging.info(f"Policy {policy_name} saved to {policy_dir}")


import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.trajectories import time_step as ts

from trigger.train.reinforcement_tuning.gng_environment import GNGParameterEnvironment

environment = GNGParameterEnvironment()
utils.validate_py_environment(environment, episodes=5)
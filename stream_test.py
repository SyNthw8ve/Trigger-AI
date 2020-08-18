from trigger.models.opening import Opening
from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.user import User
from trigger.recommend import smart
from trigger.recommend.controller import Controller
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningTransformer
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer
from celluloid import Camera

import logging

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

from trigger.train.cluster.gstream.gstream import GStream, GNG
from matplotlib import pyplot as plt 

import pprint
import numpy as np
import pickle as pk

with open('examples/2D_points_no_true/4', 'rb') as f:

    stream = pk.load(f)

np_stream = [np.array([data[0], data[1]]) for data in stream]

#gstream = GStream(vector_size=2, alpha1=0.05, alpha2=0.0006, beta=200, error_decrease=0.95)

fig = plt.figure()
camera = Camera(fig)

gng = GNG(0.1, 0, 5, 0.9995, 0.95, 10, 0.1, 1.5, 2, camera)

gng.lambda_fase(np_stream)

gng.animate()

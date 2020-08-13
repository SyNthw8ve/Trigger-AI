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

from trigger.train.cluster.gstream.gstream import GStream
from matplotlib import pyplot as plt 

import pprint
import numpy as np
import pickle as pk

with open('examples/g_stream/for_g_stream', 'rb') as f:

    stream = pk.load(f)

np_stream = [np.array([data[0], data[1]]) for data in stream]

X = [ data[0] for data in np_stream ]
Y = [ data[1] for data in np_stream ]

plt.plot(X, Y, 'or')

gstream = GStream(vector_size=2, alpha1=0.05, alpha2=0.0006, beta=200, error_decrease=0.95)

for i in range(0, len(np_stream), 300):

    mini_stream = np_stream[i:i+300]

    gstream.got_data(mini_stream)

centers = [node.protype for node in gstream.graph.nodes]

X_g = [ data[0] for data in centers ]
Y_g = [ data[1] for data in centers ]

plt.plot(X_g, Y_g, 'ob')
plt.show()
# from trigger.models.opening import Opening
# from trigger.models.softskill import Softskill
# from trigger.models.hardskill import Hardskill
# from trigger.models.language import Language
# from trigger.models.user import User
# from trigger.recommend import smart
# from trigger.recommend.controller import Controller
# from trigger.recommend.clusters import Clusters
# from trigger.recommend.opening_transformer import OpeningTransformer
# from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

from trigger.train.cluster.ecm.ecm import ECM
from matplotlib import pyplot as plt

import pprint
import numpy as np
import pickle as pk

with open('examples/2D_points/0', 'rb') as f:

    stream = pk.load(f)

np_stream = [np.array([data[0], data[1]]) for data in stream]

X = [data[0] for data in np_stream]
Y = [data[1] for data in np_stream]

print(len(X))

gstream = ECM(distance_threshold=100)

for i, v in enumerate(np_stream):
    gstream.add(v)
    # print(i, v, len(gstream.clusters))

# If there are some reds, this means we didn't put them in a cluster, which *SHOULDN'T* happen
plt.scatter(X, Y, c='red', edgecolors='black', marker='o')

colors = ['#6b6b6b', '#ff2994', '#b3b3b3', '#ffd1e8',
          '#6b00bd', '#0000f0', '#c880ff', '#8080ff',
          '#005757', '#00b300', '#00b3b3', '#005700',
          '#ada800', '#bd7b00', '#fff957', '#ff974d',
          '#ff4d4d']

for i, cluster in enumerate(sorted(gstream.clusters, key=lambda cluster: cluster.center[0])):

    color = colors[i % len(colors)]

    position = (cluster.center[0], cluster.center[1])

    # circle = plt.Circle(position, cluster.radius,
    #                     color=color, fill=False, linestyle="--")

    # plt.gcf().gca().add_artist(circle)

    plt.scatter(position[0], position[1], c=color,
                edgecolors='black', marker='D', linewidths=2)

    _X = []
    _Y = []

    for instance in cluster.instances:
        _X.append(instance[0])
        _Y.append(instance[1])

    # plt.plot(_X, _Y, linestyle="None", marker='o', color=color)
    plt.scatter(_X, _Y, c=color, edgecolors='black')


plt.show()

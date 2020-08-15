from typing import Any, List, NamedTuple

from trigger.train.cluster.ecm.ecm import ECM
from matplotlib import pyplot as plt
from sklearn.metrics.cluster import adjusted_rand_score

import numpy as np
import pickle as pk
import json
import os


class TestCase(NamedTuple):
    path_or_name: str
    inputs: List[Any]
    correct: List[Any]


def read_pkl(input_path: str) -> TestCase:
    with open(input_path, 'rb') as f:
        stream = pk.load(f)

    return TestCase(
        path_or_name=input_path,
        inputs=[np.array([data[0], data[1]]) for data in stream],
        correct=[data[2] for data in stream]
    )


def test_2d(ecm: ECM, case: TestCase, should_do_plot: bool = True, want_to_know_clusters: bool = False) -> object:
    X = [data[0] for data in case.inputs]
    Y = [data[1] for data in case.inputs]

    for v in case.inputs:
        ecm.add(v)

    if should_do_plot:
        # If there are some reds, this means we didn't put them in a cluster, which *SHOULDN'T* happen
        plt.scatter(X, Y, c='red', edgecolors='black', marker='o')

        colors = ['#6b6b6b', '#ff2994', '#b3b3b3', '#ffd1e8',
                  '#6b00bd', '#0000f0', '#c880ff', '#8080ff',
                  '#005757', '#00b300', '#00b3b3', '#005700',
                  '#ada800', '#bd7b00', '#fff957', '#ff974d',
                  '#ff4d4d']

        for i, cluster in enumerate(sorted(ecm.clusters, key=lambda cluster: cluster.center[0])):
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

            plt.scatter(_X, _Y, c=color, edgecolors='black')

        plt.show()

    predicted = [ecm.index_of_cluster_containing(
        instance) for instance in case.inputs]

    results = {
        "used algorithm": ecm.describe(),
        "test": case.path_or_name,
        "clusters": [
            {
                "#": i,
                "center": cluster.center.tolist(),
                "radius": cluster.radius,
                "instances": [instance.tolist() for instance in cluster.instances]
            } for i, cluster in enumerate(ecm.clusters)
        ] if want_to_know_clusters else [],
        "scores": {
            "sklearn.metrics.cluster.adjusted_rand_score": adjusted_rand_score(case.correct, predicted),
        }

    }

    return results


def save_results(results: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as outfile:
        json.dump(results, outfile)


if __name__ == "__main__":
    case = read_pkl("examples/2D_points/0")
    ecm = ECM(distance_threshold=10)
    results = test_2d(ecm, case, False)
    save_results(results, "examples/2D_points_results/0.json")

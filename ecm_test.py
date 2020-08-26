from typing import Any, List, Tuple

from trigger.train.cluster.ecm.ecm import ECM
from matplotlib import pyplot as plt
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics import silhouette_score, calinski_harabasz_score

import numpy as np
import pickle as pk
import json
import os

import time


def read_pkl(input_path: str) -> Tuple[List, List]:
    with open(input_path, 'rb') as f:
        stream = pk.load(f)

    return [np.array([data[0], data[1]]) for data in stream], [data[2] for data in stream]


def test_2d_with_labels(ecm: ECM,
                        inputs: List[Any],
                        correct: List[Any],
                        name: str,
                        description: str,
                        path: str,
                        plot_name: str,
                        should_do_plot: bool = True,
                        want_to_know_clusters: bool = False,
                        want_to_know_inputs_and_correct: bool = False) -> object:
    X = [data[0] for data in inputs]
    Y = [data[1] for data in inputs]

    tic = time.perf_counter()

    for v in inputs:
        ecm.add(v)

    toc = time.perf_counter()

    time_to_add = f"{toc - tic:0.4f} seconds"

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

            _X = []
            _Y = []

            for instance in cluster.instances:
                _X.append(instance[0])
                _Y.append(instance[1])

            plt.scatter(_X, _Y, c=color, edgecolors='black')
            plt.scatter(position[0], position[1], c=color,
                        edgecolors='black', marker='D', linewidths=2)

        plt.show()
        plt.savefig(plot_name)

    tic = time.perf_counter()

    predicted = [ecm.index_of_cluster_containing(
        instance) for instance in inputs]

    toc = time.perf_counter()

    time_to_predict = f"{toc - tic:0.4f} seconds"

    results = {
        "used algorithm": ecm.describe(),
        "test": {
            "name": name,
            "path": path,
            "description": description,
            "inputs": inputs if want_to_know_inputs_and_correct else [],
            "correct": correct if want_to_know_inputs_and_correct else [],
        },
        "time to add": time_to_add,
        "time to predict": time_to_predict,
        "clusters": [
            {
                "#": i,
                "center": cluster.center.tolist(),
                "radius": cluster.radius,
                "instances": [instance.tolist() for instance in cluster.instances]
            } for i, cluster in enumerate(ecm.clusters)
        ] if want_to_know_clusters else [],
        "scores": {
            "sklearn.metrics.cluster.adjusted_rand_score": adjusted_rand_score(correct, predicted),
            "sklearn.metrics.silhouette_score": silhouette_score(inputs, predicted),
            "sklearn.metrics.calinski_harabasz_score": calinski_harabasz_score(inputs, predicted),
        },
        "figure": plot_name if should_do_plot else "",

    }

    return results


def save_results(results: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as outfile:
        # TODO indent=4 is just so it's easier to see, not needed!
        json.dump(results, outfile, indent=4)


def compute_filename(base: str,
                     ecm: ECM,
                     name: str,
                     version: str = "",
                     override: bool = False) -> str:

    algorithm = ecm.describe()

    algorithm_name = algorithm["name"] + version
    algorithm_parameters = algorithm["parameters"]

    algorithm_parameters_parts = [
        f"{param_name}={param_value}" for param_name, param_value in algorithm_parameters.items()
    ]

    wanted = f"{name} ; {algorithm_name} = {';'.join(algorithm_parameters_parts)}"
    proposed = wanted

    if not override:
        extra = 0
        while os.path.exists(f"{base}/{proposed}.json"):
            proposed = wanted + f"_{extra}"
            extra += 1

    return proposed


if __name__ == "__main__":

    dts = [1000, 100, 10, 250]

    cases = [("examples/2D_points/0", "0",
              "20 2D points with true labels; Generated by util/2dgenerator_with_true")]

    base = "results/2D/ecm"

    for filepath, name, description in cases:

        print("\nDoing test ", filepath)

        for dt in dts:

            print("\tWith dt =", dt)

            ecm = ECM(distance_threshold=dt)

            inputs, correct = read_pkl(filepath)

            filename = compute_filename(base, ecm, name, " v2", True)

            results = test_2d_with_labels(
                ecm,
                inputs,
                correct,
                name,
                description,
                filepath,
                f"{base}/{filename}.png",
                should_do_plot=True,
                want_to_know_clusters=False,
                want_to_know_inputs_and_correct=False,
            )

            save_results(results, f"{base}/{filename}.json")

            print("\tResults: ", results['scores'])

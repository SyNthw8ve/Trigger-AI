import time
import os
import json
import pickle as pk
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score

import matplotlib

from matplotlib import pyplot as plt
from typing import Any, List, Tuple, Union
import typing
from util.stream.stream_processor import StreamProcessor

from trigger.train.cluster.ecm.ecm import ECM


def read_pkl(input_path: str) -> Tuple[List, List]:
    with open(input_path, 'rb') as f:
        stream = pk.load(f)

    return [np.array([data[0], data[1]]) for data in stream], [data[2] for data in stream]


def construct_results(ecm: ECM,
                      inputs: List[Any],
                      correct: Union[List[Any], None],
                      predicted: List[Any],
                      time_to_add: str,
                      time_to_predict: str,
                      path: str,
                      name: str,
                      description: str,
                      plot_name: str,
                      should_do_plot,
                      want_to_know_clusters,
                      want_to_know_inputs_and_correct) -> object:

    return {
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
            "sklearn.metrics.cluster.adjusted_rand_score": adjusted_rand_score(correct, predicted) if correct is not None else "-",
            "sklearn.metrics.silhouette_score": str(silhouette_score(inputs, predicted)),
            "sklearn.metrics.calinski_harabasz_score": calinski_harabasz_score(inputs, predicted),
        },
        "figure": plot_name if should_do_plot else "",
    }


def plot(ecm: ECM, do_radius: bool = False) -> None:

    print("Plotting")

    colors = ['#6b6b6b', '#ff2994', '#ffd1e8',
              '#6b00bd', '#0000f0', '#c880ff', '#8080ff',
              '#005757', '#00b300', '#00b3b3', '#005700',
              '#ada800', '#bd7b00', '#fff957', '#ff974d',
              '#ff4d4d']

    sorted_by_x = sorted(ecm.clusters, key=lambda cluster: cluster.center[0])
    
    _X = []
    _Y = []
    _colors = []
    _X_positions = []
    _Y_positions = []
    _colors_positions = []

    for cluster in sorted_by_x:

        color = colors[cluster.index % len(colors)]

        for instance in cluster.instances:
            _X.append(instance[0])
            _Y.append(instance[1])
            _colors.append(color)

        _colors_positions.append(color)
        _X_positions.append(cluster.center[0])
        _Y_positions.append(cluster.center[1])

    plt.scatter(_X, _Y, c=_colors, edgecolors='black')

    plt.scatter(_X_positions, _Y_positions, c=_colors_positions,
                    edgecolors='black', marker='D', linewidths=2)


def test_2d_with_labels(ecm: ECM,
                        inputs: List[Any],
                        correct: List[Any],
                        name: str,
                        description: str,
                        path: str,
                        plot_name: str,
                        should_do_plot: bool = False,
                        want_to_know_clusters: bool = False,
                        want_to_know_inputs_and_correct: bool = False) -> object:
    time_to_add = 0

    animate = False

    if animate and should_do_plot:
        plt.ion()

    for v in inputs:
        tic = time.perf_counter()
        ecm.add(v)
        toc = time.perf_counter()
        time_to_add += toc - tic

        if animate and should_do_plot:
            plot(ecm)
            plt.draw()
            while not plt.waitforbuttonpress():
                pass
            plt.clf()

    print("Δt", ecm.faiss_t)

    time_to_add = f"{time_to_add:0.4f} seconds"

    if should_do_plot:
        plot(ecm)
        figure = plt.gcf()
        figure.set_size_inches(19, 9, forward=True)
        plt.savefig(plot_name, dpi=100)
        plt.show()

    tic = time.perf_counter()

    predicted = [ecm.index_of_cluster_containing(
        instance) for instance in inputs]

    toc = time.perf_counter()

    time_to_predict = f"{toc - tic:0.4f} seconds"

    return construct_results(
        ecm,
        inputs,
        correct,
        predicted,
        time_to_add,
        time_to_predict,
        path,
        name,
        description,
        plot_name,
        should_do_plot,
        want_to_know_clusters,
        want_to_know_inputs_and_correct
    )


def test_2d_stream(stream_processor: StreamProcessor,
                   name: str,
                   description: str,
                   test_filepath: str,
                   plot_filepath: str,
                   apply_delay: bool,
                   should_do_plot: bool = False,
                   want_to_know_clusters: bool = False,
                   want_to_know_inputs_and_correct: bool = False):

    if not apply_delay:
        tic = time.perf_counter()

    stream_processor.process(apply_delay)

    if not apply_delay:
        toc = time.perf_counter()
        time_to_add = f"{toc - tic:0.4f} seconds"
    else:
        time_to_add = "-"

    if should_do_plot:
        figure = plt.gcf()
        figure.set_size_inches(19, 9, forward=True)
        plot(stream_processor.processor)
        plt.savefig(plot_filepath, dpi=100)
        # plt.show()
        plt.clf()

    tic = time.perf_counter()

    inputs = [instance[0] for instance in stream_processor.instances]

    predicted = [typing.cast(ECM, stream_processor.processor).index_of_cluster_containing(
        _input) for _input in inputs]

    toc = time.perf_counter()

    time_to_predict = f"{toc - tic:0.4f} seconds"

    return construct_results(
        typing.cast(ECM, stream_processor.processor),
        inputs,
        None,
        predicted,
        time_to_add,
        time_to_predict,
        test_filepath,
        name,
        description,
        plot_filepath,
        should_do_plot,
        want_to_know_clusters,
        want_to_know_inputs_and_correct
    )


def save_results(results: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as outfile:
        # TODO indent=4 is just so it's easier to see, not needed!
        json.dump(results, outfile, indent=4)


def compute_filename(ecm: ECM,
                     name: str,
                     version: str = "") -> str:

    algorithm = ecm.describe()

    algorithm_name = algorithm["name"] + version
    algorithm_parameters = algorithm["parameters"]

    algorithm_parameters_parts = [
        f"{param_name}={param_value}" for param_name, param_value in algorithm_parameters.items()
    ]

    return f"{name} ; {algorithm_name} = {';'.join(algorithm_parameters_parts)}"


if __name__ == "__main__":

    dts = [2000, 2500, 7500, 12000, 12500]

    cases = [
        # ("examples/2D_points/0", "0",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
        # ("examples/2D_points/1", "1",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
        # ("examples/2D_points/2", "2",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
    ]

    base = "results/2D/ecm"

    for filepath, name, description in cases:

        print("\nDoing test ", filepath)

        for dt in dts:

            print("\tWith dt =", dt)

            ecm = ECM(distance_threshold=dt, dimensions=2)

            inputs, correct = read_pkl(filepath)

            # np.random.shuffle(inputs)

            filename = compute_filename(ecm, name, " v4")

            results = test_2d_with_labels(
                ecm,
                inputs,
                correct,
                name,
                description,
                filepath,
                f"{base}/{filename}.jpg",
                should_do_plot=False,
                want_to_know_clusters=False,
                want_to_know_inputs_and_correct=False,
            )

            save_results(results, f"{base}/{filename}.json")

            print("\tResults: ", results['scores'])

    with open('./examples/2D_stream/1_r', 'rb') as f:
        stream = pk.load(f)

    with open('./examples/2D_stream/2_r', 'rb') as f:
        stream2 = pk.load(f)

    base = "results/2D_stream/ecm"

    for dt in dts:
        ecm = ECM(dt, 2)
        stream_processor = StreamProcessor(processor=ecm, instances=stream)

        print("Doing stream 1")

        name = "1_r"

        filename = compute_filename(ecm, name, " v4")

        results = test_2d_stream(
            stream_processor,
            name,
            "",
            './examples/2D_stream/1_r',
            f"{base}/{filename}.jpg",
            apply_delay=False,
            should_do_plot=True,
            want_to_know_clusters=False,
            want_to_know_inputs_and_correct=False
        )

        save_results(results, f"{base}/{filename}.json")

        print("\tResults: ", results['scores'])

        name = "1_r + 2_r"

        filename = compute_filename(ecm, name, " v4")

        print("Doing stream 2")

        stream_processor = StreamProcessor(processor=ecm, instances=stream2)

        results = test_2d_stream(
            stream_processor,
            name,
            "",
            './examples/2D_stream/2_r',
            f"{base}/{filename}.jpg",
            apply_delay=False,
            should_do_plot=True,
            want_to_know_clusters=False,
            want_to_know_inputs_and_correct=False
        )

        save_results(results, f"{base}/{filename}.json")

        print("\tResults: ", results['scores'])

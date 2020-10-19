from os import system
import time
import os
import json
import pickle as pk
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score

from matplotlib import pyplot as plt
from typing import Any, List, Tuple, Union
import typing
from util.stream.stream_processor import StreamProcessor

from trigger.train.cluster.birch.birch import Birch
from matplotlib.colors import ListedColormap


def read_pkl(input_path: str) -> Tuple[List, List]:
    with open(input_path, 'rb') as f:
        stream = pk.load(f)

    return [np.array([data[0], data[1]]) for data in stream], [data[2] for data in stream]


def construct_results(birch: Birch,
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
        "used algorithm": birch.describe(),
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
                "center": center,
            } for i, center in zip(birch.model.subcluster_centers_, birch.model.subcluster_labels_)
        ] if want_to_know_clusters else [],
        "scores": {
            "sklearn.metrics.cluster.adjusted_rand_score": adjusted_rand_score(correct, predicted) if correct is not None else "-",
            "sklearn.metrics.silhouette_score": str(silhouette_score(inputs, predicted)),
            "sklearn.metrics.calinski_harabasz_score": calinski_harabasz_score(inputs, predicted),
        },
        "figure": plot_name if should_do_plot else "",
    }


def plot(birch: Birch, do_radius: bool = False) -> None:

    print("Plotting")

    colors = ['#6b6b6b', '#ff2994', '#ffd1e8',
              '#6b00bd', '#0000f0', '#c880ff', '#8080ff',
              '#005757', '#00b300', '#00b3b3', '#005700',
              '#ada800', '#bd7b00', '#fff957', '#ff974d',
              '#ff4d4d']

    cluster_labels = birch.model.subcluster_labels_

    _X = []
    _Y = []
    _labels = []

    _X_center = []
    _Y_center = []
    _labels_center = []

    sorted_by_x = sorted(zip(birch.model.subcluster_centers_,
                             cluster_labels), key=lambda t: t[0][0] ** 2 + t[0][1])

    for instance in birch.instances:
        _X.append(instance[0])
        _Y.append(instance[1])
        label = birch.index_of_cluster_containing(instance)
        _labels.append(label)

    labels_to_color_index = {}

    for center, label in sorted_by_x:
        _X_center.append(center[0])
        _Y_center.append(center[1])
        _labels_center.append(label)
        labels_to_color_index[label] = len(labels_to_color_index) % len(colors)

    _color_indexes = [labels_to_color_index[label] for label in _labels]
    _color_indexes_center = [labels_to_color_index[label]
                             for label in _labels_center]

    cmap = ListedColormap(colors=colors)

    plt.scatter(_X, _Y, c=_color_indexes, cmap=cmap, edgecolors='black')

    plt.scatter(_X_center, _Y_center, c=_color_indexes_center, cmap=cmap,
                edgecolors='black', marker='D', linewidths=2)


def test_2d_with_labels(birch: Birch,
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
        birch.add(v)
        toc = time.perf_counter()
        time_to_add += toc - tic

        if animate and should_do_plot:
            plot(birch)
            plt.draw()
            while not plt.waitforbuttonpress():
                pass
            plt.clf()

    time_to_add = f"{time_to_add:0.4f} seconds"

    print("Δt", time_to_add)

    if should_do_plot:
        plot(birch)
        figure = plt.gcf()
        figure.set_size_inches(19, 9, forward=True)
        plt.savefig(plot_name, dpi=100)
        plt.show()

    tic = time.perf_counter()

    predicted = [birch.index_of_cluster_containing(
        instance) for instance in inputs]

    toc = time.perf_counter()

    time_to_predict = f"{toc - tic:0.4f} seconds"

    return construct_results(
        birch,
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
                   want_to_know_inputs_and_correct: bool = False,
                   do_offline=True):

    if not apply_delay:
        tic = time.perf_counter()

    stream_processor.process(apply_delay)
    
    if do_offline:
        birch.offline()

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

    predicted = [typing.cast(birch, stream_processor.processor).index_of_cluster_containing(
        _input) for _input in inputs]

    toc = time.perf_counter()

    time_to_predict = f"{toc - tic:0.4f} seconds"

    return construct_results(
        typing.cast(birch, stream_processor.processor),
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
        from util.json_util.json_converter import EnhancedJSONEncoder
        json.dump(results, outfile, indent=4, cls=EnhancedJSONEncoder)


def compute_filename(birch: Birch,
                     name: str,
                     version: str = "") -> str:

    algorithm = birch.describe()

    algorithm_name = algorithm["name"] + version
    algorithm_parameters = algorithm["parameters"]

    algorithm_parameters_parts = [
        f"{param_name}={param_value}" for param_name, param_value in algorithm_parameters.items()
    ]

    return f"{name} ; {algorithm_name} = {';'.join(algorithm_parameters_parts)}"


if __name__ == "__main__":

    dts = [12000, 15000, 20000, 25000, 30000, 45000, 50000]

    cases = [
        # ("examples/2D_points/0", "0",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
        # ("examples/2D_points/1", "1",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
        # ("examples/2D_points/2", "2",
        #  "2D points with true labels; Generated by util/2dgenerator_with_true"),
    ]

    base = "results/2D/birch"

    # birch = Birch()

    # name = "test"

    # filename = compute_filename(birch, name)

    # description = ""

    # inputs = [
    #     np.array([1, 2]),
    #     np.array([2, 2]),
    #     np.array([5, 5]),
    #     np.array([3, 3]),
    #     np.array([19, 2]),
    #     np.array([17, 2]),
    # ]

    # for v in inputs:
    #     birch.add(v)
    #     print(birch.model.root_)
    #     print(birch.model.dummy_leaf_)
    #     print(birch.model.subcluster_centers_)
    #     print(birch.model.subcluster_labels_)
    #     print(birch.model.labels_)

    # exit(0)

    for filepath, name, description in cases:

        base = "results/2D/birch"

        print("\nDoing test ", filepath)

        for dt in dts:

            birch = Birch(threshold=dt)

            inputs, correct = read_pkl(filepath)

            # np.random.shuffle(inputs)

            filename = compute_filename(birch, name)

            results = test_2d_with_labels(
                birch,
                inputs,
                correct,
                name,
                description,
                filepath,
                f"{base}/{filename}.svg",
                should_do_plot=True,
                want_to_know_clusters=False,
                want_to_know_inputs_and_correct=False,
            )

            save_results(results, f"{base}/{filename}.json")

            print("\tResults: ", results['scores'])

    with open('./examples/2D_stream/1_r', 'rb') as f:
        stream = pk.load(f)

    with open('./examples/2D_stream/2_r', 'rb') as f:
        stream2 = pk.load(f)

    base = "results/2D_stream/birch"

    for dt in dts:
        birch = Birch(dt)
        stream_processor = StreamProcessor(processor=birch, instances=stream)

        print("Doing stream 1")

        name = "1_r"

        filename = compute_filename(birch, name, "")

        results = test_2d_stream(
            stream_processor,
            name,
            "",
            './examples/2D_stream/1_r',
            f"{base}/{filename}.svg",
            apply_delay=False,
            should_do_plot=True,
            want_to_know_clusters=False,
            want_to_know_inputs_and_correct=False,
            do_offline=False,
        )

        save_results(results, f"{base}/{filename}.json")

        print("\tResults: ", results['scores'])

        name = "1_r + 2_r"

        filename = compute_filename(birch, name, "")

        print("Doing stream 2")

        stream_processor = StreamProcessor(processor=birch, instances=stream2)

        results = test_2d_stream(
            stream_processor,
            name,
            "",
            './examples/2D_stream/2_r',
            f"{base}/{filename}.svg",
            apply_delay=False,
            should_do_plot=True,
            want_to_know_clusters=False,
            want_to_know_inputs_and_correct=False,
            do_offline=False,
        )

        save_results(results, f"{base}/{filename}.json")

        print("\tResults: ", results['scores'])

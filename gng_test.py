from matplotlib import pyplot as plt
from trigger.train.cluster.gstream.gstream import GNG
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score
from typing import Tuple, List
from util.stream.stream_processor import StreamProcessor
from util.stream.stream_generator import StreamGeneratorUniformDelay, StreamGeneratorRandomDelay
import pprint
import numpy as np
import pickle as pk
import logging
import json

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)


def get_stream(stream_generator, path, new_stream=False, num_items=100):

    stream = []

    if new_stream:

        stream = stream_generator.generate_stream(num_items=num_items)
        stream_generator.save_stream(path)

    else:

        with open(path, 'rb') as f:

            stream = pk.load(f)

    return stream

def get_test_name(base_name, gng: GNG) -> str:

    algorithm = gng.describe()

    algorithm_name = algorithm["name"]
    algorithm_parameters = algorithm["parameters"]

    algorithm_parameters_parts = [
        f"{param_name}={param_value}" for param_name, param_value in algorithm_parameters.items()
    ]

    return f"{base_name} ; {algorithm_name} = {';'.join(algorithm_parameters_parts)}"

def test_gng(streams: List, gng: GNG, results_path: str,
             apply_offline: bool, test_name: str):

    for stream in streams:

        stream_processor = StreamProcessor(processor=gng, instances=stream)
        stream_processor.process(apply_delay=True)

        if apply_offline:

            gng.offline_fase()

    final_name = '/' + get_test_name(test_name, gng)

    gng.plot2D(results_path + final_name + '.png')

    silhouette_score, calinski_harabasz_score = eval_cluster(gng)

    results = {

        "used_algorithm": gng.describe(),
        "test": {
            "name": test_name,
            "path": "./examples/2D_stream/1_r",
            "description": "",
            "inputs": [],
            "correct": []
        },
        "time to add": "-",
        "time to predict": "-",
        "clusters": [],
        "scores": {
            "sklearn.metrics.cluster.adjusted_rand_score": "-",
            "sklearn.metrics.silhouette_score": str(silhouette_score),
            "sklearn.metrics.calinski_harabasz_score": str(calinski_harabasz_score)
        },
        "plot_path": results_path
    }

    with open(results_path + final_name + '.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)

def eval_cluster(gng: GNG) -> Tuple[float, float]:

    X = gng.instances
    labels = []

    for x in X:

        labels.append(gng.get_cluster(x))

    return (silhouette_score(X, labels), calinski_harabasz_score(X, labels))


def test_generator(epsilon_b, epsilon_n, lam, beta, alpha, max_age, off_max_age,
                   lambda_2, dimensions, nodes_per_cycle):

    param_map = {
        "epsilon_b": epsilon_b,
        "epsilon_n": epsilon_n,
        "lam": lam,
        "beta": beta,
        "alpha": alpha,
        "max_age": max_age,
        "off_max_age": off_max_age,
        "time_decay": lambda_2,
        "nodes_per_cycle": nodes_per_cycle
    },

    return [
        {
            "results": './results/2D_stream/gstream/on',
            "name": '1_r',
            "offline": False,
            "param_map": param_map,
            'streams': [stream]
        },
        {
            "results": './results/2D_stream/gstream/on_off',
            "name": '1_r',
            "offline": True,
            "param_map": param_map,
            'streams': [stream]
        },
        {
            "results": './results/2D_stream/gstream/on',
            "name": '1_2_r',
            "offline": False,
            "param_map": param_map,
            'streams': [stream, stream_2]
        },
        {
            "results": './results/2D_stream/gstream/on_off',
            "name": '1_2_r',
            "offline": True,
            "param_map": param_map,
            'streams': [stream, stream_2]
        }
    ]


if __name__ == "__main__":

    stream_generator = StreamGeneratorRandomDelay(
        max_delay=0.005, min_delay=0.001, stream_values_interval=100000, dimensions=2)

    stream = get_stream(
        stream_generator, './examples/2D_stream/1_r', new_stream=False, num_items=500)
    stream_2 = get_stream(
        stream_generator, './examples/2D_stream/2_r', new_stream=False, num_items=500)

    param_maps = [
        {
            "epsilon_b": 0.001,
            "epsilon_n": 0,
            "lam": 200,
            "beta": 0.9995,
            "alpha": 0.95,
            "max_age": 200,
            "off_max_age": 200,
            "time_decay": 0.2,
            "nodes_per_cycle": 1
        },
        {
            "epsilon_b": 0.01,
            "epsilon_n": 0,
            "lam": 200,
            "beta": 0.9995,
            "alpha": 0.95,
            "max_age": 100,
            "off_max_age": 100,
            "time_decay": 0.2,
            "nodes_per_cycle": 3
        },
        {
            "epsilon_b": 0.1,
            "epsilon_n": 0,
            "lam": 100,
            "beta": 0.9995,
            "alpha": 0.95,
            "max_age": 100,
            "off_max_age": 100,
            "time_decay": 0.2,
            "nodes_per_cycle": 3
        },
        {
            "epsilon_b": 0.001,
            "epsilon_n": 0,
            "lam": 200,
            "beta": 0.9995,
            "alpha": 0.95,
            "max_age": 200,
            "off_max_age": 200,
            "time_decay": 0.2,
            "nodes_per_cycle": 5
        },
        {
            "epsilon_b": 0.01,
            "epsilon_n": 0,
            "lam": 200,
            "beta": 0.9995,
            "alpha": 0.95,
            "max_age": 100,
            "off_max_age": 100,
            "time_decay": 0.4,
            "nodes_per_cycle": 3
        },
    ]


    tests_sets = []

    for param_map in param_maps:

        tests_sets.append(test_generator(
            epsilon_b=param_map['epsilon_b'],
            epsilon_n=param_map['epsilon_n'],
            lam=param_map['lam'],
            beta=param_map['beta'],
            alpha=param_map['alpha'],
            max_age=param_map['max_age'],
            off_max_age=param_map['off_max_age'],
            lambda_2=param_map['time_decay'],
            dimensions=2,
            nodes_per_cycle=param_map['nodes_per_cycle']
        ))

    for test_set in tests_sets:

        for test in test_set:

            param_map = test['param_map'][0]

            gng = GNG(epsilon_b=param_map['epsilon_b'],
                      epsilon_n=param_map['epsilon_n'],
                      lam=param_map['lam'],
                      beta=param_map['beta'],
                      alpha=param_map['alpha'],
                      max_age=param_map['max_age'],
                      off_max_age=param_map['off_max_age'],
                      lambda_2=param_map['time_decay'],
                      dimensions=2,
                      nodes_per_cycle=param_map['nodes_per_cycle'])

            test_gng(test['streams'], gng, test['results'],
                     test['offline'], test['name'])

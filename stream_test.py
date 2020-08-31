import pprint
import numpy as np
import pickle as pk
import logging

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

from util.stream.stream_generator import StreamGeneratorUniformDelay, StreamGeneratorRandomDelay
from util.stream.stream_processor import StreamProcessor

from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics import silhouette_score, calinski_harabasz_score

from trigger.train.cluster.gstream.gstream import GNG
from trigger.train.cluster.ecm.ecm import ECM
from util.stream.processor import Processor

from matplotlib import pyplot as plt 

def get_stream(stream_generator, path, new_stream=False, num_items=100):

    stream = []

    if new_stream:

        stream = stream_generator.generate_stream(num_items=num_items)
        stream_generator.save_stream(path)

    else:

        with open(path, 'rb') as f:

            stream = pk.load(f)

    return stream

def eval_cluster(algo, fase: str):

    X = algo.instances
    labels = []

    for x in X:

        labels.append(algo.get_cluster(x))

    print(fase, "Silhouette Score: ", silhouette_score(X, labels))

if __name__ == "__main__":
    
    path = './results/3D/'

    stream_generator = StreamGeneratorRandomDelay(max_delay=0.005, min_delay=0.001, stream_values_interval=1000000, dimensions=2)

    stream = get_stream(stream_generator, './examples/2D_stream/1_r_big', new_stream=False, num_items=10000)

    gng = GNG(epsilon_b=0.1, epsilon_n=0, lam=400, beta=0.9995, 
                alpha=0.95, max_age=100, off_max_age=100, aging='time', lambda_2=0.2, 
                dimensions=2, nodes_per_cycle=3)

    stream_processor = StreamProcessor(processor=gng, instances=stream)
    stream_processor.process(apply_delay=True)

    eval_cluster(gng, "Online 1")

    gng.offline_fase()
    eval_cluster(gng, "Offline 1")

    stream_2 = get_stream(stream_generator, './examples/2D_stream/2_r_big', new_stream=False, num_items=10000)

    stream_processor_2 = StreamProcessor(processor=gng, instances=stream_2)
    stream_processor_2.process(apply_delay=True)

    eval_cluster(gng, "Online 2")

    gng.offline_fase()
    eval_cluster(gng, "Offline 2")
   
    """ path = './results/ecm/'

    stream_generator = StreamGeneratorRandomDelay(max_delay=0.005, min_delay=0.001, stream_values_interval=100000, dimensions=2)

    stream = get_stream(stream_generator, './examples/2D_stream/1_r_big', new_stream=False, num_items=10000)

    ecm = ECM(distance_threshold=1000000)

    stream_processor = StreamProcessor(processor=ecm, instances=stream)
    stream_processor.process(apply_delay=False)

    eval_cluster(ecm, "Online 1")

    stream_2 = get_stream(stream_generator, './examples/2D_stream/2_r_big', new_stream=False, num_items=10000)

    stream_processor_2 = StreamProcessor(processor=ecm, instances=stream_2)
    stream_processor_2.process(apply_delay=False)

    eval_cluster(ecm, "Online 2") """
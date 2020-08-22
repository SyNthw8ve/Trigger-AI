import pprint
import numpy as np
import pickle as pk
import logging

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

from util.stream.stream_generator import StreamGeneratorUniformDelay
from util.stream.stream_processor import StreamProcessor

from sklearn.metrics.cluster import adjusted_rand_score

from trigger.train.cluster.gstream.gstream import GNG
from matplotlib import pyplot as plt 

def get_stream(delay, values, path, new_stream=False):

    stream = []

    if new_stream:

        stream_generator = StreamGeneratorUniformDelay(delay=delay, stream_values_interval=values)

        stream = stream_generator.generate_stream(num_items=10000)
        stream_generator.save_stream(path)

    else:

        with open(path, 'rb') as f:

            stream = pk.load(f)

    return stream

if __name__ == "__main__":
    
    stream = get_stream(0.005, 10000, './examples/2D_stream/1', new_stream=False)

    gng = GNG(epsilon_b=0.05, epsilon_n=0, lam=300, beta=0.9995, 
                alpha=0.95, max_age=350, aging='time', lambda_2=0.2, 
                dimensions=2, nodes_per_cycle=3)

    stream_processor = StreamProcessor(processor=gng, instances=stream)

    stream_processor.process(apply_delay=True)

    gng.plot(path='./results/1_time_3_node.png')

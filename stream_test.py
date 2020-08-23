import pprint
import numpy as np
import pickle as pk
import logging

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

from util.stream.stream_generator import StreamGeneratorUniformDelay, StreamGeneratorRandomDelay
from util.stream.stream_processor import StreamProcessor

from sklearn.metrics.cluster import adjusted_rand_score

from trigger.train.cluster.gstream.gstream import GNG
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

if __name__ == "__main__":
    
    path = './results/3D/'

    stream_generator = StreamGeneratorRandomDelay(max_delay=0.005, min_delay=0.001, stream_values_interval=100000, dimensions=3)

    stream = get_stream(stream_generator, './examples/2D_stream/1_r_3d', new_stream=True, num_items=500)

    gng = GNG(epsilon_b=0.05, epsilon_n=0, lam=300, beta=0.9995, 
                alpha=0.95, max_age=100, off_max_age=100, aging='time', lambda_2=0.2, 
                dimensions=3, nodes_per_cycle=1)

    stream_processor = StreamProcessor(processor=gng, instances=stream)
    stream_processor.process(apply_delay=True)

    gng.plot3D(path=path + '1_r_time_1_node_on.png')

    gng.offline_fase()

    gng.plot3D(path=path + '1_r_time_1_node_off.png')

    stream_2 = get_stream(stream_generator, './examples/2D_stream/2_r_3d', new_stream=False, num_items=500)

    stream_processor_2 = StreamProcessor(processor=gng, instances=stream_2)
    stream_processor_2.process(apply_delay=False)

    gng.plot3D(path=path + '2_r_time_1_node_on.png')

    gng.offline_fase()
   
    gng.plot3D(path=path + '2_r_time_1_node_off.png')


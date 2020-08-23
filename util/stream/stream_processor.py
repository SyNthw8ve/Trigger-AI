import time
import numpy as np

from typing import List, Any

from util.stream.processor import Processor

class StreamProcessor():

    def __init__(self, processor: Processor, instances: List[Any]):

        self.processor = processor
        self.instances = instances

    def process(self, apply_delay=False):

        for instance in self.instances:

            np_instance = instance[0]
            
            self.processor.process(np_instance)

            if apply_delay:

                delay = instance[1]
                time.sleep(delay)

    
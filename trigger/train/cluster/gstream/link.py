import time
import numpy as np

from trigger.train.cluster.gstream.node import Node

class Link:

    def __init__(self, v: Node, u: Node, aging: str) -> None:

        self.age = 0
        self.v = v
        self.u = u
        self.aging = aging
        self.creation_time = None

        if aging == 'time':

            self.creation_time = time.time()


    def fade(self, lambda_2: float) -> None:

        if self.aging == 'counter':

            self.age += 1

        elif self.aging == 'time':

            curr_time = time.time()
            self.age = np.power(2, lambda_2*(curr_time - self.creation_time))

    def renew(self) -> None:

        self.age = 0
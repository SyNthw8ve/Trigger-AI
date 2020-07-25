from typing import List, Dict

import numpy

from trigger.models.softskill import Softskill


# This is probably only temporary!

class SoftskillTransformer:

    def __init__(self, all_softskills_names: List[str]):
        self.all_softskills_names = all_softskills_names

    def transform(self, softskills: List[Softskill]) -> numpy.array:
        out = []
        softskill_as_dict: Dict[str, int] = {softskill.name: softskill.score for softskill in softskills}
        for softskill_name in self.all_softskills_names:
            if softskill_name in softskill_as_dict:
                out.append(softskill_as_dict.get(softskill_name))
            else:
                out.append(0)
        return numpy.array(out)

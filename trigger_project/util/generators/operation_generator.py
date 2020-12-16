import random

from typing import List, cast

from ...instances.opening_instance import OpeningInstance
from ...operation import Operation, OperationType


class OperationGenerator:

    @staticmethod
    def random_from_openings_instances(opening_instances: List[OpeningInstance], n: int) -> List[Operation]:
        operations = []
        # TODO: A set is better suited?
        present_map = {
            opening.opening.entityId: False
            for opening in opening_instances
        }
        for _ in range(n):
            opening_instance = cast(OpeningInstance, random.choice(opening_instances))
            opening = opening_instance.opening
            tag = opening.entityId

            if present_map[tag]:
                op_type = cast(OperationType,
                               random.choice([OperationType.UPDATE_OPENING, OperationType.REMOVE_OPENING]))
                if op_type == OperationType.REMOVE_OPENING:
                    present_map[tag] = False
                elif op_type == OperationType.UPDATE_OPENING:
                    opening_instance = cast(OpeningInstance, random.choice(opening_instances))
                    opening_instance.opening.entityId = tag
            else:
                op_type = OperationType.NEW_OPENING
                present_map[tag] = True

            operations.append(
                Operation(
                    type=op_type,
                    opening_instance_tag=tag,
                    opening_instance=opening_instance
                )
            )

        return operations

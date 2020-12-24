from dataclasses import dataclass
from typing import List, Optional

import os


@dataclass
class OperationFile:
    """
    "avg"\n
    "0/avg"\n
    "data/operations_instances_ss_confirmed/0/avg"
    """
    layer: str
    test_subpath: str
    full_path: str

_BASE = "data/operations_instances_ss_confirmed"

def fetch_operations_files(sub_folders: Optional[List[str]] = None, layers: Optional[List[str]] = None) -> List[OperationFile]:
    collected: List[OperationFile]= []

    for folder_name in os.listdir(_BASE):
        if folder_name in ["__pycache__", "__init__.py"]:
            continue

        if sub_folders is not None and not folder_name in sub_folders:
            continue

        folder_path = os.path.join(_BASE, folder_name)

        for layer in os.listdir(folder_path):
            if layers is not None and layer not in layers:
                continue

            full_path = os.path.join(folder_path, layer)
            test_subpath = os.path.join(folder_name, layer)

            collected.append(OperationFile(layer, test_subpath, full_path))

    return collected
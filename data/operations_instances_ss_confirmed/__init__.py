from dataclasses import dataclass
from typing import List

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


def fetch_by_layer_name(*layers: str) -> List[OperationFile]:
    collected: List[OperationFile]= []

    for folder_name in os.listdir(_BASE):
        if folder_name.find("__pycache__") != -1:
            continue

        folder_path = os.path.join(_BASE, folder_name)

        for layer in os.listdir(folder_path):

            if not layer in layers:
                continue

            full_path = os.path.join(folder_path, layer)
            test_subpath = os.path.join(folder_name, layer)

            collected.append(OperationFile(layer, test_subpath, full_path))

    return collected

def fetch_by_subfolder(*sub_folders: str) -> List[OperationFile]:
    collected: List[OperationFile]= []

    for folder_name in os.listdir(_BASE):
        if folder_name.find("__pycache__") != -1:
            continue

        if not folder_name in sub_folders:
            continue

        folder_path = os.path.join(_BASE, folder_name)

        for layer in os.listdir(folder_path):
            if layer in sub_folders:
                full_path = os.path.join(folder_path, layer)
                test_subpath = os.path.join(folder_name, layer)

                collected.append(OperationFile(layer, test_subpath, full_path))

    return collected

def fetch_all() -> List[OperationFile]:
    collected: List[OperationFile]= []

    for folder_name in os.listdir(_BASE):
        if folder_name in ["__pycache__", "__init__.py"]:
            continue

        folder_path = os.path.join(_BASE, folder_name)

        for layer in os.listdir(folder_path):
            full_path = os.path.join(folder_path, layer)
            test_subpath = os.path.join(folder_name, layer)

            collected.append(OperationFile(layer, test_subpath, full_path))

    return collected

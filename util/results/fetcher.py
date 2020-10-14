import os
from typing import List


def get_result_paths_from_folder_and_sub_folders(directory_path: str,
                                                 contains: str) -> List[str]:
    path_list = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory_path)
        for filename in filenames
        if filename.endswith('.json')
    ]

    return [
        path
        for path in path_list
        if path.find(contains) != -1
    ]

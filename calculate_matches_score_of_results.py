import os
import json
from os import name
import statistics
import sys
from typing import Callable


def patch(matches_results):
    def average_from_distribution(distribution) -> float:
        return sum(int(number) * frequency
                   for number, frequency
                   in distribution.items()) / \
            sum(frequency
                for frequency
                in distribution.values())

    matches_results["avg #matches"] = average_from_distribution(
        matches_results["distribution #matches"])
    matches_results["avg #potential"] = average_from_distribution(
        matches_results["distribution #potential"])

    by_user = matches_results["by_user"]

    matches_results["avg matches score"] = statistics.mean(
        [user["avg matches"] for user in by_user])
    matches_results["avg real score"] = statistics.mean(
        [user["avg real"] for user in by_user])
    matches_results["avg similarity score"] = statistics.mean(
        [user["avg similarities"] for user in by_user])
    matches_results["avg quality score"] = statistics.mean(
        [user["avg qualities"] for user in by_user])

    # this reorders
    del matches_results["by_user"]
    matches_results["by_user"] = by_user

    return matches_results

def constrain(x: float, lower: float = 0., higher: float = 1.) -> float:
    return min(higher, max(x, lower))

def calculate_at_least_1_match_score(percentage: float) -> float:
    # * 100 so we take it to a different scale
    # **2 so each point makes more difference
    # /10000 to bring it back to the [0, 1] range
    return constrain((percentage * 100) ** 2 / 10000)

def calculate_avg_number_of_matches_score(avg: float) -> float:
    if avg < 1:
        return 0

    if avg < 2:
        return 0.5
    
    return 1.


def patch_folder_and_sub_folders(directory_path: str) -> None:
    path_list = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory_path)
        for filename in filenames
        if filename.endswith('.json')
    ]

    for path in path_list:
        try:
            with open(path, 'r') as file:
                json_as_dict = json.load(file)

                if json_as_dict.get("results", None) is None:
                    continue

                mr = json_as_dict["results"].get("matches_results", None)

                if mr is None:
                    continue

                mr = patch(mr)
                score_1 = 0.2 * calculate_at_least_1_match_score(mr[f"% at least 1 match"])
                score_2 = 0.1 * calculate_avg_number_of_matches_score(mr[f"avg #matches"])
                score_3 = 0.7 * mr[f"avg matches score"]

                json_as_dict["results"]["matches_results"] = {
                    "composite score": score_1 + score_2 + score_3,
                    **mr
                }

            with open(path, 'w') as file:
                json.dump(json_as_dict, file)

        except Exception as e:
            print(e, path)



if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./results/openings_users"
    patch_folder_and_sub_folders(folder)

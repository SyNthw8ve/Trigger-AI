import json
import statistics
from typing import List, Callable, Optional

from util.metrics.matches import average_from_distribution, max_from_distribution, min_from_distribution


def add_avg_max_min(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    matches_results = results_dict.get("matches_results", None)

    if matches_results is None:
        return None

    matches_results["avg #matches"] = average_from_distribution(matches_results["distribution #matches"])
    matches_results["max #matches"] = max_from_distribution(matches_results["distribution #matches"])
    matches_results["min #matches"] = min_from_distribution(matches_results["distribution #matches"])

    matches_results["avg #potential"] = average_from_distribution(matches_results["distribution #potential"])
    matches_results["max #potential"] = max_from_distribution(matches_results["distribution #potential"])
    matches_results["min #potential"] = min_from_distribution(matches_results["distribution #potential"])

    by_user = matches_results["by_user"]

    matches_results["avg matches score"] = statistics.mean([user["avg matches"] for user in by_user])
    matches_results["avg real score"] = statistics.mean([user["avg real"] for user in by_user])
    matches_results["avg similarity score"] = statistics.mean([user["avg similarities"] for user in by_user])
    matches_results["avg quality score"] = statistics.mean([user["avg qualities"] for user in by_user])

    # this reorders
    del matches_results["by_user"]
    matches_results["by_user"] = by_user

    json_dict["matches_results"] = matches_results

    return json_dict


def patch_result_paths(path_list: List[str],
                       patch_function: Callable[[dict], Optional[dict]]) -> None:
    patched = {}

    for path in path_list:
        with open(path, 'r') as file:
            json_as_dict = json.load(file)

            if json_as_dict.get("results", None) is None:
                continue

            patched_json = patch_function(json_as_dict)

            if patched_json is not None:
                patched[path] = patched_json

    for path, patched_json in patched.items():
        json.dump(patched_json, open(path, 'w'))

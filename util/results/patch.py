import json
import statistics
from collections import Counter
from typing import List, Callable, Optional, Dict, Any

from util.metrics.matches import average_from_distribution, max_from_distribution, min_from_distribution, \
    make_distribution, to_range

default_order = [
    "distribution #matches",
    "distribution #potential",
    "distribution avg similarity range",
    "distribution avg quality range",
    "distribution avg real range",
    "distribution avg matches range",
    "distribution matches range",
    "% at least 1 match",
    "avg #matches",
    "max #matches of a user",
    "min #matches of a user",
    "avg #potential",
    "max #potential of a user",
    "min #potential of a user",
    "avg matches score",
    "avg real score",
    "avg similarity score",
    "avg quality score",
    "by_user",
]


def reorder_dictionary(order: List[str], dictionary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: dictionary[key]
        for key in order
    }


def rename(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    matches_results = results_dict.get("matches_results", None)

    if matches_results is None:
        return None

    rename_map = {
        "max #matches of a user": "max #matches",
        "min #matches of a user": "min #matches",
        "max #potential of a user": "max #potential",
        "min #potential of a user": "min #potential",
    }

    for new_name, old_name in rename_map.items():
        matches_results[new_name] = matches_results[old_name]
        del matches_results[old_name]

    return json_dict


def reorder(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    matches_results = results_dict.get("matches_results", None)

    if matches_results is None:
        return None

    order = default_order.copy()

    for key in matches_results:
        if key not in order:
            order.append(key)

    results_dict["matches_results"] = reorder_dictionary(order, matches_results)
    return json_dict


def correct_min_max(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    ma = results_dict.get("max instances of any cluster", None)

    if ma is None:
        return None

    mi = results_dict["min instances of any cluster"]

    if ma < mi:
        results_dict["max instances of any cluster"] = mi
        results_dict["min instances of any cluster"] = ma
        return json_dict

    return None


def add_avg_max_min(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    matches_results = results_dict.get("matches_results", None)

    if matches_results is None:
        return None

    if "avg #matches" in matches_results:
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

    return json_dict


def add_matches_distribution(json_dict: dict) -> Optional[dict]:
    results_dict = json_dict.get("results", None)

    if results_dict is None:
        return None

    matches_results = results_dict.get("matches_results", None)

    if matches_results is None:
        return None

    matches_range_counter = Counter()

    for user_and_matches in matches_results["by_user"]:
        for match in user_and_matches["matches"]:
            matches_range_counter.update([to_range(match["score"], 5)])

    matches_results["distribution matches range"] = {range_: count for range_, count in
                                                     matches_range_counter.most_common()}

    return json_dict


def patch_result_paths(path_list: List[str],
                       patch_function: Callable[[dict], Optional[dict]]) -> None:
    patched = {}

    for path in path_list:
        with open(path, 'r') as file:
            json_as_dict = json.load(file)

            patched_json = patch_function(json_as_dict)

            if patched_json is not None:
                patched[path] = patched_json

    for path, patched_json in patched.items():
        json.dump(patched_json, open(path, 'w'))

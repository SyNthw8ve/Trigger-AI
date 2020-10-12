import json
import os
import statistics
import numpy as np
import sys
from collections import Counter
from typing import List, NamedTuple, Dict, Tuple

from trigger.models.opening import Opening
from util.metrics.matches import to_range


class MatchResult(NamedTuple):
    score: float
    opening: Opening


# I was confused with the number of List[List...]]
MatchesPerUser = List[MatchResult]


def get_all_results_paths_from_folder_and_sub_folders(directory_path: str) -> List[str]:
    return [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory_path)
        for filename in filenames
        if filename.endswith('.json')
    ]


def filter_out_ss_or_no_results(path_list: List[str], ss_min: float) -> List[str]:
    competitor_paths = []

    for path in path_list:
        with open(path, 'r') as file:
            json_as_dict = json.load(file)
            results = json_as_dict.get("results", None)

            if results is None:
                continue

            ss = float(results["ss"])

            # We probably have everything together and it just has a lot
            # of matches because of that
            if ss < ss_min:
                continue

            if results.get("matches_results", None) is None:
                continue

            competitor_paths.append(path)

    return competitor_paths


def extract_first_number_from_range(range_: str) -> int:
    return [int(s) for s in range_.split() if s.isdigit()][0]


def make_distribution(matches: MatchesPerUser, range_step: int) -> Dict[str, int]:
    counter = Counter()
    for match in matches:
        counter.update([to_range(match.score, range_step)])
    return {score: count for score, count in counter.most_common()}


def normed_interval(key: str, maxi, mini) -> float:

    upper_bound = eval(key.split('-')[-1].strip())

    return (upper_bound - mini)/(maxi - mini)


def compare_distributions_test(test_distribution: Dict[str, int], to_compare_distribution: Dict[str, int]) -> float:

    test_keys = set(test_distribution.keys())
    to_compare_keys = set(to_compare_distribution.keys())

    all_keys = test_keys.union(to_compare_keys)

    scores = []

    for key in all_keys:

        test_value = test_distribution.get(key, 0)
        to_compare_value = to_compare_distribution.get(key, 0)

        diff = test_value - to_compare_value
        w_diff = diff * np.exp(normed_interval(key, 100, 50))

        scores.append(w_diff)

    return np.sum(scores)


def load_distributions(directory_path):

    path_list = get_all_results_paths_from_folder_and_sub_folders(
        directory_path)
    competitor_paths = filter_out_ss_or_no_results(path_list, 0.2)

    competitors_by_cluster = [
        {"dists": json.load(open(competitor_path, 'r'))["results"]["matches_results"],
            "path": competitor_path}
        for competitor_path in competitor_paths
    ]

    results = []

    for i in range(len(competitors_by_cluster) - 1):

        test_matches_dist = competitors_by_cluster[i]["dists"]["distribution matches"]
        test_path = competitors_by_cluster[i]["path"]

        test_result= {'test_algo': test_path, 'comparisons': []}

        for j in range(i + 1, len(competitors_by_cluster)):

            to_compare_matches_dist = competitors_by_cluster[j]["dists"]["distribution matches"]
            to_compare_path = competitors_by_cluster[j]["path"]

            bean_deviation = compare_distributions_test(
                test_matches_dist, to_compare_matches_dist)

            test_result['comparisons'].append({'compared_algo': to_compare_path,
                            'bean_deviation': str(bean_deviation)})

        results.append(test_result)

    with open("./compared_test.json", "w") as f:
        
        json.dump(results, f)


def compare_distributions(perfect_distribution: Dict[str, int],
                          competitor_distribution: Dict[str, int]) -> Tuple[float, float]:
    # perfect:
    #
    # "distribution matches": {
    #    "100 - 105": 4,
    #    "95  - 100": 2,
    #    "90  - 95" : 3,
    #    "85  - 90" : 4,
    #    "80  - 85" : 5,
    #    "75  - 80" : 6,
    #    "70  - 75" : 7,
    #    "65  - 70" : 8,
    #    "60  - 65" : 9,
    #    "55  - 60" : 5,
    #    "50  - 55" : 7,
    # },

    # competitor:
    #
    # "distribution matches": {
    #    "100 - 105": 0,
    #    "95  - 100": 0,
    #    "90  - 95" : 1,
    #    "85  - 90" : 5,
    #    "80  - 85" : 5,
    #    "75  - 80" : 3,
    #    "70  - 75" : 3,
    #    "65  - 70" : 9,
    #    "60  - 65" : 5,
    #    "55  - 60" : 5,
    #    "50  - 55" : 5,
    # },

    perfect_ranges = set(perfect_distribution.keys())
    sorted_perfect_ranges = sorted(
        perfect_ranges, key=extract_first_number_from_range, reverse=True)

    highest_sorted_perfect_ranges = sorted_perfect_ranges[0:2]
    highest_sorted_perfect_ranges_weights = [0.55, 0.45]

    quality = 0.

    for match_range, weight in zip(highest_sorted_perfect_ranges, highest_sorted_perfect_ranges_weights):
        if match_range in competitor_distribution:
            quality += weight

    quantity = 0.

    highest_sorted_perfect_ranges = sorted_perfect_ranges

    for match_range in highest_sorted_perfect_ranges:

        if match_range not in competitor_distribution:
            continue

        count = int(competitor_distribution[match_range])
        perfect_count = int(perfect_distribution[match_range])

        percentage = count / perfect_count

        quantity += percentage / len(highest_sorted_perfect_ranges)

    print("Perfect", perfect_distribution)
    print("Competitor", competitor_distribution)
    print("#", quantity)
    print("%", quality)
    return min(1., max(0., quantity)), min(1., max(0., quality))


def look_folder_and_sub_folders(directory_path: str) -> None:
    path_list = get_all_results_paths_from_folder_and_sub_folders(
        directory_path)
    competitor_paths = filter_out_ss_or_no_results(path_list, 0.2)

    # This is perfect in the sense that: it has everything in the same cluster ->
    # it has the most #matches, the highest #potential -> it will have the both, quality and quantity.
    # Even if it sucks in terms of clustering, this is the best-case in terms of matches
    # (in a perfect world where we have no limitations of computing power / memory so we don't even need to cluster)
    perfect_path = r"results\openings_users\instances_ss_confirmed\avg_layer_norm\ECM\ECM = distance_threshold=1.1.json"

    with open(perfect_path, 'r') as perfect:
        perfect_by_users = json.load(
            perfect)["results"]["matches_results"]["by_user"]

    competitors_by_users = [
        json.load(open(competitor_path, 'r'))[
            "results"]["matches_results"]["by_user"]
        for competitor_path in competitor_paths
    ]

    matches_of_clusterers: List[List[MatchesPerUser]] = []

    for users_results in competitors_by_users + [perfect_by_users]:

        matches_per_clusterer_ = []

        for user_results in users_results:
            matches_per_user_ = [
                MatchResult(float(match_dict["score"]), Opening(
                    **match_dict["opening"]))
                for match_dict in user_results["matches"]
            ]

            matches_per_clusterer_.append(matches_per_user_)

        matches_of_clusterers.append(matches_per_clusterer_)

    perfect_matches_list, competitors_matches_list = matches_of_clusterers[-1], matches_of_clusterers[0:-1]

    range_step = 5

    perfect_distributions_list = [
        make_distribution(perfect_matches_list, range_step)
        for perfect_matches_list in perfect_matches_list
    ]

    wow = {}

    for matches_list, path in zip(competitors_matches_list, competitor_paths):
        quality_scores = []
        quantity_scores = []
        for i, perfect_distribution in enumerate(perfect_distributions_list):
            competitor_matches_distribution = make_distribution(
                matches_list[i], range_step)
            quantity_score, quality_score = compare_distributions(
                perfect_distribution, competitor_matches_distribution)

            quantity_scores.append(quantity_score)
            quality_scores.append(quality_score)

        wow[path] = {
            "avg %": statistics.mean(quality_scores),
            "avg #": statistics.mean(quantity_scores),
        }

    wow = sorted(
        wow.items(), key=lambda pair: pair[1]["avg %"] + pair[1]["avg #"])

    with open('compared.json', 'w') as f:
        json.dump(wow, f)


if __name__ == "__main__":
    folder = sys.argv[1] if len(
        sys.argv) > 1 else "./results/openings_users/instances_ss_confirmed"
    """ look_folder_and_sub_folders(folder) """

    load_distributions(folder)

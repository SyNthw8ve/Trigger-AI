import json
import os
import statistics
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

    range_gains = {
        "100 - 105": 1.,
        "95 - 100": .95,
        "90 - 95": .90,
        "85 - 90": .85,
        "80 - 85": .70,
        "75 - 80": .60,
        "70 - 75": .50,
        "65 - 70": .40,
        "60 - 65": .30,
        "55 - 60": .20,
        "50 - 55": .10,
    }

    perfect_ranges = set(perfect_distribution.keys())

    quality = 0.

    for match_range in perfect_ranges:
        if match_range in competitor_distribution:
            quality += range_gains[match_range]

    range_punishments = {
        "100 - 105": .15,
        "95 - 100": .14,
        "90 - 95": .13,
        "85 - 90": .12,
        "80 - 85": .11,
        "75 - 80": .09,
        "70 - 75": .08,
        "65 - 70": .04,
        "60 - 65": .03,
        "55 - 60": .02,
        "50 - 55": .01,
    }

    quantity = 1.

    for match_range in perfect_ranges:
        punishment = range_punishments[match_range]

        if match_range not in competitor_distribution:
            quantity -= punishment
            continue

        count = int(competitor_distribution[match_range])
        perfect_count = int(perfect_distribution[match_range])

        if count == perfect_count:
            continue

        same_percentage = count / perfect_count
        weight = 1. - same_percentage
        quantity -= punishment * weight

    # least_important_ranges = {"60 - 65", "55 - 60", "50 - 55"}
    #
    # if len(perfect_ranges.difference(least_important_ranges)) < 2:
    #     score += .2

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
            competitor_matches_distribution = make_distribution(matches_list[i], range_step)
            quantity_score, quality_score = compare_distributions(perfect_distribution, competitor_matches_distribution)

            quantity_scores.append(quantity_score)
            quality_scores.append(quality_score)

        wow[path] = {
            "avg %": statistics.mean(quality_scores),
            "avg #": statistics.mean(quantity_scores),
        }

    wow = sorted(wow.items(), key=lambda pair: pair[1]["avg %"] + pair[1]["avg #"])

    with open('compared.json', 'w') as f:
        json.dump(wow, f)


if __name__ == "__main__":
    folder = sys.argv[1] if len(
        sys.argv) > 1 else "./results/openings_users/instances_ss_confirmed"
    look_folder_and_sub_folders(folder)

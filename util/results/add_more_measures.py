import os
import json
import sys
import statistics

def patch(matches_results):
    def average_from_distribution(distribution) -> float:
        return sum(int(number) * frequency
                   for number, frequency
                   in distribution.items()) / \
            sum(frequency
                for frequency
                in distribution.values())

    def max_from_distribution(distribution) -> float:
        return max(int(number)
                   for number
                   in distribution.keys())

    def min_from_distribution(distribution) -> float:
        return min(int(number)
                   for number
                   in distribution.keys())

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

    return matches_results

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
                json_as_dict["results"]["matches_results"] = mr

            with open(path, 'w') as file:
                json.dump(json_as_dict, file)

        except Exception as e:
            print("?", e, sys.exc_info()[0], path)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else R".\results\openings_users"
    patch_folder_and_sub_folders(folder)

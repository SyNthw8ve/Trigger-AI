import json
import sys
import ast
from typing import List, Dict, Any
from util.results.fetcher import get_result_paths_from_folder_and_sub_folders


def look_in_folder_and_sub_folders(directory_path: str,
                                   contains: str,
                                   keys: List[str],
                                   n: int) -> Dict[str, List[Dict[str, Any]]]:

    paths = get_result_paths_from_folder_and_sub_folders(directory_path, contains)
    return look_in(paths, keys, n)


def look_in(path_list: List[str],
            keys: List[str],
            n: int
            ) -> Dict[str, List[Dict[str, Any]]]:
    all_scores = {}

    for path in path_list:
        try:
            with open(path, 'r') as file:
                json_as_dict = json.load(file)

                if json_as_dict.get("results", None) is None:
                    continue

                mr = json_as_dict["results"].get("matches_results", None)

                if mr is None:
                    all_scores[path] = {
                        "ss": float(json_as_dict["results"]["ss"]),
                        "chs": float(json_as_dict["results"]["chs"]),
                        r"% at least 1 match": 0,
                        "avg #matches": 0,
                        "max #matches": 0,
                        "avg #potential": 0,
                        "max #potential": 0,
                        "avg matches score": 0,
                        "avg similarity score": 0,
                        "avg quality score": 0,
                    }
                else:
                    all_scores[path] = {
                        "ss": float(json_as_dict["results"]["ss"]),
                        "chs": float(json_as_dict["results"]["chs"]),
                        r"% at least 1 match": float(mr[r"% at least 1 match"], ),
                        "avg #matches": float(mr["avg #matches"]),
                        "max #matches": float(mr["max #matches"]),
                        "avg #potential": float(mr["avg #potential"]),
                        "max #potential": float(mr["max #potential"]),
                        "avg matches score": float(mr["avg matches score"]),
                        "avg similarity score": float(mr["avg similarity score"]),
                        "avg quality score": float(mr["avg quality score"]),
                    }

        except Exception as e:
            print(e, path)

    results = {}

    for key in keys:
        try:
            ordered = sorted(all_scores.items(), key=lambda item: item[1].get(key, 0), reverse=True)[0:n]
            results[key] = [
                {
                    "path": path,
                    "scores": scores
                } for path, scores in ordered
            ]

        except Exception as e:
            print(e, key)

    return results


def parse_array_from_string(string: str) -> List[str]:
    return [key.strip() for key in ast.literal_eval(string)]


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./results/openings_users"
    path_contains = sys.argv[2] if len(sys.argv) > 2 else ""
    measures = parse_array_from_string(sys.argv[3]) if len(sys.argv) > 3 else [
        "ss",
        "chs",
        r"% at least 1 match",
        "avg #matches",
        "max #matches",
        "avg #potential",
        "max #potential",
        "avg matches score",
        "avg similarity score",
        "avg quality score",
    ]

    output_path = sys.argv[4] if len(sys.argv) > 4 else "best.json"

    best = look_in_folder_and_sub_folders(folder, path_contains, measures, 100)

    with open('../../best.json', 'w') as f:
        json.dump(best, f)

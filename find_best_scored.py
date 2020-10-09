import os
import json
import sys


def look_folder_and_sub_folders(directory_path: str) -> None:
    path_list = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory_path)
        for filename in filenames
        if filename.endswith('.json')
    ]

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

    n = 100

    keys = [
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

    with open('best.json', 'w') as f:
        json.dump(results, f)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./results/openings_users"
    look_folder_and_sub_folders(folder)

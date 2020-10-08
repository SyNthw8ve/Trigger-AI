import os
import json
import sys
from typing import Optional, Tuple

TEST_RESULTS = Tuple[float, float, Optional[float], str]

def look_at_composite_score(scores: TEST_RESULTS) -> float:
    return 0 if scores[2] is None else scores[2] 

def look_at_ss_score(scores: TEST_RESULTS) -> float:
    return scores[0]

def look_at_chs_score(scores: TEST_RESULTS) -> float:
    return scores[1]

def look_folder_and_sub_folders(directory_path: str) -> None:
    path_list = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory_path)
        for filename in filenames
        if filename.endswith('.json')
    ]

    all_scores = []

    for path in path_list:
        try:
            with open(path, 'r') as file:
                json_as_dict = json.load(file)

                if json_as_dict.get("results", None) is None:
                    continue

                mr = json_as_dict["results"].get("matches_results", None)

                if mr is None:
                    all_scores.append((
                        float(json_as_dict["results"]["ss"]),
                        float(json_as_dict["results"]["chs"]),
                        None,
                        path
                    ))
                    continue

                all_scores.append((
                    float(json_as_dict["results"]["ss"]),
                    float(json_as_dict["results"]["chs"]),
                    float(mr["composite score"]),
                    path
                ))

        except Exception as e:
            print(e, path)

    n = 10

    descriptions_and_functions = [
        ("ss", look_at_ss_score),
        ("chs", look_at_chs_score),
        ("composite", look_at_composite_score)
    ]

    for description, function in descriptions_and_functions:
        print(f"By {description} score the first {n} are:")
        ordered = sorted(all_scores, key=function, reverse=True)[0:n]

        for test in ordered:
            print(test)



if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./results/openings_users"
    look_folder_and_sub_folders(folder)
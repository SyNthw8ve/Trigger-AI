from collections import Counter
from typing import Dict, List
import numpy
from scipy.spatial.distance import cosine


def similarity_metric(embedding1: numpy.ndarray, embedding2: numpy.ndarray) -> float:
    return numpy.nan_to_num(1 - cosine(embedding1, embedding2), 0)


def to_range(percentage: float, step: int) -> str:
    lower = (int(percentage * 100) // step) * step
    upper = lower + step
    return f"{lower} - {upper}"


def extract_first_number_from_range(range_: str) -> int:
    return [int(s) for s in range_.split() if s.isdigit()][0]


def make_distribution(matches: List[dict], range_step: int) -> Dict[str, int]:
    counter = Counter()
    for match in matches:
        counter.update([to_range(match["score"], range_step)])
    return {score: count for score, count in counter.most_common()}


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
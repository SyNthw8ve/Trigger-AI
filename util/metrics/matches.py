import logging
import statistics
from collections import Counter
from typing import Dict, List

import numpy
from scipy.spatial.distance import cosine

from trigger.models.match import Match
from trigger.models.user import User
from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.opening_transformer import Opening
from trigger.train.transformers.user_transformer import UserInstance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('matches')
logger.setLevel(logging.INFO)


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


def real_metric(similarity_score: float, quality_score: float):
    return 0.5 * similarity_score + 0.5 * quality_score


def similarity_metric(embedding1: numpy.ndarray, embedding2: numpy.ndarray) -> float:
    return numpy.nan_to_num(1 - cosine(embedding1, embedding2), 0)


def quality_metric(user: User, opening: Opening):
    u_h = set(user.hardSkills)
    u_s = set(user.softSkills)

    o_h = set(opening.hardSkills)
    o_s = set(opening.softSkills)

    if len(o_h) == 0:
        HS_s = 1
    else:
        HS_s = len(o_h.intersection(u_h)) / len(o_h)

    if len(o_s) == 0:
        SS_s = 1

    else:
        SS_s = len(o_s.intersection(u_s)) / len(o_s)

    Mq = 0.6 * HS_s + 0.4 * SS_s

    return Mq


def computeScore(userInstance: UserInstance, openingInstance: Opening) -> float:
    return 1 - cosine(userInstance.embedding, openingInstance.embedding)


def eval_matches(processor: Processor, users_instances: List[UserInstance]):
    # logger.info("Computing matches results...")

    threshold = 0.5

    by_user = []

    matches_counter = Counter()
    potential_counter = Counter()

    avg_similarity_range_counter = Counter()
    avg_quality_range_counter = Counter()
    avg_real_range_counter = Counter()
    avg_matches_range_counter = Counter()

    matches_range_counter = Counter()

    for user_instance in users_instances:
        cluster_id = processor.predict(user_instance.embedding)

        instances, tags = [], []

        if cluster_id is not None:
            instances, tags = processor.get_instances_and_tags_in_cluster(cluster_id)

        else:
            logger.warning("User has no prediction??", user_instance.user)

        openings = [processor.get_custom_data_by_tag(tag) for tag in tags]
        similarities = [similarity_metric(user_instance.embedding, instance) for instance in instances]
        qualities = [quality_metric(user_instance.user, opening) for opening in openings]
        reals = [real_metric(similarity, quality) for similarity, quality in zip(similarities, qualities)]

        matches = []
        for i, real in enumerate(reals):
            if real >= threshold:
                matches.append(Match(user_instance.user, real, openings[i]))

        match_scores = [match.score for match in matches]

        these_results = {
            'user': {
                'name': user_instance.user.name,
                'softSkill': user_instance.user.softSkills,
                'hardSkills': [{'name': hardskill.name} for hardskill in user_instance.user.hardSkills],
            },
            '#matches': len(matches),
            '#potential': len(openings),
            'avg real': statistics.mean(reals) if len(reals) > 0 else 0,
            'avg similarities': statistics.mean(similarities) if len(similarities) > 0 else 0,
            'avg qualities': statistics.mean(qualities) if len(qualities) > 0 else 0,
            'avg matches': statistics.mean(match_scores) if len(match_scores) > 0 else 0,
            'matches': [
                {
                    'score': match.score,
                    'opening': {
                        'entityId': match.opening.entityId,
                        'softSkills': match.opening.softSkills,
                        'hardSkills': [{'name': hardskill.name} for hardskill in match.opening.hardSkills],
                    }
                } for match in matches
            ]
        }

        by_user.append(these_results)

        matches_counter.update([these_results['#matches']])
        potential_counter.update([these_results['#potential']])

        avg_similarity_range = to_range(these_results['avg similarities'], 5)
        avg_quality_range = to_range(these_results['avg qualities'], 5)
        avg_real_range = to_range(these_results['avg real'], 5)
        avg_matches_range = to_range(these_results['avg matches'], 5)

        for match in matches:
            matches_range_counter.update([to_range(match.score, 5)])

        if len(match_scores) > 0:
            avg_matches_range_counter = avg_matches_range_counter + Counter([avg_matches_range])

        avg_similarity_range_counter = avg_similarity_range_counter + Counter([avg_similarity_range])
        avg_quality_range_counter = avg_quality_range_counter + Counter([avg_quality_range])
        avg_real_range_counter = avg_real_range_counter + Counter([avg_real_range])

    matches_count_distribution = {score: count for score, count in matches_counter.most_common()}
    potential_count_distribution = {score: count for score, count in potential_counter.most_common()}

    return {
        "distribution #matches": matches_count_distribution,
        "distribution #potential": potential_count_distribution,
        "distribution avg similarity range": {range_: count
                                              for range_, count in avg_similarity_range_counter.most_common()},
        "distribution avg quality range": {range_: count for range_, count in avg_quality_range_counter.most_common()},
        "distribution avg real range": {range_: count for range_, count in avg_real_range_counter.most_common()},
        "distribution avg matches range": {range_: count for range_, count in avg_matches_range_counter.most_common()},
        "distribution matches range": {range_: count for range_, count in matches_range_counter.most_common()},
        "% at least 1 match": 1 - (matches_counter.get(0, 0) / sum(matches_counter.values())),
        "avg #matches": average_from_distribution(matches_count_distribution),
        "max #matches of a user": max_from_distribution(matches_count_distribution),
        "min #matches of a user": min_from_distribution(matches_count_distribution),
        "avg #potential": average_from_distribution(potential_count_distribution),
        "max #potential of a user": max_from_distribution(potential_count_distribution),
        "min #potential of a user": min_from_distribution(potential_count_distribution),
        "avg matches score": statistics.mean([user["avg matches"] for user in by_user]),
        "avg real score": statistics.mean([user["avg real"] for user in by_user]),
        "avg similarity score": statistics.mean([user["avg similarities"] for user in by_user]),
        "avg quality score": statistics.mean([user["avg qualities"] for user in by_user]),
        "by_user": by_user
    }

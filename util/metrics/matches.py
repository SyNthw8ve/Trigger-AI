from collections import Counter

import numpy

from trigger.models.match import Match
from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import Opening
from trigger.models.user import User

from scipy.spatial.distance import cosine
from typing import Dict, List
import statistics


def getOpenings(id: int, user: UserInstance, openings: List[Opening], threshold: float) -> List[Match]:
    openings_of_interest = [
        openingInstance for openingInstance in openings
        if openingInstance.cluster_index == id
    ]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openings_of_interest
            if computeScore(user, openingInstance) >= threshold]


def eval_matches(processor: Processor, users_instances: List[UserInstance]):
    threshold = 0.5

    results = []

    matches_counter = Counter()
    potential_counter = Counter()

    avg_similarity_counter = Counter()
    avg_quality_counter = Counter()
    avg_real_counter = Counter()
    avg_matches_counter = Counter()

    for user_instance in users_instances:
        cluster_id = processor.predict(user_instance.embedding)

        if cluster_id is None:
            print("!!!!!!")
            continue

        instances, tags = processor.get_instances_and_tags_in_cluster(cluster_id)
        openings = [processor.get_custom_data_by_tag(tag) for tag in tags]
        similarities = [similarity_metric(user_instance.embedding, instance) for instance in instances]
        qualities = [quality_metric(user_instance.user, opening) for opening in openings]
        reals = [real_metric(similarity, quality) for similarity, quality in zip(similarities, qualities)]

        matches = []
        for i, real in enumerate(reals):
            if real >= threshold:
                matches.append(Match(user_instance.user, real, openings[i]))

        match_scores = [match.score for match in matches]

        print(user_instance.user.hardSkills)

        these_results = {
            'user': {
                'name': user_instance.user.name,
                'softSkill': user_instance.user.softSkills,
                'hardSkills': user_instance.user.hardSkills,
            },
            '#matches': len(matches),
            '#potential': len(openings),
            'avg real': statistics.mean(reals),
            'avg similarities': statistics.mean(similarities),
            'avg qualities': statistics.mean(qualities),
            'avg matches': statistics.mean(match_scores) if len(match_scores) > 0 else "0",
            'matches': [
                {
                    'score': match.score,
                    'opening': {
                        'entityId': match.opening.entityId,
                        'softSkills': match.opening.softSkills,
                        'hardSkills': match.opening.hardSkills,
                    }
                } for match in matches
            ]
        }

        results.append(these_results)

        matches_counter.update([these_results['#matches']])
        potential_counter.update([these_results['#potential']])

        avg_similarity_counter = avg_similarity_counter + Counter([these_results['avg similarities']])
        avg_quality_counter = avg_quality_counter + Counter([these_results['avg qualities']])
        avg_real_counter = avg_real_counter + Counter([these_results['avg real']])
        avg_matches_counter = avg_matches_counter + Counter([these_results['avg matches']])

    return {
        "distribution #matches": list(matches_counter.items()),
        "distribution #potential": list(potential_counter.items()),
        "distribution similarity": list(avg_similarity_counter.items()),
        "distribution quality": list(avg_quality_counter.items()),
        "distribution real": list(avg_real_counter.items()),
        "distribution matches": list(avg_matches_counter.items()),
        "% at least 1 match": 1 - (matches_counter.get(0) / sum(matches_counter.values())),
        "by_user": results,
    }


def real_metric(similarity_score: float, quality_score: float):
    return 0.5 * similarity_score + 0.5 * quality_score


def similarity_metric(embedding1: numpy.ndarray, embedding2: numpy.ndarray) -> float:
    return 1 - cosine(embedding1, embedding2)


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

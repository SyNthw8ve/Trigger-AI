import logging
import statistics
from collections import Counter

import numpy

# from trigger_project.scoring_result import ScoringResult
# from trigger_project.scoring_options import ScoringOptions
# from trigger.metrics.match import similarity_metric, to_range, average_from_distribution, max_from_distribution, min_from_distribution
# from typing import List

from ..models.user import User
from ..models.opening import Opening
from ..instances.user_instance import UserInstance
from ..models.opening import Opening

from trigger.clusters.processor import Processor
from trigger.test.cluster import eval_cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('matches')
logger.setLevel(logging.INFO)


def real_metric(similarity_score: float, quality_score: float, similarity_weight: float = .5, quality_weight: float = .5):
    return similarity_weight * similarity_score + quality_weight * quality_score


def quality_metric(user: User, opening: Opening, hardskill_weight: float = 0.6, softskill_weight: float = 0.4):
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

    Mq = hardskill_weight * HS_s + softskill_weight * SS_s

    return Mq


# def eval_matches(processor: Processor, users_instances: List[UserInstance], score_to_be_match: float = .5):
#     # logger.info("Computing matches results...")

#     by_user = []

#     matches_counter = Counter()
#     potential_counter = Counter()

#     avg_similarity_range_counter = Counter()
#     avg_quality_range_counter = Counter()
#     avg_real_range_counter = Counter()
#     avg_matches_range_counter = Counter()

#     matches_range_counter = Counter()

#     for user_instance in users_instances:
#         cluster_id = processor.predict(user_instance.embedding)

#         instances, tags = [], []

#         if cluster_id is not None:
#             instances, tags = processor.get_instances_and_tags_in_cluster(cluster_id)

#         else:
#             logger.warning("User has no prediction??", user_instance.user)

#         openings = [
#             processor.get_custom_data_by_tag(tag)
#             for tag in tags
#         ]

#         similarities = [
#             similarity_metric(user_instance.embedding, instance)
#             for instance in instances
#         ]

#         qualities = [
#             quality_metric(user_instance.user, opening)
#             for opening in openings
#         ]

#         reals = [
#             real_metric(similarity, quality)
#             for similarity, quality in zip(similarities, qualities)
#         ]

#         matches = []
#         for i, real in enumerate(reals):
#             if real >= .5:
#                 matches.append(TriggerScoring(real, user_instance.user, openings[i]))

#         match_scores = [match.score for match in matches]

#         these_results = {
#             'user': {
#                 'name': user_instance.user.name,
#                 'softSkill': user_instance.user.softSkills,
#                 'hardSkills': [{'name': hardskill.name} for hardskill in user_instance.user.hardSkills],
#             },
#             '#matches': len(matches),
#             '#potential': len(openings),
#             'avg real': statistics.mean(reals) if len(reals) > 0 else 0,
#             'avg similarities': statistics.mean(similarities) if len(similarities) > 0 else 0,
#             'avg qualities': statistics.mean(qualities) if len(qualities) > 0 else 0,
#             'avg matches': statistics.mean(match_scores) if len(match_scores) > 0 else 0,
#             'matches': [
#                 {
#                     'score': match.score,
#                     'opening': {
#                         'entityId': match.opening.entityId,
#                         'softSkills': match.opening.softSkills,
#                         'hardSkills': [{'name': hardskill.name} for hardskill in match.opening.hardSkills],
#                     }
#                 } for match in matches
#             ]
#         }

#         by_user.append(these_results)

#         matches_counter.update([these_results['#matches']])
#         potential_counter.update([these_results['#potential']])

#         avg_similarity_range = to_range(these_results['avg similarities'], 5)
#         avg_quality_range = to_range(these_results['avg qualities'], 5)
#         avg_real_range = to_range(these_results['avg real'], 5)
#         avg_matches_range = to_range(these_results['avg matches'], 5)

#         for match in matches:
#             matches_range_counter.update([to_range(match.score, 5)])

#         if len(match_scores) > 0:
#             avg_matches_range_counter = avg_matches_range_counter + \
#                 Counter([avg_matches_range])

#         avg_similarity_range_counter = avg_similarity_range_counter + \
#             Counter([avg_similarity_range])
#         avg_quality_range_counter = avg_quality_range_counter + \
#             Counter([avg_quality_range])
#         avg_real_range_counter = avg_real_range_counter + \
#             Counter([avg_real_range])

#     matches_count_distribution = {
#         score: count for score, count in matches_counter.most_common()}
#     potential_count_distribution = {
#         score: count for score, count in potential_counter.most_common()}

#     return {
#         "distribution #matches": matches_count_distribution,
#         "distribution #potential": potential_count_distribution,
#         "distribution avg similarity range": {range_: count
#                                               for range_, count in avg_similarity_range_counter.most_common()},
#         "distribution avg quality range": {range_: count for range_, count in avg_quality_range_counter.most_common()},
#         "distribution avg real range": {range_: count for range_, count in avg_real_range_counter.most_common()},
#         "distribution avg matches range": {range_: count for range_, count in avg_matches_range_counter.most_common()},
#         "distribution matches range": {range_: count for range_, count in matches_range_counter.most_common()},
#         "% at least 1 match": 1 - (matches_counter.get(0, 0) / sum(matches_counter.values())),
#         "avg #matches": average_from_distribution(matches_count_distribution),
#         "max #matches of a user": max_from_distribution(matches_count_distribution),
#         "min #matches of a user": min_from_distribution(matches_count_distribution),
#         "avg #potential": average_from_distribution(potential_count_distribution),
#         "max #potential of a user": max_from_distribution(potential_count_distribution),
#         "min #potential of a user": min_from_distribution(potential_count_distribution),
#         "avg matches score": statistics.mean([user["avg matches"] for user in by_user]),
#         "avg real score": statistics.mean([user["avg real"] for user in by_user]),
#         "avg similarity score": statistics.mean([user["avg similarities"] for user in by_user]),
#         "avg quality score": statistics.mean([user["avg qualities"] for user in by_user]),
#         "by_user": by_user
#     }

# def eval_matches_and_cluster(processor: Processor, users_instances: List[UserInstance]):
#     cluster_results = eval_cluster(processor)
#     matches_results = eval_matches(processor, users_instances)

#     results = cluster_results
#     results['matches_results'] = matches_results

#     return results


# def calculate_scores(user_instance: UserInstance,
#                      opening: Opening,
#                      embedding2: numpy.ndarray,
#                      scoring_options: ScoringOptions = ScoringOptions()) -> ScoringResult:

#     similarity = similarity_metric(user_instance.embedding, embedding2)
#     quality = quality_metric(user_instance.user, opening)

#     final = real_metric(similarity_weight=scoring_options.similarity_weight, similarity_score=similarity,
#                         quality_weight=scoring_options.quality_weight, quality_score=quality)

#     return ScoringResult(opening,
#                          similarity, scoring_options.similarity_weight,
#                          quality, scoring_options.quality_weight,
#                          final)
from typing import List

import json
import dataclasses

from ...metrics.match import quality_metric, real_metric

from ...models.project import Project
from ...models.opening import Opening
from ...models.trigger_match import TriggerMatch
from ...models.user import User


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def opening_to_json(opening: Opening):

    return {'hard_skills': opening.hardSkills, 'soft_skills': opening.softSkills}


def user_to_json(user: User, matches: List[TriggerMatch]):

    user_json = {'name': user.name, 'hard_skills': user.hardSkills,
                 'soft_skills': user.softSkills, 'matches': []}

    user_matches = []

    for match in matches:

        quality = quality_metric(user, match.opening)
        # FIXME: match.score here?
        real_score = real_metric(match.score, quality)

        user_match = {
            'score': str(match.score),
            'quality': str(quality), 
            'real_score': str(real_score),
            'opening': opening_to_json(match.opening)
        }

        user_matches.append(user_match)

    user_matches = sorted(user_matches, key=lambda match: match['score'], reverse=True)

    user_json['matches'] = user_matches

    return user_json


def project_to_json(project: Project, variability):

    return {'name': project.name, 'openings': [opening_to_json(opening.opening) for opening in project.openings], 'variability': variability}


def json_to_csv(file_path, output_path):

    pass

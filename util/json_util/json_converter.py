import json
from trigger.models.project import Project
from trigger.models.softskill import Softskill
import pandas

from util.metrics.matches import quality_metric
from typing import List
from trigger.models.opening import Opening
from trigger.models.match import Match
from trigger.models.user import User

import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def opening_to_json(opening: Opening):

    return {'hard_skills': opening.hardSkills, 'soft_skills': opening.softSkills}


def user_to_json(user: User, matches: List[Match]):

    user_json = {'name': user.name, 'hard_skills': user.hardSkills,
                 'soft_skills': user.softSkills, 'matches': []}

    user_matches = []

    for match in matches:

        quality = quality_metric(user, match.opening)
        real_score = 0.5*(match.score + quality)

        user_match = {'score': str(match.score), 'quality':  str(
            quality), 'real_score': str(real_score), 'opening': opening_to_json(match.opening)}

        user_matches.append(user_match)

    user_matches = sorted(
        user_matches, key=lambda match: match['score'], reverse=True)

    user_json['matches'] = user_matches

    return user_json


def project_to_json(project: Project, variability):

    return {'openings': [opening_to_json(opening.opening) for opening in project.openings], 'variability': variability}


def json_to_csv(file_path, output_path):

    pass

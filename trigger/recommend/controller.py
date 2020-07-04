from typing import List, Optional

from trigger.models.User import User
from trigger.models.Opening import Opening
from trigger.models.Match import Match

# configs?
# or class?
from trigger.recommend.smart import Smart

lowest_to_consider_match = 0.


class Controller:
    def __init__(self, smart: Smart) -> None:
        self.smart = smart

    def on_user_change(self, user: User, openings: List[Opening]) -> Optional[List[Match]]:
        # very complex stuff

        matches = []

        for opening in openings:

            score = self.smart.distance(user, opening)
            if score < lowest_to_consider_match:
                continue

            matches.append(Match(user, score, opening))

        return matches

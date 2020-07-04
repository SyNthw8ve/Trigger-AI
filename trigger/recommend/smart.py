# I can't think of a good name for this D:

from trigger.models.User import User
from trigger.models.Opening import Opening


class Smart:
    def __init__(self, model_filepath: str) -> None:
        self.model_filepath = model_filepath

        # load the model, yeppy

    def distance(self, user: User, opening: Opening) -> float:
        # very complicated stuff
        score = 0
        first = user.softSkills[0]
        try:
            score = next(soft.score / first.score for soft in opening.softSkills if soft.name == first.name)
            if score > 1:
                score = 1.0
        except StopIteration as _:
            pass

        return score

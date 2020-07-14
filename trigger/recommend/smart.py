# I can't think of a good name for this D:
from trigger.models.opening import Opening
from trigger.models.user import User
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningPoint
from trigger.recommend.user_transformer import UserPoint
from scipy.spatial import distance


def user_distance(user: User, user_point: UserPoint, opening: Opening, opening_point: OpeningPoint) -> float:
    # very complicated stuff
    return distance.cosine(user_point, opening_point)


def opening_distance(opening_a: Opening, opening_a_point: OpeningPoint, opening_b: Opening, opening_b_point: OpeningPoint) \
        -> float:
    # very complicated stuff
    return distance.cosine(opening_a_point, opening_b_point)

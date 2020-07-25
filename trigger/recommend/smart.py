# I can't think of a good name for this D:
import logging

from trigger.models.opening import Opening
from trigger.models.user import User
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningPoint
from trigger.recommend.user_transformer import UserPoint
from scipy.spatial import distance

logging.basicConfig(format="%(filename)s:%(funcName)s <%(levelname)s>: %(message)s", level=logging.DEBUG)
_logger = logging.getLogger(__name__)


def user_distance(user: User, user_point: UserPoint, opening: Opening, opening_point: OpeningPoint) -> float:
    # very complicated stuff
    result = distance.cosine(user_point, opening_point)
    _logger.debug("Distance between User %s and Opening %s is %f [ aka (%s) & aka (%s) ]",
                  user_point, opening_point, result, user, opening)
    return result


def opening_distance(opening_a: Opening, opening_a_point: OpeningPoint,
                     opening_b: Opening, opening_b_point: OpeningPoint) -> float:
    # very complicated stuff
    result = distance.cosine(opening_a_point, opening_b_point)

    _logger.debug("Distance between Opening %s and Opening %s is %f  ( aka (%s) & aka (%s) )",
                  opening_a_point, opening_b_point, result, opening_a, opening_b)
    return result

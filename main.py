from trigger.models.opening import Opening
from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.user import User
from trigger.recommend import smart
from trigger.recommend.controller import Controller
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningTransformer
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

import pprint

# some init?
from trigger.recommend.user_transformer import UserTransformer

from trigger.train.other.reader import SkillsFileReader

"""
all_softskill_names = ["Leadership", "Creativity", "Individuality"]
softskill_transformer = SoftskillTransformer(all_softskill_names)

opening_transformer = OpeningTransformer(softskill_transformer)
clusters = Clusters(opening_transformer)

user_transformer = UserTransformer(softskill_transformer)

controller = Controller(clusters, user_transformer)

# We got this from the web?

user = User(softSkills=[Softskill("Leadership", 2), Softskill("Creativity", 3)],
            hardSkills=[], interests=["Swimming"])

openings = \
    [
        Opening(
            entityId="0x" + str(i),
            sector='Cheese',
            area="Informática",
            languages=[Language("English")],
            softSkills=[Softskill("Leadership", i + 1), Softskill("Individuality", 5 - i)],
            hardSkills=[]
        )
        for i in range(5)
    ]

openings.append(
    Opening(
            entityId="0x6",
            sector='Cheese',
            area="Informática",
            languages=[Language("English")],
            softSkills=[Softskill("Leadership", 1), Softskill("Creativity", 2)],
            hardSkills=[]
    )
)

for opening in openings:
    clusters.add_opening(opening)

print("Clusters:")
pprint.pprint(clusters.cluster_dict)

print("User: ")
pprint.pprint(user)

matches = controller.user_matches(user)

print("Matches: ")

pprint.pprint([(match.opening, match.score) for match in matches])
"""

reader = SkillsFileReader('./inputs.json')




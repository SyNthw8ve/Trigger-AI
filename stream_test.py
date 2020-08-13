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

from trigger.train.cluster.gstream import 

import pprint

# some init?
from trigger.recommend.user_transformer import UserTransformer

from trigger.train.other.reader import SkillsFileReader
from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.kmeans import KCluster

reader = SkillsFileReader('./inputs.json')
embedder = SentenceEmbedder(modelname='distilbert-base-nli-stsb-mean-tokens')

hardSkills = reader.hardskills
softSkills = reader.softskills
competences = reader.competences

user = User(softSkills=[Softskill(softSkills[0], 2), Softskill(softSkills[2], 3)],
            hardSkills=[Hardskill(hardSkills[0]), Hardskill(hardSkills[4])], interests=["Swimming"])

openings = [
    Opening(
        entityId="0x1",
        sector='Computer Engineering',
        area="Software Development",
        languages=[Language("English")],
        softSkills=[Softskill(softSkills[1], 2), Softskill(softSkills[2], 3)],
        hardSkills=[Hardskill(hardSkills[0])]
    ),
    Opening(
        entityId="0x2",
        sector='Formula 1',
        area="Aerodynamics",
        languages=[Language("English")],
        softSkills=[Softskill(softSkills[1], 4), Softskill(softSkills[3], 3)],
        hardSkills=[Hardskill(hardSkills[1]), Hardskill(hardSkills[3])]
    ),
    Opening(
        entityId="0x3",
        sector='Computer Engineering',
        area="Security",
        languages=[Language("English")],
        softSkills=[Softskill(softSkills[1], 4), Softskill(softSkills[6], 3)],
        hardSkills=[Hardskill(hardSkills[0])]
    )
]

userInstance = UserInstance(user, embedder)

openingsIntances = [OpeningInstance(opening, embedder) for opening in openings]


gstream = GStream(vector_size=2, alpha1=0.01, alpha2=0.001, beta=5, error_decrease=0.9)
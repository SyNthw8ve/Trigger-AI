from trigger_project.models.user import User
from trigger_project.models.softskill import Softskill
from trigger_project.models.hardskill import Hardskill
from trigger_project.models.opening import Opening
from trigger_project.transformers.opening_transformer import OpeningTransformer
from trigger_project.scoring import TriggerScoringCalculator, TriggerScoringOptions
from trigger.trigger_interface import TriggerInterface
from trigger.scoring import ScoringCalculator
from trigger.clusters.ecm import ECM
from trigger_project.transformers.user_transformer import UserTransformer

if __name__ == "__main__":

    ti = TriggerInterface(ECM(0.5), {
        "opening": OpeningTransformer(),
        "user": UserTransformer(),
    }, TriggerScoringCalculator())

    ti.add("1", "opening", Opening(
        "1",
        hardSkills=[Hardskill("Hunting"), Hardskill("IT")],
        softSkills=[Softskill("Teamwork"), Softskill("Makes the dream work")]
        )
    )

    ti.add("2", "opening", Opening(
        "2",
        hardSkills=[Hardskill("IT")],
        softSkills=[Softskill("Teamwork")]
        )
    )

    ti.add("3", "opening", Opening(
        "3",
        hardSkills=[Hardskill("Hunter")],
        softSkills=[Softskill("Dream catcher")]
        )
    )

    print(ti.get_scorings_for("user", User(
        "Kimmy",
        softSkills=[Softskill("Teamwork")],
        hardSkills=[Hardskill("Hunter")]
    )))
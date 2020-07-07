from trigger.models.Opening import Opening
from trigger.models.Softskill import Softskill
from trigger.models.Hardskill import Hardskill
from trigger.models.Language import Language
from trigger.models.User import User
from trigger.recommend.controller import Controller
import trigger.train

# on user change
from trigger.recommend.smart import Smart

smart = Smart("")
controller = Controller(smart)

# We got this from the web?

user = User(softSkills=[Softskill("Bullshitting", 3)],
            hardSkills=[Hardskill("Please", 1)], interests=["Swimming"])
openings = [Opening(sector='Color', area="Klawn", languages=[Language("English", 10)], softSkills=[Softskill("Bullshitting", i + 1), Softskill(
    "Gestão", 5 - i + 1)], hardSkills=[Hardskill("Please", i + 1)]) for i in range(5)]

matches = controller.on_user_change(user, openings)

print(user)

for match in matches:
    print(match.opening, "<Score: " + str(match.score) + ">")

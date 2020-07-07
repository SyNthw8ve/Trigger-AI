from trigger.models.Opening import Opening
from trigger.models.Softskill import Softskill
from trigger.models.User import User
from trigger.recommend.controller import Controller
import trigger.train

# on user change
from trigger.recommend.smart import Smart

smart = Smart("")
controller = Controller(smart)

# We got this from the web?

user = User([Softskill("Bullshitting", 3)])
openings = [Opening([Softskill("Bullshitting", i), Softskill(
    "Gestão", 5 - i)], 1000 * i) for i in range(5)]

matches = controller.on_user_change(user, openings)

for match in matches:
    print(match)

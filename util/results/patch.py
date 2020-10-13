import os
import logging

from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.models.softskill import Softskill as Softzkill
from trigger.models.user import User as Userz
from trigger.models.opening import Opening as Openingz

instances_paths = ['./data/instances', './data/instances_ss_confirmed', './data/save']

import io
import pickle


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == "trigger.models.SoftSkill":
            renamed_module = "trigger.models.softskill"
        elif module == "trigger.models.softskillz":
            renamed_module = "trigger.models.softskill"
        elif module == "trigger.models.userz":
            renamed_module = "trigger.models.user"
        elif module == "trigger.models.openingz":
            renamed_module = "trigger.models.opening"

        return super(RenameUnpickler, self).find_class(renamed_module, name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)

# What I did:
# Create files with a different name. (For example Softskill -> Softskillz)
# Read the old embeddings and replace old Softskill for new one
# Save
# Delete file with the correct name (Softskill)
# Rename Softskillz -> Softskill
# edit the find_class and add something like:

#elif module == "trigger.models.softskillz":
#            renamed_module = "trigger.models.softskill"

# Run this again

for instances_path in instances_paths:

    instances_files = [os.path.join(instances_path, f) for f in os.listdir(
        instances_path) if os.path.isfile(os.path.join(instances_path, f))]

    users_instances_files = [instance_path for instance_path in instances_files if instance_path.find("users") != -1]
    openings_instances_files = [instance_path for instance_path in instances_files if
                                instance_path.find("openings") != -1]

    for users_instances_path in users_instances_files:

        logging.info("Users instances " + users_instances_path)

        with open(users_instances_path, 'rb') as file:
            users_instances = renamed_load(file)

        for users_instance in users_instances:
            old = users_instance.user
            old_sss = old.softSkills

            new_ss = [
                Softzkill(old_ss.name)
                for old_ss in old_sss
            ]

            users_instance.user = Userz(old.name, new_ss, old.hardSkills)

        UserInstance.save_instances(users_instances_path, users_instances)

    for openings_instances_path in openings_instances_files:

        logging.info("Opening instances " + openings_instances_path)

        with open(openings_instances_path, 'rb') as file:
            openings_instances = renamed_load(file)

        for opening_instance in openings_instances:
            old = opening_instance.opening
            old_sss = old.softSkills
            new_ss = [
                Softzkill(old_ss.name)
                for old_ss in old_sss
            ]
            opening_instance.opening = Openingz(old.entityId, old.hardSkills, new_ss)

        OpeningInstance.save_instances(openings_instances_path, openings_instances)

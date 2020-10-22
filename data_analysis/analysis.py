import os
import pandas as pd

from trigger.models.opening import Opening
from trigger.models.user import User
from typing import List
from util.readers.reader import DataReaderOpenings, DataReaderUsers

from sklearn.preprocessing import LabelEncoder

def load_data(users_path, openings_path):

    openings = DataReaderOpenings.populate(openings_path)
    users = DataReaderUsers.populate(users_path)

    return (users, openings)


def data_frame_build_openings(openings: List[Opening]):

    soft_skills = []
    hard_skills = []

    for opening in openings:

        soft_skills += [ [opening.entityId, soft_skill.name] for soft_skill in opening.softSkills ]
        hard_skills += [ [opening.entityId, hard_skill.name] for hard_skill in opening.hardSkills ]

    soft_skill_frame = pd.DataFrame(soft_skills, columns=['Opening ID', 'Softskill'])
    hard_skill_frame = pd.DataFrame(hard_skills, columns=['Opening ID', 'Hardskill'])

    return (soft_skill_frame, hard_skill_frame)

def data_frame_build_users(users: List[User]):

    soft_skills = []
    hard_skills = []

    for user in users:

        soft_skills += [ [user.name, soft_skill.name] for soft_skill in user.softSkills ]
        hard_skills += [ [user.name, hard_skill.name] for hard_skill in user.hardSkills ]

    soft_skill_frame = pd.DataFrame(soft_skills, columns=['User Name', 'Softskill'])
    hard_skill_frame = pd.DataFrame(hard_skills, columns=['User Name', 'Hardskill'])

    soft_skill_frame.to_csv('./data/csv/users/softskills.csv')
    hard_skill_frame.to_csv('./data/csv/users/hardskills.csv')

    return (soft_skill_frame, hard_skill_frame)

def skills_count_users(users: List[User]):

    soft_skill_frame, hard_skill_frame = data_frame_build_users(users)

    soft_skill_frame['Softskill'].value_counts().to_csv('./data/csv/users/soft_skill_count.csv')
    hard_skill_frame['Hardskill'].value_counts().to_csv('./data/csv/users/hard_skill_count.csv')

def skills_count_openings(openings: List[Opening]):

    soft_skill_frame, hard_skill_frame = data_frame_build_openings(openings)

    soft_skill_frame['Softskill'].value_counts().to_csv('./data/csv/openings/soft_skill_count.csv')
    hard_skill_frame['Hardskill'].value_counts().to_csv('./data/csv/openings/hard_skill_count.csv')

if __name__ == "__main__":
    
    users_path = './examples/openings_users_softskills_confirmed/users'
    openings_path = './examples/openings_users_softskills_confirmed/openings'

    users_file = os.path.join(users_path, 'users_0.txt')
    openings_file = os.path.join(openings_path, 'openings_0.txt')

    users, openings = load_data(users_file, openings_file)

    skills_count_users(users)
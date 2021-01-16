import os
import pandas as pd
import matplotlib.pyplot as plt

from trigger.models.opening import Opening
from trigger.models.user import User
from typing import List
from util.readers.reader import DataReaderOpenings, DataReaderUsers

from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from umap import UMAP


class DataAnalyser:

    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(users_path, openings_path):

        openings = DataReaderOpenings.populate(openings_path)
        users = DataReaderUsers.populate(users_path)

        return (users, openings)

    @staticmethod
    def data_frame_build_openings(openings: List[Opening]):

        soft_skills = []
        hard_skills = []

        for opening in openings:

            soft_skills += [ [opening.entityId, soft_skill.name] for soft_skill in opening.softSkills ]
            hard_skills += [ [opening.entityId, hard_skill.name] for hard_skill in opening.hardSkills ]

        soft_skill_frame = pd.DataFrame(soft_skills, columns=['Opening ID', 'Softskill'])
        hard_skill_frame = pd.DataFrame(hard_skills, columns=['Opening ID', 'Hardskill'])

        return (soft_skill_frame, hard_skill_frame)

    @staticmethod
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

    @staticmethod
    def skills_count_users(users: List[User]):

        soft_skill_frame, hard_skill_frame = DataAnalyser.data_frame_build_users(users)

        soft_skill_frame['Softskill'].value_counts().to_csv('./data/csv/users/soft_skill_count.csv')
        hard_skill_frame['Hardskill'].value_counts().to_csv('./data/csv/users/hard_skill_count.csv')

    @staticmethod
    def skills_count_openings(openings: List[Opening]):

        soft_skill_frame, hard_skill_frame = DataAnalyser.data_frame_build_openings(openings)

        soft_skill_frame['Softskill'].value_counts().to_csv('./data/csv/openings/soft_skill_count.csv')
        hard_skill_frame['Hardskill'].value_counts().to_csv('./data/csv/openings/hard_skill_count.csv')

    @staticmethod
    def dulicate(users: List[User]):

        soft_skill_frame, hard_skill_frame = DataAnalyser.data_frame_build_users(users)

        soft_skill_group = soft_skill_frame.groupby('User Name')
    
    @staticmethod
    def plot_data(data, dim, plot_path):

        if dim > 3:

            raise Exception('Too many dimensions to plot.')

        if dim == 2:

            xs = [vec[0] for vec in data]
            ys = [vec[1] for vec in data]

            plt.scatter(xs, ys)

        if dim == 3:

            xs = [vec[0] for vec in data]
            ys = [vec[1] for vec in data]
            zs = [vec[2] for vec in data]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            ax.scatter(xs, ys, zs)
        
        plt.savefig(plot_path)

    @staticmethod
    def dimension_reduction_analysis(data, algorithm: str='pca', components: int=2, plot:bool=False, plot_path=''):

        transformed_data = []

        if algorithm == 'pca':

            pca = PCA(n_components=components)

            transformed_data = pca.fit_transform(data)

        if algorithm == 'tsne':

            tsne = TSNE(n_components=components)

            transformed_data = tsne.fit_transform(data)

        if algorithm == 'tsne_pca':

            pca = PCA(n_components=50)

            t_data = pca.fit_transform(data)

            tsne = TSNE(n_components=components)

            transformed_data = tsne.fit_transform(t_data)

        if algorithm == 'umap':

            umap = UMAP(n_components=components)

            transformed_data = umap.fit_transform(data)

        if plot:

           DataAnalyser.plot_data(transformed_data, components, plot_path)

        return transformed_data


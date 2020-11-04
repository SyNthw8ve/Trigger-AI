import os
import pickle


from util.test.project_test import test_variability
from tests.covariance_test import test_cov

users_path = './examples/openings_users_softskills_confirmed/users'
openings_path = './examples/openings_users_softskills_confirmed/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

if __name__ == "__main__":
    """ with open("data/projects/sample", 'rb') as f:
        projects = pickle.load(f)

    
    test_variability(projects) """

    test_cov()

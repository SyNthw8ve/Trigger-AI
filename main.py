from trigger_project.test.covariance_test import test_cov
from trigger_project.test.ecm_tests import test_ecm
from trigger_project.test.gng_test import test_gng


if __name__ == "__main__":
    test_ecm()
    test_gng()
    test_cov()
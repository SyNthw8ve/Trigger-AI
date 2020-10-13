from trigger.train.cluster.birch.birch import Birch

from util.metrics.cluster import eval_cluster as complete_eval_cluster


def eval_cluster(birch: Birch):
    all_results = complete_eval_cluster(birch)
    return {'ss': all_results["ss"], 'chs': all_results["chs"]}

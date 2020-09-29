from rq.worker import SimpleWorker

from trigger.train.cluster.gstream.gstream import GNG
from server.score_calculator import RealScoreCalculator
from trigger.train.transformers.input_transformer import SentenceEmbedder
from server.trigger_driver import TriggerDriver
from rq.defaults import DEFAULT_LOGGING_DATE_FORMAT, DEFAULT_LOGGING_FORMAT
from rq.local import LocalStack

import json

drivers = LocalStack()


def get_driver() -> TriggerDriver:
    v = drivers.top
    if not v:
        raise Exception('Run outside of worker context')
    return v


class TriggerWorker(SimpleWorker):

    def work(self, burst=False, logging_level="INFO", date_format=DEFAULT_LOGGING_DATE_FORMAT,
             log_format=DEFAULT_LOGGING_FORMAT, max_jobs=None, with_scheduler=False):

        config_path = "server/config.json"

        with open(config_path) as f:
            config = json.load(f)
            print(config)

        driver = TriggerDriver(
            sentence_embedder=SentenceEmbedder(),
            config=config,
            # FIXME: TEMPORARY
            score_to_be_match=0.0,
            score_calculator=RealScoreCalculator(0.5, 0.5),
            clusterer=GNG(epsilon_b=0.001,
                          epsilon_n=0,
                          lam=5,
                          beta=0.9995,
                          alpha=0.95,
                          max_age=10,
                          off_max_age=10,
                          lambda_2=0.2,
                          nodes_per_cycle=1,
                          dimensions=1024,
                          index_type='L2')
        )

        driver.init_clusterer()
        drivers.push(driver)

        return super().work(burst, logging_level, date_format,
                            log_format, max_jobs, with_scheduler)

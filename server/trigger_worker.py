from rq.worker import SimpleWorker

from trigger.train.cluster.ecm.ecm import ECM
from trigger.train.transformers.input_transformer import SentenceEmbedder
from server.trigger_driver import TriggerDriver
from rq.defaults import DEFAULT_LOGGING_DATE_FORMAT, DEFAULT_LOGGING_FORMAT
from rq.local import LocalStack

import logging
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

        logger = logging.getLogger('trigger_worker')
        logger.setLevel(logging_level)

        with open(config_path) as f:
            config = json.load(f)
            logger.info("Starting Worker with config %s", config)

        driver = TriggerDriver(
            sentence_embedder=SentenceEmbedder(),
            config=config,
            processor=ECM(.5)
        )

        driver.init_processor()
        drivers.push(driver)

        return super().work(burst, logging_level, date_format,
                            log_format, max_jobs, with_scheduler)

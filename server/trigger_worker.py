from trigger.scoring import TriggerScoringCalculator
from trigger.transformers.opening_transformer import OpeningTransformer
from trigger.transformers.user_transformer import UserTransformer
from trigger.trigger_interface import TriggerInterface
from rq.worker import SimpleWorker

from server.trigger_driver import TriggerDriver
from interference.clusters.ecm import ECM

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
            interface=TriggerInterface(
                ECM(0.5),
                {
                    "user": UserTransformer(),
                    "opening": OpeningTransformer()
                },
                TriggerScoringCalculator()
            ),
            config=config,
        )

        driver.init_processor()
        drivers.push(driver)

        return super().work(burst, logging_level, date_format,
                            log_format, max_jobs, with_scheduler)

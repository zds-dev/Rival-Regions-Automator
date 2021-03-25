from config import read_config
from modules.ScheduleJob import ScheduleJob
import logging


class TestScheduler(ScheduleJob):
    def __init__(self, config_file='config.json'):
        super().__init__(self.initiate_schedule, 0, config_file)

        self.config = read_config(config_file)
        self.logger = logging.getLogger(__name__)

    def initiate_schedule(self):
        self.logger.info("Initiated Fake Schedule")






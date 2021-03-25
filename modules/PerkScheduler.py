from config import read_config
from rival_regions_wrapper.api_wrapper import Perks

from modules.ScheduleJob import ScheduleJob
import threading
import datetime
import logging

class PerkScheduler(ScheduleJob):
    def __init__(self, perk_type=1, upgrade_type=1, config_file='config.json'):
        super().__init__(self.initiate_schedule, 0, config_file)
        self.perk_type = perk_type
        self.upgrade_type = upgrade_type#

        self.config = read_config(config_file)
        self.logger = logging.getLogger(__name__)

    def check_perk_upgrade(self):
        perks = Perks(self.client.api_wrapper)
        current_perk_info = perks.info()
        if current_perk_info['upgrade_date']:
            return current_perk_info['upgrade_date']
        else:
            return datetime.datetime.now(datetime.timezone.utc)

    def get_perk_stats(self):
        perks = Perks(self.client.api_wrapper)
        current_info = perks.info()
        return current_info

    def upgrade_perk(self):
        perks = Perks(self.client.api_wrapper)
        current_perk_info = perks.info()
        if current_perk_info['upgrade_date']:
            self.logger.warning("Perk upgrade failed. Perk upgrade still running.")
        else:
            perks.upgrade(1,1)
            self.initiate_schedule()
            self.logger.info("Perk upgrade ran.")

    def initiate_schedule(self):
        finish = self.check_perk_upgrade()
        delay = (finish - datetime.datetime.now(datetime.timezone.utc))
        self.logger.info("Scheduled perk upgrade for in {}. [{} UTC]".format(str(delay), finish.strftime('%c')))
        self.timer_thread = threading.Timer(delay.total_seconds()+60, self.upgrade_perk)
        self.timer_thread.start()

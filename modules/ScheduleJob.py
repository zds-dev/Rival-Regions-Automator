import threading
import logging
from .Client import Client

class ScheduleJob:
    client = False

    def __init__(self, run_function, delay, config_file):
        self.logger = logging.getLogger(__name__)
        self.run_function = run_function
        self.delay = delay
        if not ScheduleJob.client:
            ScheduleJob.client = Client()
        else:
            self.logger.debug("Found a created Client. Using...")
        self.client = ScheduleJob.client
        self.timer_thread = None
        self.schedule_running = False

    def start(self):
        self.timer_thread = threading.Timer(self.delay, self.run_function)
        self.timer_thread.start()
        self.schedule_running = True

    def stop(self):
        self.timer_thread.cancel()
        self.schedule_running = False


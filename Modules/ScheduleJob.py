import threading


class ScheduleJob:
    def __init__(self, run_function, delay):
        self.run_function = run_function
        self.delay = delay
        self.timer_thread = None
        self.schedule_running = False

    def start(self):
        self.timer_thread = threading.Timer(self.delay, self.run_function)
        self.timer_thread.start()
        self.schedule_running = True

    def stop(self):
        self.timer_thread.cancel()
        self.schedule_running = False


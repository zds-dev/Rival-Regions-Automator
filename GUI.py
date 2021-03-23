import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
from os import path
from Modules.PerkScheduler import PerkScheduler
from Modules.TestScheduler import TestScheduler
import logging
import threading
from rival_regions_wrapper.authentication_handler import FILE_FORMATTER


SETTINGS_FILE = path.join(path.dirname(__file__), r'config.json')
DEFAULT_SETTINGS = {'USERNAME': 'usernamehere', 'PASSWORD': 'passwordhere', 'LOGIN_METHOD': 'g/v/f'}
# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'USERNAME': '-USERNAME-', 'PASSWORD': '-PASSWORD-', 'LOGIN_METHOD': '-LOGIN METHOD-'}


class Handler(logging.StreamHandler):
    def __init__(self, initial_buffer="", logging_window=None, history=''):
        logging.StreamHandler.__init__(self)
        self.logging_window = logging_window
        self.history = history

    def emit(self, record):
        record = self.format(record)
        if self.logging_window:
            self.logging_window['LOG'].update(value=record+'\n', append=True)
            self.history += record+'\n'

    def re_emit(self):
        if self.logging_window:
            self.logging_window['LOG'].update(value=self.history, append=True)



Logger = logging.getLogger()
Logger.setLevel(logging.DEBUG)


class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.config = self.load_settings(DEFAULT_SETTINGS)

    def load_settings(self, default_settings):
        """Load our settings file"""
        try:
            with open(self.settings_file, 'r') as f:
                settings = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you',
                                   keep_on_top=True,
                                   background_color='red', text_color='white')
            settings = default_settings
            self.save_settings(self.settings_file, settings, None)

        self.config = settings
        return settings

    @staticmethod
    def save_settings(settings_file, settings, values):
        if values:  # if there are stuff specified by another window, fill in those values
            for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
                try:
                    settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
                except Exception as e:
                    print(f'Problem updating settings from window values. Key = {key}')

        with open(settings_file, 'w') as f:
            jsondump(settings, f)

        sg.popup('Settings saved')


class GUI:
    def __init__(self, SETTINGS_FILE, long_tasks):
        self.Setting = Settings(SETTINGS_FILE)
        self.long_tasks = long_tasks
        self.running_long_tasks = {}
        self.window = self.create_main_window()
        self.window_handler = Handler(logging_window=self.window)
        self.window_handler.setFormatter(FILE_FORMATTER)
        self.window_handler.setLevel(logging.INFO)
        Logger.debug("GUI initialized.")
        Logger.addHandler(self.window_handler)


    def create_settings_window(self):

        def text_label(text):
            return sg.Text(text + ':', justification='r', size=(15, 1))

        layout = [[sg.Text('Settings', font='Any 15')],
                  [text_label('Username'), sg.Input(key='-USERNAME-')],
                  [text_label('Password'), sg.Input(key='-PASSWORD-')],
                  [text_label('Login Method'), sg.Input(key='-LOGIN METHOD-')],
                  [sg.Button('Save'), sg.Button('Exit')]]

        window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=self.Setting.config[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

        return window

    def create_main_window(self):
        left_col = [[sg.Multiline(size=(90, 30), key='LOG', font=('Helvetica 10'))],
                    [sg.B('Exit'), sg.B('Change Settings')]]

        right_col_lower = []
        for long_task in [task.__name__ for task in self.long_tasks]+list(self.running_long_tasks.keys()):
            if long_task in [task.__name__ for task in self.long_tasks]:
                active = False
            else:
                active = True
            right_col_lower.append([sg.Checkbox(long_task, default=active, enable_events=True, key=long_task)])

        right_col = [#[sg.T("Username:")],
                     #[sg.T("", key="username")],
                     #[sg.T("Perks:")],
                     #[sg.T("", key='perks')],
                     [sg.Column(right_col_lower)]]

        layout = [[sg.Column(left_col),sg.Column(right_col)]]

        window = sg.Window('RRBot', layout, resizable=True)
        window.finalize()
        self.window = window
        return window

    def run(self):
        while True:  # Event Loop
            if self.window is None:
                self.create_main_window()
                self.window_handler.logging_window = self.window
                self.window_handler.re_emit()

            event, values = self.window.read()
            for long_task in list(self.long_tasks):
                if values[long_task.__name__]:
                    t = threading.Thread(target=self.run_task, args=[long_task])
                    t.start()

            for long_task in list(self.running_long_tasks):
                if not values[long_task]:
                    t = threading.Thread(target=self.stop_task, args=[long_task])
                    t.start()

            if event in (None, 'Exit'):
                break
            if event == 'Change Settings':
                event, values = self.create_settings_window().read(close=True)
                if event == 'Save':
                    self.window.close()
                    self.window = None
                    self.Setting.save_settings(SETTINGS_FILE, self.Setting.config, values)


        self.window.close()

    def run_task(self, task):
        scheduler = task(config_file=SETTINGS_FILE)
        scheduler.start()
        self.running_long_tasks[task.__name__] = scheduler
        Logger.info("Started {}".format(task.__name__))
        self.long_tasks.remove(task)

    def stop_task(self, task):
        scheduler = self.running_long_tasks[task]
        scheduler.stop()
        self.running_long_tasks.pop(task)
        self.long_tasks.append(scheduler.__class__)


gui = GUI(SETTINGS_FILE=SETTINGS_FILE, long_tasks=[PerkScheduler,TestScheduler])
gui.run()

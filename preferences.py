import os.path
import json
from util import is_macos, is_darkmode

class Preferences:
    pref_file = os.path.join(os.getcwd(), "prefs", "config.json")
    defaults = os.path.join(os.getcwd(), "prefs", "defaults.json")
    copy_list = [
        'report_sheet',
        'format_unfinished',
        'unfinished_color',
        'class_portal',
        'protected_set',
        'debug'
    ]

    def __init__(self):
        with open(Preferences.defaults, "r+") as df:
            self.defaults = json.load(df)
        if not os.path.isfile(Preferences.pref_file):
            with open(Preferences.pref_file, 'w+') as pf:
                build_prefs = self.get_default_theme()
                for pref in Preferences.copy_list:
                    build_prefs[pref] = self.defaults[pref]
                json.dump(build_prefs, pf)
        with open(Preferences.pref_file, "r+") as pf:
            self.prefs = json.load(pf)
        self.pref_file = Preferences.pref_file

    def has_pref(self, key):
        return key in self.prefs

    def get_pref(self, key):
        if self.has_pref(key): return self.prefs[key]
        return None

    def update_pref(self, key, value):
        self.prefs[key] = value
        self.save_prefs()

    def save_prefs(self):
        with open(Preferences.pref_file, "w+") as pf:
            json.dump(self.prefs, pf)

    def get_default_pref(self, key):
        if key in self.defaults: return self.defaults[key]
        return None

    def get_default_theme(self):
        return self.defaults['dark_theme'] if is_darkmode() else self.defaults['light_theme']

prefs = Preferences()
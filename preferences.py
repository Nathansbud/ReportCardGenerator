import os.path
import json

class Preferences:
    pref_file = os.path.join(os.path.dirname(__file__), "prefs", "config.json")
    def __init__(self, prefs=None, pref_file=None):
        if prefs is None:
            with open(Preferences.pref_file, "r+") as pf:
                self.prefs = json.load(pf)
        else:
            self.prefs = prefs
        self.pref_file = (Preferences.pref_file if pref_file is None else pref_file)

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

prefs = Preferences()
import os.path
import json
from util import is_macos

class Preferences:
    pref_file = os.path.join(os.getcwd(), "prefs", "config.json")
    defaults = os.path.join(os.getcwd(), "prefs", "defaults.json")
    copy_list = [
        'report_sheet',
        'format_unfinished',
        'unfinished_color',
        'class_portal',
        'debug'
    ]

    if is_macos():
        from Foundation import NSUserDefaults
        theme = NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle')

    def __init__(self):
        def get_default_theme(d):
            return d['dark_theme'] if is_macos() and Preferences.theme == 'Dark' else d['light_theme']

        if not os.path.isfile(Preferences.pref_file):
            with open(Preferences.defaults, 'r+') as df, open(Preferences.pref_file, 'w+') as pf:
                load_defaults = json.load(df)
                build_prefs = get_default_theme(load_defaults)
                for pref in Preferences.copy_list:
                    build_prefs[pref] = load_defaults[pref]
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

prefs = Preferences()
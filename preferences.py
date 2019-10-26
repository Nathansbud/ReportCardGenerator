import os.path
import json
import platform

class Preferences:
    pref_file = os.path.join(os.path.dirname(__file__), "prefs", "config.json")
    defaults = os.path.join(os.path.dirname(__file__), "prefs", "defaults.json")
    os = platform.system()
    if os == "Darwin":
        from Foundation import NSUserDefaults
        theme = NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle')

    def __init__(self):
        def get_default_theme(d):
            if Preferences.is_macos() and Preferences.theme == 'Dark':
                return d['dark_theme']
            else:
                return d['light_theme']

        if not os.path.isfile(Preferences.pref_file):
            with open(Preferences.defaults, 'r+') as df, open(Preferences.pref_file, 'w+') as pf:
                load_defaults = json.load(df)
                build_prefs = get_default_theme(load_defaults)
                build_prefs['report_sheet'] = ""
                json.dump(build_prefs, pf)
        with open(Preferences.pref_file, "r+") as pf:
            self.prefs = json.load(pf)
            #should add a "has changed theme" here but w/e
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

    @staticmethod
    def is_macos():
        return Preferences.os == 'Darwin'

    @staticmethod
    def is_dark():
        return Preferences.theme == "Dark"

prefs = Preferences()
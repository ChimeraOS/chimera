import os
import json


class Settings:

    def __init__(self, settings_directory, settings_default):
        self.settings_directory = settings_directory
        self.settings_default = settings_default
        self.settings_file = os.path.join(self.settings_directory, "settings.json")
        # Make sure a settings file with all expected values exists
        self.__add_new_settings()

    def __add_new_settings(self):
        if not os.path.isdir(self.settings_directory):
            os.makedirs(self.settings_directory)
        settings = self.get_settings()
        for key in self.settings_default:
            try:
                settings[key]
            except KeyError:
                self.set_setting(key, self.settings_default[key])

    def save(self, settings) -> None:
        with open(self.settings_file, "w") as file:
            file.write(json.dumps(settings))
            file.close()

    def set_setting(self, key, value) -> None:
        settings = self.get_settings()
        settings[key] = value
        self.save(settings)

    def get_setting(self, setting: str) -> any:
        with open(self.settings_file, "r") as file:
            settings = json.loads(file.read())
            try:
                return settings[setting]
            except KeyError:
                return None

    def get_settings(self) -> dict:
        if os.path.isfile(self.settings_file):
            with open(self.settings_file, "r") as file:
                results = json.loads(file.read())
                changed = False
                if 'ftp_password' in results and results['ftp_password'] and len(results['ftp_password']) < 8:
                    results['ftp_password'] = self.settings_default['ftp_password']
                    changed = True

                if 'ftp_username' in results and results['ftp_username'] and len(results['ftp_username']) < 5:
                    results['ftp_username'] = self.settings_default['ftp_username']
                    changed = True

                if changed:
                    results['enable_ftp_server'] = False
                    self.save(results)

                return results
        return {}

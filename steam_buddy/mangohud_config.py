import os
from configparser import ConfigParser


class MangoHudConfig:

    def __init__(self, settings_handler, env_dir, mango_dir):
        self.enable_file = env_dir + "/10-mangohud.conf"
        self.config_file = mango_dir + "/MangoHud.conf"
        self.enabled = settings_handler.get_setting("enable_mangohud")
        self.__setup_environment()
        self.__read_toggle_key()

    def __setup_environment(self):
        if self.enabled:
            env_dir = os.path.dirname(self.enable_file)
            if not os.path.exists(env_dir):
                os.mkdir(env_dir, mode=0o755)
            if not os.path.exists(self.enable_file):
                f = open(self.enable_file, "w+")
                f.write("MANGOHUD=1")
                f.close()
            if not os.path.exists(self.config_file):
                self.reset_config()
            else:
                pass
        else:
            if os.path.exists(self.enable_file):
                os.remove(self.enable_file)

    def __read_toggle_key(self):
        if os.path.exists(self.config_file):
            f = open(self.config_file, "r")
            parser = ConfigParser(allow_no_value=True)
            parser.read_string("[Mangohud]\n" + f.read())
            if 'toggle_hud' in parser['Mangohud']:
                self.toggle_key = parser['Mangohud']['toggle_hud']
            else:
                self.toggle_key = "Shift_R+F12"
        else:
            self.toggle_key = "Shift_R+F12"

    def set_enabled(self, enabled) -> None:
        self.enabled = enabled
        self.__setup_environment()
        self.__read_toggle_key()

    def reset_config(self) -> None:
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.mkdir(config_dir, mode=0o755)
        f = open(self.config_file, "w+")
        f.write("no_display")
        self.__read_toggle_key()

    def get_togle_hud_key(self):
        return self.toggle_key

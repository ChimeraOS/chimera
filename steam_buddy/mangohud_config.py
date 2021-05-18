import os
from configparser import ConfigParser


class MangoHudConfig:

    def __init__(self, mango_dir):
        self.config_file = mango_dir + "/MangoHud.conf"
        self.__setup_environment()
        self.__read_toggle_key()

    def __setup_environment(self):
        if not os.path.exists(self.config_file):
            self.reset_config()

    def __read_toggle_key(self):
        if os.path.exists(self.config_file):
            f = open(self.config_file, "r")
            parser = ConfigParser(allow_no_value=True)
            parser.read_string("[Mangohud]\n" + f.read())
            f.close()
            if 'toggle_hud' in parser['Mangohud']:
                self.toggle_key = parser['Mangohud']['toggle_hud']
            else:
                self.toggle_key = "F3"
        else:
            self.toggle_key = "Shift_R+F12"

    def reset_config(self) -> None:
        defaultt_config = [
            "no_display",
            'toggle_hud = "F3"'
        ]
        self.save_config("\n".join(defaultt_config))

    def get_current_config(self):
        if os.path.exists(self.config_file):
            f = open(self.config_file, "r")
            current_config = f.read()
            f.close()
            return current_config

    def save_config(self, new_content):
        self.ensure_dir_for_file(self.config_file)
        f = open(self.config_file, "w+")
        f.write(new_content)
        f.close()
        self.__read_toggle_key()

    def get_toggle_hud_key(self):
        return self.toggle_key

    @staticmethod
    def ensure_dir_for_file(file):
        d = os.path.dirname(file)
        if not os.path.exists(d):
            os.mkdir(d, mode=0o755)

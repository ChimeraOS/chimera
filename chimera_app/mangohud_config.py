import os
from configparser import ConfigParser
from chimera_app.utils import ensure_directory_for_file


class MangoHudConfig:

    def __init__(self, mango_dir):
        self.config_file = mango_dir + "/MangoHud.conf"
        self.__setup_environment()
        self.__read_toggle_key()

    def __setup_environment(self):
        if not os.path.exists(self.config_file):
            self.reset_config()

    def __read_toggle_key(self):
        t_key = "Shift_R+F12"  # MangoHud default
        parser = ConfigParser(allow_no_value=True)

        # Check in file for override
        if os.path.exists(self.config_file):
            f = open(self.config_file, "r")
            parser.read_string("[Mangohud]\n" + f.read())
            f.close()
            if 'toggle_hud' in parser['Mangohud']:
                t_key = parser['Mangohud']['toggle_hud']

        # Check override in MANGOHUD_CONFIG
        config_var = os.environ.get("MANGOHUD_CONFIG")
        if config_var:
            config = '\n'.join(config_var.split(','))
            parser.read_string("[Mangohud]\n" + config)
            if 'toggle_hud' in parser['Mangohud']:
                t_key = parser['Mangohud']['toggle_hud']

        self.toggle_key = t_key

    def reset_config(self) -> None:
        defaultt_config = [
            'no_display',
            'toggle_hud = F3'
        ]
        self.save_config("\n".join(defaultt_config))

    def get_current_config(self):
        if os.path.exists(self.config_file):
            f = open(self.config_file, "r")
            current_config = f.read()
            f.close()
            return current_config

    def save_config(self, new_content):
        ensure_directory_for_file(self.config_file)
        f = open(self.config_file, "w+")
        f.write(new_content)
        f.close()
        self.__read_toggle_key()

    def get_toggle_hud_key(self):
        return self.toggle_key

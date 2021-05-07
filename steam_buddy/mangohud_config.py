import os


class MangoHudConfig:

    def __init__(self, settings_handler, env_dir, mango_dir):
        self.enable_file = env_dir + "/10-mangohud.conf"
        self.config_file = mango_dir + "/MangoHud.conf"
        self.enabled = settings_handler.get_setting("enable_mangohud")
        self.toggle_key = "Shift_R+F12"
        self.__setup_environment()

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

    def set_enabled(self, enabled) -> None:
        self.enabled = enabled
        self.__setup_environment()

    def reset_config(self) -> None:
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.mkdir(config_dir, mode=0o755)
        f = open(self.config_file, "w+")
        f.write("no_display")

    def get_togle_hud_key(self):
        return self.toggle_key

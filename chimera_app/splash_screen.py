import os
import subprocess
import psutil
from chimera_app.config import BIN_PATH


class SplashScreen:
    def __init__(self):
        bin_path = BIN_PATH
        self.__app = os.path.join(bin_path, 'chimera-splash')
        self.__fg = os.path.join(bin_path, 'gamescope-fg')

    def launch(self) -> None:
        print("Showing splash screen")
        subprocess.Popen([self.__fg, self.__app])
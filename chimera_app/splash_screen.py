import os
import subprocess
import psutil
from chimera_app.config import BIN_PATH


class SplashScreen:
    def __init__(self):
        self.__app = os.path.join(BIN_PATH, 'chimera-splash')
        self.__fg = os.path.join(BIN_PATH, 'gamescope-fg')

    def launch(self) -> None:
        print("Showing splash screen")
        subprocess.Popen([self.__fg, self.__app])

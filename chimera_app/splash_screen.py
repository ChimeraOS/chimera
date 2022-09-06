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
        self.kill()
        subprocess.Popen([self.__fg, self.__app])

    def kill(self):
        for process in psutil.process_iter():
            if self.__app in process.cmdline() and self.__fg not in process.cmdline():
                print("Stopping splash screen")
                process.kill()
                break

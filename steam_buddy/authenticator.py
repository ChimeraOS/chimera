import os
import subprocess
import psutil
from steam_buddy.config import AUTHENTICATOR_PATH


def launch_authenticator():
    print("Showing authenticator on screen")
    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0.0"
    kill_authenticator()
    subprocess.Popen([AUTHENTICATOR_PATH])


def kill_authenticator():
    for process in psutil.process_iter():
        if AUTHENTICATOR_PATH in process.cmdline():
            print("Stopping authenticator")
            process.kill()
            break

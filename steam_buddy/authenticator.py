import os
import subprocess
import psutil
from steam_buddy.config import AUTHENTICATOR_PATH


def launch_authenticator():
    print("trying things")
    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0.0"
    already_running = False
    for process in psutil.process_iter():
        if AUTHENTICATOR_PATH in process.cmdline():
            already_running = True
            break
    if not already_running:
        subprocess.Popen([AUTHENTICATOR_PATH])

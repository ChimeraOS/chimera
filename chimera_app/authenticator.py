import os
import secrets
import string
import subprocess
import psutil


def generate_password(length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    # Exclude the O, I, J and 0
    alphabet = alphabet.replace("O", "")
    alphabet = alphabet.replace("I", "")
    alphabet = alphabet.replace("0", "")
    alphabet = alphabet.replace("J", "")  # Looks too much like a lowercase letter
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


class Authenticator:
    def __init__(self, bin_path: str, password_length: int):
        self.__app = os.path.join(bin_path, 'chimera-authenticator')
        self.__wrap = os.path.join(bin_path, 'env-wrapper')
        self.__fg = os.path.join(bin_path, 'gamescope-fg')
        self.__password_length = password_length
        self.__password = generate_password(self.__password_length)

    def reset_password(self) -> None:
        self.__password = generate_password(self.__password_length)

    def matches_password(self, password):
        if password == self.__password:
            return True
        return False

    def launch(self) -> None:
        print("Showing authenticator on screen")
        self.kill()
        subprocess.Popen([self.__fg, self.__wrap, self.__app, self.__password])

    def kill(self):
        for process in psutil.process_iter():
            try:
                cmdline = process.cmdline()
            except:
                continue

            if self.__app in cmdline and self.__fg not in cmdline:
                print("Stopping authenticator")
                process.kill()
                break

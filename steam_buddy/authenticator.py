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
    def __init__(self, authenticator_path: str, password_length: int):
        self.__app = authenticator_path
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
        subprocess.Popen([self.__app, self.__password])

    def kill(self):
        for process in psutil.process_iter():
            if self.__app in process.cmdline():
                print("Stopping authenticator")
                process.kill()
                break

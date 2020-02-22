import os
import secrets
import string
import subprocess
import psutil


class Authenticator:
    def __init__(self, authenticator_path: str, password_length: int):
        self.__app = authenticator_path
        self.__password_length = password_length
        self.__password = self.__make_password()

    def __make_password(self) -> str:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(self.__password_length))
        return password

    def reset_password(self) -> None:
        self.__password = self.__make_password()

    def matches_password(self, password):
        if password == self.__password:
            return True
        return False

    def launch(self) -> None:
        print("Showing authenticator on screen")
        if not os.environ.get("DISPLAY"):
            os.environ["DISPLAY"] = ":0.0"
        self.kill()
        subprocess.Popen([self.__app, self.__password])

    def kill(self):
        for process in psutil.process_iter():
            if self.__app in process.cmdline():
                print("Stopping authenticator")
                process.kill()
                break

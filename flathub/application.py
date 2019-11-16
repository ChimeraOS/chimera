import os
from io import BytesIO
import threading
import time
import subprocess
import flathub
import requests


class Application:

    def __init__(self, flatpak_id: str, name: str, summary: str, image_url: str, installed: bool = False, version="", available_version=""):
        self.flatpak_id = flatpak_id
        self.name = name
        self.summary = summary
        self.installed = installed
        self.__description = ""
        self.progress = -1
        self.busy = False
        self.version = version
        self.available_version = available_version

        if image_url.startswith("/"):
            self.image_url = "https://flathub.org{}".format(image_url)
        else:
            self.image_url = image_url

    def get_image(self, directory: str) -> str:
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, "{}.png".format(self.flatpak_id))
        if not os.path.isfile(filename):
            download = requests.get(self.image_url)
            with open(filename, "wb") as writer:
                writer.write(download.content)
                writer.close()
        return filename

    def get_description(self) -> str:
        if not self.__description:
            request_url = "https://flathub.org/api/v1/apps/" + self.flatpak_id
            api_response = requests.get(request_url)
            if api_response.status_code == requests.codes.ok:
                entry = api_response.json()
                self.__description = entry['description']
        return self.__description

    def install(self):
        if not self.busy:
            self.busy = True
        else:
            print("Error: {} is currently not installable".format(self.name))
            return

        if self.installed:
            print("Error: {} is already installed".format(self.name))
            self.busy = False
            return
        thread = threading.Thread(target=self.__update_installation_progress, args=(flathub.Flathub.install(self.flatpak_id),))
        thread.start()

    def uninstall(self):
        if not self.busy:
            self.busy = True
        else:
            print("Error: {} is currently not uninstallable".format(self.name))
            return

        if not self.installed:
            print("Error: {} is not installed".format(self.name))
            self.busy = False
            return
        thread = threading.Thread(target=self.__update_installation_progress, args=(flathub.Flathub.uninstall(self.flatpak_id),))
        thread.start()

    def update(self):
        if not self.busy:
            self.busy = True
        else:
            print("Error: {} is currently not updateable".format(self.name))
            return

        if not self.installed:
            print("Error: {} is not installed".format(self.name))
            self.busy = False
            return
        # Set the version
        self.version = self.available_version
        self.installed = False
        thread = threading.Thread(target=self.__update_installation_progress, args=(flathub.Flathub.update(self.flatpak_id),))
        thread.start()

    def __update_installation_progress(self, sp: subprocess):
        if not self.busy or sp is None:
            return
        buf = BytesIO()
        while sp.poll() is None:
            if self.installed:
                time.sleep(1)
                continue
            out = sp.stdout.read(1)
            buf.write(out)
            if out in (b'\r', b'\n'):
                for value in buf.getvalue().split():
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    if "%" in value:
                        self.progress = int(value.replace("%", ""))
                buf.truncate(0)
        self.installed = (not self.installed)
        self.busy = False
        self.progress = -1

    def __str__(self) -> str:
        return self.name.title()

    def __lt__(self, other) -> bool:
        names = [str(self), str(other)]
        names.sort()
        if names[0] == str(self):
            return True
        else:
            return False
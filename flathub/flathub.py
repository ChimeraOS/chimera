import subprocess
from typing import List
import flathub
import requests


class Flathub:

    def __init__(self):
        flathub_url = "https://dl.flathub.org/repo/flathub.flatpakrepo"
        self.__add_repo("flathub", flathub_url)
        self.__api_url = "https://flathub.org/api/v1/apps"
        self.__applications = self.__get_application_list()

    def __add_repo(self, name: str, url: str) -> None:
        # This only adds the flatpak repo if it isn't already installed
        return_value = subprocess.call(
            ["flatpak", "remote-add", "--if-not-exists", name, url])
        if return_value != 0:
            print("Error: Failed to add the {name} repo to with url {url} flatpak".format(name=name, url=url))

    def __get_application_list(self):
        applications = []
        api_response = requests.get(self.__api_url)
        if api_response.status_code == requests.codes.ok:
            installed_ids = self.__get_installed_ids()
            for entry in api_response.json():
                flatpak_id = entry['flatpakAppId']
                name = entry['name']
                description = entry['summary']
                image_url = entry['iconDesktopUrl']
                installed = False

                if flatpak_id in installed_ids:
                    installed = True

                application = flathub.Application(flatpak_id, name, description, image_url, installed)
                applications.append(application)
        return applications

    def get_available_applications(self) -> List[flathub.Application]:
        applications = []
        for application in self.__applications:
            if not application.installed or (application.installed and application.busy):
                applications.append(application)
        return applications

    def get_installed_applications(self) -> List[flathub.Application]:
        applications = []
        for application in self.__applications:
            if application.installed and not application.busy or not application.installed and application.busy:
                applications.append(application)
        return applications

    def get_application(self, flatpak_id: str) -> flathub.Application:
        for application in self.__applications:
            if application.flatpak_id == flatpak_id:
                return application
        return None

    def __get_installed_ids(self) -> List[str]:
        command = ["flatpak", "list", "--app"]
        installed_list = []
        for line in subprocess.check_output(command).splitlines():
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            name_description, flatpak_id, _, _ = line.split("\t", 3)
            installed_list.append(flatpak_id)
        return installed_list

    @staticmethod
    def install(flatpak_id: str) -> subprocess:
        return subprocess.Popen(["flatpak", "install", "-y", "flathub", flatpak_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    @staticmethod
    def uninstall(flatpak_id: str) -> subprocess:
        return subprocess.Popen(["flatpak", "uninstall", "-y", flatpak_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)




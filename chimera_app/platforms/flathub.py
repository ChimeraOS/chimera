import os
import subprocess
import requests
from typing import List, Dict
from chimera_app.platforms.store_platform import StorePlatform, dic
from chimera_app.config import RESOURCE_DIR, BANNER_DIR
from chimera_app.steam_config import status_to_collection_name


FLATPAK_WRAPPER = "bin/flatpak-wrapper"


def listdir(path):
    if os.path.isdir(path):
        return os.listdir(path)
    else:
        return []


class Flathub(StorePlatform):
    def __init__(self):
        super().__init__()
        self.platform_code = 'flathub'

        try:
            flathub_url = "https://dl.flathub.org/repo/flathub.flatpakrepo"
            self.__add_repo("flathub", flathub_url)
            self.__api_url = "https://flathub.org/api/v1/apps"
        except Exception:
            print('Error: Failed to initialize flathub support')

    def is_authenticated(self):
        return True

    def __add_repo(self, name: str, url: str) -> None:
        return_value = None
        try:
            # This only adds the flatpak repo if it isn't already installed
            return_value = subprocess.call(["flatpak",
                                            "remote-add",
                                            "--user",
                                            "--if-not-exists",
                                            name,
                                            url])
        finally:
            if return_value != 0:
                print(("Error: Failed to add the {name} repo "
                      "with url {url} flatpak").format(name=name, url=url))

    def _get_all_content(self):
        applications = []
        api_response = requests.get(self.__api_url, timeout=5)
        if api_response.status_code == requests.codes.ok:
            installed_list = self.__get_installed_list()
            for entry in api_response.json():
                flatpak_id = entry['flatpakAppId']
                name = entry['name']
                description = entry['summary']
                available_version = entry['currentReleaseVersion']
                installed = False
                version = ""
                db = self._get_db_entry('flathub', flatpak_id)

                banner = self._get_image_url('flathub', flatpak_id, 'banner')
                poster = self._get_image_url('flathub', flatpak_id, 'poster')
                background = self._get_image_url('flathub', flatpak_id, 'background')
                logo = self._get_image_url('flathub', flatpak_id, 'logo')
                icon = self._get_image_url('flathub', flatpak_id, 'icon')

                default_img = 'https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/' + flatpak_id + '.png'

                if not banner:
                    banner = default_img

                if not poster:
                    poster = default_img

                for app in installed_list:
                    if app['flatpak_id'].strip() == flatpak_id:
                        installed = True
                        version = app['version']

                applications.append(dic({"content_id": flatpak_id,
                                         "summary": description,
                                         "name": name,
                                         "installed_version": version,
                                         "available_version": available_version,
                                         "image_url": banner,
                                         "banner": banner,
                                         "poster": poster,
                                         "background": background,
                                         "logo": logo,
                                         "icon": icon,
                                         "installed": installed,
                                         "operation": None,
                                         "status": db.status,
                                         "status_icon": db.status_icon,
                                         "notes": db.notes,
                                         "launch_options": db.launch_options
                                        }))

        return applications

    def __get_installed_list(self) -> List[Dict[str, any]]:
        installed_list = []
        for line in subprocess.check_output(["flatpak",
                                             "list",
                                             "--user",
                                             "--app"]).splitlines():
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            try:
                _, flatpak_id, version, _ = line.split("\t", 3)
            except ValueError:
                flatpak_id = line
                version = ""
            application_tuple = {
                'flatpak_id': flatpak_id,
                'version': version
            }
            installed_list.append(application_tuple)
        return installed_list

    def get_image_file_base_dir(self, content_id):
        filename = content_id + '.png'
        path = os.path.join(RESOURCE_DIR, 'images/flathub')
        local = os.path.join(BANNER_DIR, 'banner', 'flathub')
        if os.path.isfile(os.path.join(local, filename)):
            path = local
        return path

    def get_image_file_path(self, content_id):
        path = self.get_image_file_base_dir(content_id)
        return os.path.join(path, content_id + '.png')

    def get_shortcut(self, content):
        shortcut = {
            'name': content.name,
            'hidden': False,
            'cmd': "flatpak run " + content.content_id,
            'dir': "~",
            'tags': list(filter(None, [ "Flathub", status_to_collection_name(content.status) ])),
        }

        for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            img_url = getattr(content, img_type)
            if not img_url:
                continue

            if img_url.startswith('http'):
                img_path = self.get_image_path(content, img_type)
            else:
                img_path = self.get_image_file_path(content.content_id)

            if img_path:
                shortcut[img_type] = img_path

        if content.launch_options:
            shortcut['params'] = content.launch_options

        return shortcut

    def _install(self, content) -> subprocess:
        return subprocess.Popen([FLATPAK_WRAPPER,
                                 "install",
                                 "--user",
                                 "-y",
                                 "flathub",
                                 content.content_id],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

    def _uninstall(self, content_id) -> subprocess:
        return subprocess.Popen([FLATPAK_WRAPPER,
                                 "uninstall",
                                 "--user",
                                 "-y",
                                 content_id],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

    def _update(self, content_id) -> subprocess:
        return subprocess.Popen([FLATPAK_WRAPPER,
                                 "update",
                                 "--user",
                                 "-y",
                                 content_id],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

import subprocess
import json
import os
import chimera_app.context as context
from chimera_app.config import CONTENT_DIR
from chimera_app.platforms.store_platform import StorePlatform, dic


class EpicStore(StorePlatform):
    def __init__(self):
        super().__init__()
        self.platform_code = 'epic-store'
        self.METADATA_DIR = os.path.join(context.CONFIG_HOME,
                                         'legendary',
                                         'metadata')

    def is_authenticated(self):
        return os.path.isfile(os.path.join(context.CONFIG_HOME,
                                           "legendary",
                                           "user.json"))

    def authenticate(self, password):
        subprocess.check_output(["legendary", "auth", "--sid", password])

    def get_shortcut(self, content):
        banner = self.get_banner_path(content)

        shortcut = {
            'name': content.name,
            'hidden': False,
            'banner': banner,
            'cmd': '$(epic-store ' + content.content_id + ')',
            'dir': self.__get_folder_path(content.content_id),
            'tags': ["Epic Games Store"],
            'compat_tool': content.compat_tool or 'proton_7'
        }

        if content.compat_config:
            shortcut['compat_config'] = content.compat_config

        if content.launch_options:
            shortcut['params'] = content.launch_options

        return shortcut

    def __get_installed_content(self) -> list:
        content = {}
        for line in subprocess.check_output(["legendary", "list-installed", "--csv"]).splitlines()[1:]:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            data = line.split(',')

            content[data[0]] = dic({
                                "installed_version": data[2],
                                "available_version": data[3],
                            })

        return content

    def _get_all_content(self) -> list:
        content = []
        installed = self.__get_installed_content()
        for line in subprocess.check_output(["legendary", "list-games", "--csv"]).splitlines()[1:]:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            data = line.split(',')
            if data[3] == 'True':  # exclude DLC
                continue

            epic_id = data[0]

            db = self._get_db_entry('epic-store', epic_id)

            image_url = self.__get_image_url(epic_id)

            is_installed = epic_id in installed
            available_version = data[2]
            installed_version = None
            if is_installed:
                installed_version = installed[epic_id].installed_version
                available_version = installed[epic_id].available_version


            content.append(dic({
                                "content_id": epic_id,
                                "summary": "",
                                "name": data[1],
                                "installed_version": installed_version,
                                "available_version": available_version,
                                "image_url": image_url,
                                "installed": is_installed,
                                "operation": None,
                                "status": db.status,
                                "status_icon": db.status_icon,
                                "notes": db.notes,
                                "compat_tool": db.compat_tool,
                                "compat_config": db.compat_config,
                                "launch_options": db.launch_options
                            }))

        return content

    def __load_metadata(self, content_id):
        with open(os.path.join(self.METADATA_DIR, content_id+'.json')) as f:
            return json.load(f)


    def __get_folder_path(self, content_id):
        metadata = self.__load_metadata(content_id)
        folder_name = metadata['metadata']['customAttributes']['FolderName']['value']
        return os.path.join(CONTENT_DIR, 'epic-store', folder_name)


    def __get_image_url(self, content_id):
        url = self._get_image_url('epic-store', content_id)

        if url:
            return url

        metadata = self.__load_metadata(content_id)
        for img in metadata['metadata']['keyImages']:
            if img['type'] == 'DieselGameBox':
                break

        url = img['url'] + '?h=215&resize=1'

        return url


    def _update(self, content_id) -> subprocess:
        return subprocess.Popen(["legendary", "--yes", "update", content_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _install(self, content) -> subprocess:
        return subprocess.Popen(
            ["legendary", "--yes", "install", "--base-path", os.path.join(CONTENT_DIR, 'epic-store'), content.content_id],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _uninstall(self, content_id) -> subprocess:
        return subprocess.Popen(["legendary", "--yes", "uninstall", content_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

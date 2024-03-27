import subprocess
import json
import os
import chimera_app.context as context
from chimera_app.config import CONTENT_DIR
from chimera_app.platforms.store_platform import StorePlatform, dic
from chimera_app.steam_config import status_to_collection_name


class EpicStore(StorePlatform):
    def __init__(self):
        super().__init__()
        self.platform_code = 'epic-store'
        self.METADATA_DIR = os.path.join(context.CONFIG_HOME,
                                         'legendary',
                                         'metadata')

    def is_authenticated(self):
        output = subprocess.check_output(['legendary', 'status'])
        return '<not logged in>' not in output.decode('utf-8')

    def authenticate(self, password):
        clean_password = password.replace('authorizationCode', '')
        clean_password = ''.join(c for c in clean_password if c.isalnum())
        subprocess.check_output(["legendary", "auth", "--code", clean_password])

    def get_shortcut(self, content):
        # must specify explicit compat_tool proton version for automatic download to work
        shortcut = {
            'name': content.name,
            'hidden': False,
            'cmd': '$(epic-store ' + content.content_id + ')',
            'dir': self.__get_folder_path(content.content_id),
            'tags': list(filter(None, [ "Epic Games Store", status_to_collection_name(content.status) ])),
            'compat_tool': content.compat_tool or 'proton_8'
        }

        for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            img_path = self.get_image_path(content, img_type)
            if img_path:
                shortcut[img_type] = img_path

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

            banner = self.__get_image_url(epic_id, 'banner')
            poster = self.__get_image_url(epic_id, 'poster')
            background = self.__get_image_url(epic_id, 'background')
            logo = self.__get_image_url(epic_id, 'logo')
            icon = self.__get_image_url(epic_id, 'icon')

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
                                "image_url": banner,
                                "banner": banner,
                                "poster": poster,
                                "background": background,
                                "logo": logo,
                                "icon": icon,
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


    def __get_image_url(self, content_id, img_type='banner'):
        url = self._get_image_url('epic-store', content_id, img_type)

        if url:
            return url

        img_key = None
        match img_type:
            case 'banner':
                img_key = 'DieselGameBox'
            case 'logo':
                img_key = 'DieselGameBoxLogo'
            case 'poster':
                img_key = 'DieselGameBoxTall'

        if not img_key:
            return None

        metadata = self.__load_metadata(content_id)
        for img in metadata['metadata']['keyImages']:
            if img['type'] == img_key:
                url = img['url']
                break

        if url and img_key == 'DieselGameBox':
            url += '?h=215&resize=1'

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

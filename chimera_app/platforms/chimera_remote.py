import os
import subprocess
import requests
import tempfile
from typing import List, Dict
from chimera_app.utils import upsert_file
from chimera_app.utils import is_direct
from chimera_app.config import CONTENT_DIR
from chimera_app.config import UPLOADS_DIR
from chimera_app.shortcuts import PlatformShortcutsFile
from chimera_app.platforms.store_platform import StorePlatform, App
from chimera_app.config import PLATFORMS, RESOURCE_DIR, BANNER_DIR, BIN_PATH



class ChimeraRemote(StorePlatform):
    def __init__(self, platform_id, server_ip):
        super().__init__()
        self.platform_id = platform_id
        self.__server_ip = server_ip
        self.__host = f'http://{server_ip}:8844'

    @property
    def platform_code(self):
        return self.platform_id

    def is_authenticated(self):
        return True

    def _get_all_content(self):
        applications = []
        api_response = requests.get(f'{self.__host}/share/platforms/{self.platform_code}', timeout=20)
        if api_response.status_code == requests.codes.ok:
            installed_list = self.__get_installed_list()
            for entry in api_response.json():
                name = entry['name']
                content_filename = entry['content_filename']
                content_download_url = self.__host + entry['content_download_url']
                banner = None
                poster = None
                background = None
                logo = None
                icon = None

                if 'banner' in entry:
                    banner = self.__host + entry['banner']
                if 'poster' in entry:
                    poster = self.__host + entry['poster']
                if 'background' in entry:
                    background = self.__host + entry['background']
                if 'logo' in entry:
                    logo = self.__host + entry['logo']
                if 'icon' in entry:
                    icon = self.__host + entry['icon']

                installed = False
                if name in installed_list:
                    installed = True

                applications.append(App(
                    content_id=name,
                    summary='',
                    name=name,
                    content_filename=content_filename,
                    content_download_url=content_download_url,
                    installed_version=None,
                    available_version=None,
                    image_url=banner,
                    banner=banner,
                    poster=poster,
                    background=background,
                    logo=logo,
                    icon=icon,
                    installed=installed,
                    operation=None,
                    status=None,
                    status_icon=None,
                    notes=None,
                    launch_options=None,
                    native=None,
                    compat_tool=None,
                    compat_config=None
                ))

        return applications

    def __get_installed_list(self) -> List[str]:
        shortcuts_file = PlatformShortcutsFile(self.platform_code)
        installed = shortcuts_file.get_shortcuts_data()
        return [ game['name'] for game in installed if 'deleted' not in game or game['deleted'] != True ]

    def get_shortcut(self, content):
        rundir = os.path.join(CONTENT_DIR, self.platform_code)
        _, content_extension = os.path.splitext(content.content_filename)
        params = f'{content.name}{content_extension}'

        if is_direct(self.platform_code, 'content'):
            rundir = os.path.join(rundir, f'.{self.platform_code}')
            params = content.content_filename

        shortcut = {
            'name': content.name,
            'hidden': False,
            'cmd': PLATFORMS[self.platform_code]['cmd'],
            'dir': f'"{rundir}"',
            'tags': [PLATFORMS[self.platform_code]['name']],
            'params': f'"{params}"',
        }

        for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            img_path = self.get_image_path(content, img_type)
            if img_path:
                shortcut[img_type] = img_path

        return shortcut

    def _install(self, content) -> subprocess.Popen:
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)
        (_, tmp_path) = tempfile.mkstemp(dir=UPLOADS_DIR)
        self.__temp_download_path = tmp_path

        return subprocess.Popen(['curl', '--progress-bar', content.content_download_url, '-o', tmp_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

    def _post_install(self, content_id):
        content = self.get_content(content_id)
        if not content:
            return

        content_path = upsert_file(self.__temp_download_path,
                            CONTENT_DIR,
                            self.platform_code,
                            content.name,
                            content.content_filename)

    def _uninstall(self, content_id) -> None:
        # uninstall handled through regular shortcut deletion i.e. server.py:shortcut_delete
        pass

    def _update(self, content_id) -> None:
        # no updates for regular shortcut files
        pass

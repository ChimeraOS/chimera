import os
import time
import subprocess
import threading
from io import BytesIO
from chimera_app.file_utils import ensure_directory
from chimera_app.config import GAMEDB
from chimera_app.config import BANNER_DIR


# allow accessing dictionary items as object attributes
class dic(object):
    def __init__(self, d):
        self.__dict__ = d

    def get(self, attr, default=None):
        return getattr(self, attr, default)


class StorePlatform:
    def __init__(self):
        self.tasks = {}

    def get_installed_content(self) -> list:
        apps = self._get_all_content()
        return [app for app in apps if app.installed]

    def get_available_content(self, listAll=False) -> list:
        apps = self._get_all_content()
        return [app for app in apps if not app.installed and (listAll or app.status in [ 'verified', 'playable' ]) ]

    def _get_all_content(self) -> list:
        pass

    def get_content(self, content_id):
        app = None
        apps = self.get_installed_content()
        results = list(filter(lambda app: app.content_id == content_id, apps))
        if len(results) > 0:
            app = results[0]

        if not app:
            apps = self.get_available_content(True)
            apps = list(filter(lambda app: app.content_id == content_id, apps))
            if len(apps) < 1:
                return
            app = apps[0]

        app.progress = None
        app.operation = None
        if content_id in self.tasks:
            app.progress = self.tasks[content_id].progress
            app.operation = self.tasks[content_id].operation

        return app

    def create_task(self, content_id, opName):
        if content_id in self.tasks:
            return False
        self.tasks[content_id] = dic({'progress': -1, 'operation': opName})
        return True

    def uninstall_content(self, content_id):
        if self.create_task(content_id, 'Uninstalling'):
            thread = threading.Thread(target=self._update_progress,
                                      args=(self._uninstall(content_id),
                                            content_id))
            thread.start()

    def install_content(self, content):
        if self.create_task(content.content_id, 'Installing'):
            thread = threading.Thread(target=self._update_progress,
                                      args=(self._install(content),
                                            content.content_id))
            thread.start()

    def update_content(self, content_id):
        if self.create_task(content_id, 'Updating'):
            thread = threading.Thread(target=self._update_progress,
                                      args=(self._update(content_id),
                                            content_id))
            thread.start()

    def get_shortcut(self, content):
        pass

    def __get_status_icon(self, status):
        if not status:
            return None

        if status == 'verified':
            return '🟢'
        elif status =='playable':
            return '🟡'
        elif status == 'unsupported':
            return '🔴'
        else:
            return '⚫'

    def _get_db_entry(self, platform, content_id):
        game = {}
        cid = str(content_id)

        if cid in GAMEDB[platform]:
            game = GAMEDB[platform][cid]

        if 'status' not in game:
            game['status'] = 'unknown'

        for key in [ 'notes', 'compat_tool', 'compat_config', 'launch_options' ]:
            if key not in game:
                game[key] = None

        game['status_icon'] = self.__get_status_icon(game['status'])

        return dic(game)

    def _get_image_url(self, platform, content_id, img_type='banner'):
        game = None
        cid = str(content_id)
        img = None

        if cid in GAMEDB[platform]:
            game = GAMEDB[platform][cid]

        if not game:
            return None

        if img_type in game:
            img = game[img_type]
        elif 'banner' in game and game['banner'].startswith('steam:'):
            img = game['banner']

        if img and img.startswith('steam:'):
            steam_id = img.split(':')[1]
            match img_type:
                case 'banner':
                    img = 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + str(steam_id) + '/header.jpg'
                case 'poster':
                    img = 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + str(steam_id) + '/library_600x900_2x.jpg'
                case 'background':
                    img = 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + str(steam_id) + '/library_hero.jpg'
                case 'logo':
                    img = 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + str(steam_id) + '/logo.png'
                case 'icon':
                    img = None

        return img

    def download_images(self, content):
        for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            img_url = getattr(content, img_type)
            if img_url and img_url.startswith('http'):
                img_path = self.get_image_path(content, img_type)
                subprocess.check_output(["curl", img_url, "-o", img_path])

    def __get_ext(self, url):
        url_noquery = url.split('?')[0]
        ext = os.path.splitext(url_noquery)[1]

        if not ext:
            ext = '.jpg'

        return ext

    def get_image_path(self, content, img_type='banner'):
        img_url = getattr(content, img_type)
        if not img_url:
            return None

        ext = self.__get_ext(img_url)
        base_path = os.path.join(BANNER_DIR, img_type, self.platform_code)
        ensure_directory(base_path)

        return os.path.join(base_path, content.content_id + ext)

    def _update_progress(self, sp: subprocess, content_id):
        if sp is None:
            return

        time.sleep(1)

        buf = BytesIO()
        while sp.poll() is None:
            out = sp.stdout.read(1)
            buf.write(out)
            if out in (b'\r', b'\n'):
                for value in buf.getvalue().split():
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    if "%" in value:
                        self.tasks[content_id].progress = int(value.replace("%", "").split('.')[0])
                buf.truncate(0)
        del self.tasks[content_id]

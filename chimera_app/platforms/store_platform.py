import os
import subprocess
import threading
from io import BytesIO
from chimera_app.utils import ensure_directory
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

    def uninstall_content(self, content_id):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._uninstall(content_id),
                                        content_id,
                                        'Uninstalling'))
        thread.start()

    def install_content(self, content):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._install(content),
                                        content.content_id,
                                        'Installing'))
        thread.start()

    def update_content(self, content_id):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._update(content_id),
                                        content_id,
                                        'Updating'))
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

        if 'notes' not in game:
            game['notes'] = None

        game['status_icon'] = self.__get_status_icon(game['status'])

        return dic(game)

    def _get_image_url(self, platform, content_id):
        game = None
        cid = str(content_id)
        img = None

        if cid in GAMEDB[platform]:
            game = GAMEDB[platform][cid]

        if game and 'banner' in game:
            img = game['banner']
            if img.startswith('steam:'):
                steam_id = img.split(':')[1]
                img = 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + str(steam_id) + '/header.jpg'

        return img

    def download_banner(self, content):
        if not content.image_url or not content.image_url.startswith('http'):
            return

        base_path = os.path.join(BANNER_DIR, self.platform_code)
        ensure_directory(base_path)

        img_path = self.get_banner_path(content)
        subprocess.check_output(["curl", content.image_url, "-o", img_path])

    def get_banner_path(self, content):
        base_path = os.path.join(BANNER_DIR, self.platform_code)
        ext = os.path.splitext(content.image_url)[1]

        return os.path.join(base_path, content.content_id + ext)

    def _update_progress(self, sp: subprocess, content_id, opName):
        if content_id in self.tasks or sp is None:
            return
        task = dic({'progress': -1, 'operation': opName})
        self.tasks[content_id] = task
        buf = BytesIO()
        while sp.poll() is None:
            out = sp.stdout.read(1)
            buf.write(out)
            if out in (b'\r', b'\n'):
                for value in buf.getvalue().split():
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    if "%" in value:
                        task.progress = int(value.replace("%", "").split('.')[0])
                buf.truncate(0)
        del self.tasks[content_id]

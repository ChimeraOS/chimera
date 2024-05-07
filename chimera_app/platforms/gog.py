import subprocess
import json
import os
import shutil
import chimera_app.context as context
from chimera_app.file_utils import ensure_directory
from chimera_app.config import CONTENT_DIR
from chimera_app.shortcuts import PlatformShortcutsFile
from chimera_app.platforms.store_platform import StorePlatform, dic
from chimera_app.steam_config import status_to_collection_name


class GOG(StorePlatform):
    def __init__(self):
        super().__init__()
        self.platform_code = 'gog'

    def is_authenticated(self):
        num_lines = 0
        path = os.path.join(context.CONFIG_HOME, "wyvern", "wyvern.toml")
        if os.path.exists(path):
            num_lines = sum(1 for line in open(path))

        if num_lines > 1:
            return True

        return False

    def authenticate(self, password):
        subprocess.check_output(["wyvern", "login", "--code", password])

    def get_shortcut(self, content):
        game_dir = os.path.join(CONTENT_DIR, 'gog', content.content_id)

        shortcut = {
            'id': content.content_id,
            'name': content.name,
            'hidden': False,
            'cmd': '$(gog-launcher {id})'.format(id=content.content_id),
            'dir': game_dir,
            'tags': list(filter(None, [ "GOG", status_to_collection_name(content.status) ])),
        }

        for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            img_path = self.get_image_path(content, img_type)
            if img_path:
                shortcut[img_type] = img_path

        if not content.native:
            # must specify explicit compat_tool proton version for automatic download to work
            shortcut['compat_tool'] = content.compat_tool or 'proton_9'

            if content.compat_config:
                shortcut['compat_config'] = content.compat_config

        if content.launch_options:
            shortcut['params'] = content.launch_options

        return shortcut

    def _get_all_content(self) -> list:
        content = []

        shortcuts_file = PlatformShortcutsFile('gog')
        installed = shortcuts_file.get_shortcuts_data()
        installed_ids = [ game['id'] for game in installed if 'deleted' not in game or game['deleted'] != True ]

        text = subprocess.check_output(["wyvern", "ls", "--json"])
        data = json.loads(text)

        games = sorted(data['games'], key=lambda g: g['ProductInfo']['title'])
        for game in games:
            info = dic(game['ProductInfo'])
            if not info.isGame:
                continue

            cid = str(info.id)

            banner = self._get_image_url('gog', cid, 'banner')
            poster = self._get_image_url('gog', cid, 'poster')
            background = self._get_image_url('gog', cid, 'background')
            logo = self._get_image_url('gog', cid, 'logo')
            icon = self._get_image_url('gog', cid, 'icon')

            default_img = 'https:{img}_product_tile_256_2x.png'.format(img=info.image)

            if not banner:
                banner = default_img

            if not poster:
                poster = default_img


            db = self._get_db_entry('gog', cid)

            content.append(dic({"content_id": cid,
                                "summary": "",
                                "name": info.title,
                                "native": False,
                                "installed_version": None,
                                "available_version": None,
                                "image_url": banner,
                                "banner": banner,
                                "poster": poster,
                                "background": background,
                                "logo": logo,
                                "icon": icon,
                                "installed": cid in installed_ids,
                                'operation': None,
                                "status": db.status,
                                "status_icon": db.status_icon,
                                "notes": db.notes,
                                "compat_tool": db.compat_tool,
                                "compat_config": db.compat_config,
                                "launch_options": db.launch_options
                            }))

        return content

    def _update(self, content_id) -> subprocess:
        pass

    def _install(self, content) -> subprocess:
        cachedir = os.path.join(context.CACHE_HOME, 'chimera')
        shutil.rmtree(cachedir, ignore_errors=True)
        ensure_directory(cachedir)

        if not content.native:
            cmd = [os.path.join(BIN_PATH, 'gog-install'),
                   content.content_id,
                   os.path.join(CONTENT_DIR, 'gog', content.content_id)]
            return subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

        cmd = ["wyvern",
               "down",
               "--id",
               content.content_id,
               "--install",
               os.path.join(CONTENT_DIR, 'gog', content.content_id)]
        return subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                cwd=cachedir)

    def _uninstall(self, content_id) -> subprocess:
        game_dir = os.path.join(CONTENT_DIR, 'gog', content_id)
        return subprocess.Popen(["rm",
                                 "-rf",
                                 game_dir],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

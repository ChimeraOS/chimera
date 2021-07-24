import subprocess
import json
import os
import shutil
from io import BytesIO
from chimera_app.utils import ChimeraContext
from chimera_app.utils import ensure_directory
from chimera_app.utils import file_exists
from chimera_app.config import CONTENT_DIR
from chimera_app.config import BANNER_DIR
from chimera_app.platforms.store_platform import StorePlatform, dic
from chimera_app.functions import load_shortcuts


class GOG(StorePlatform):
    def is_authenticated(self):
        num_lines = 0
        se = ChimeraContext()
        path = os.path.join(se.CONFIG_HOME, "wyvern", "wyvern.toml")
        if file_exists(path):
            num_lines = sum(1 for line in open(path))

        if num_lines > 1:
            return True

        return False

    def authenticate(self, password):
        subprocess.check_output(["wyvern", "login", "--code", password])

    def get_shortcut(self, content):
        ext = '.png'
        base_path = os.path.join(BANNER_DIR, 'gog/')
        ensure_directory(base_path)

        img_path = base_path + content.content_id + ext
        subprocess.check_output(["curl", content.image_url, "-o", img_path])

        game_dir = os.path.join(CONTENT_DIR, 'gog', content.content_id)

        return {
            'name': content.name,
            'hidden': False,
            'banner': img_path,
            'cmd': '$(gog-launcher {id})'.format(id=content.content_id),
            'dir': game_dir,
            'tags': ["GOG"],
            'compat_tool': None if content.native else 'proton_63',
            'id': content.content_id
        }

    def get_installed_content(self) -> list:
        games = self.__get_all_content()
        return [game for game in games if game.installed == True]


    def get_available_content(self) -> list:
        games = self.__get_all_content()
        return [game for game in games if game.installed == False]


    def __get_all_content(self) -> list:
        content = []

        installed = load_shortcuts('gog')
        installed_ids = [game['id'] for game in installed]

        text = subprocess.check_output(["wyvern", "ls", "--json"])
        data = json.loads(text)

        games = sorted(data['games'], key=lambda g: g['ProductInfo']['title'])
        for game in games:
            info = dic(game['ProductInfo'])
            if not info.isGame:
                continue

            cid = str(info.id)

            img = 'https:{img}_product_tile_256_2x.png'.format(img=info.image)
            content.append(dic({ "content_id": cid, "summary": "", "name": info.title, "native": info.worksOn['Linux'], "installed_version": None, "available_version": None, "image_url": img, "installed": cid in installed_ids, 'operation' : None }))

        return content

    def _update(self, content_id) -> subprocess:
        pass

    def _install(self, content) -> subprocess:
        se = ChimeraContext()
        cachedir = os.path.join(se.CACHE_HOME, 'chimera')
        shutil.rmtree(cachedir, ignore_errors=True)
        ensure_directory(cachedir)

        if not content.native:
            cmd = ["bin/gog-install", content.content_id, os.path.join(CONTENT_DIR, 'gog', content.content_id)]
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        cmd = ["wyvern", "down", "--id", content.content_id, "--install", os.path.join(CONTENT_DIR, 'gog', content.content_id)]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cachedir)

    def _uninstall(self, content_id) -> subprocess:
        game_dir = os.path.join(CONTENT_DIR, 'gog', content_id)
        return subprocess.Popen(["rm", "-rf", game_dir],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

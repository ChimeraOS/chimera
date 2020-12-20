import subprocess
import json
import os
import glob
import shutil
from io import BytesIO
from steam_buddy.config import CACHE_DIR, CONFIG_DIR, BANNER_DIR, CONTENT_DIR
from steam_buddy.platforms.store_platform import StorePlatform, dic
from steam_buddy.functions import load_shortcuts



class GOG(StorePlatform):
    def is_authenticated(self):
        num_lines = 0
        path = os.path.join(CONFIG_DIR, "wyvern", "wyvern.toml")
        if os.path.isfile(path):
            num_lines = sum(1 for line in open(path))

        if num_lines > 1:
            return True

        return False

    def authenticate(self, password):
        subprocess.check_output(["wyvern", "login", "--code", password])

    def get_shortcut(self, content):
        ext = '.png'
        base_path = os.path.join(BANNER_DIR, 'gog/')
        try:
            os.makedirs(base_path)
        except:
            pass

        img_path = base_path + content.content_id + ext
        subprocess.check_output(["curl", content.image_url, "-o", img_path ])

        game_dir = os.path.join(CONTENT_DIR, 'gog', content.content_id)

        return {
            'name': content.name,
            'hidden': False,
            'banner': img_path,
            'cmd': '$(gog-launcher {id})'.format(id=content.content_id),
            'dir': game_dir,
            'tags': ["GOG"],
            'compat_tool': None if content.native else 'proton_513',
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
        cachedir = os.path.join(CACHE_DIR, 'steam-buddy')
        try:
            shutil.rmtree(cachedir)
        except:
            pass
        try:
            os.mkdir(cachedir)
        except:
            pass

        if not content.native:
            cmd = ["bin/gog-install", content.content_id, os.path.join(CONTENT_DIR, 'gog', content.content_id)]
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        cmd = ["wyvern", "down", "--id", content.content_id, "--install", os.path.join(CONTENT_DIR, 'gog', content.content_id)]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cachedir)

    def _uninstall(self, content_id) -> subprocess:
        game_dir = os.path.join(CONTENT_DIR, 'gog', content_id)
        return subprocess.Popen(["rm", "-rf", game_dir],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
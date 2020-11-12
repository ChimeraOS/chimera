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
        return True

    def authenticate(self, password):
        pass

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
            'cmd': '$(gog {id})'.format(id=content.content_id),
            'dir': game_dir,
            'tags': ["GOG"],
            'compat_tool': 'proton_513',
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
            content.append(dic({ "content_id": cid, "summary": "", "name": info.title, "installed_version": None, "available_version": None, "image_url": img, "installed": cid in installed_ids, 'operation' : None }))

        return content

    def _update(self, content_id) -> subprocess:
        pass

    def _install(self, content_id) -> subprocess:
        cachedir = os.path.join(CACHE_DIR, 'steam-buddy')
        try:
            shutil.rmtree(cachedir)
        except:
            pass
        try:
            os.mkdir(cachedir)
        except:
            pass
        cmd = ["wyvern", "down", "--id", content_id, "--install", os.path.join(CONTENT_DIR, 'gog', content_id), "--force-windows"]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cachedir)

    def _uninstall(self, content_id) -> subprocess:
        game_dir = os.path.join(CONTENT_DIR, 'gog', content_id)
        return subprocess.Popen(["rm", "-rf", game_dir],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
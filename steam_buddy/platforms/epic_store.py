import subprocess
import json
import os
from steam_buddy.config import CONFIG_DIR, BANNER_DIR, CONTENT_DIR
from steam_buddy.platforms.store_platform import StorePlatform, dic


METADATA_DIR = os.path.join(CONFIG_DIR, 'legendary', 'metadata')


class EpicStore(StorePlatform):
    def is_authenticated(self):
        return os.path.isfile(os.path.join(CONFIG_DIR, "legendary", "user.json"))

    def authenticate(self, password):
        subprocess.check_output(["legendary", "auth", "--sid", password])

    def get_shortcut(self, content):
        ext = '.jpg'
        base_path = os.path.join(BANNER_DIR, 'epic-store/')
        try:
            os.makedirs(base_path)
        except:
            pass

        img_path = base_path + content.content_id + ext
        subprocess.check_output(["curl", content.image_url, "-o", img_path])

        return {
            'name': content.name,
            'hidden': False,
            'banner': img_path,
            'cmd': '$(epic-store ' + content.content_id + ')',
            'tags': ["Epic Games Store"],
            'compat_tool': 'proton_513'
        }

    def get_installed_content(self) -> list:
        content = []
        for line in subprocess.check_output(["legendary", "list-installed", "--csv"]).splitlines()[1:]:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            data = line.split(',')
            if data[3] == 'True':  # exclude DLC
                continue

            with open(os.path.join(METADATA_DIR, data[0] + '.json')) as f:
                metadata = json.load(f)

            for img in metadata['metadata']['keyImages']:
                if img['type'] == 'DieselGameBox':
                    break

            content.append(dic({"content_id": data[0], "summary": "", "name": data[1], "installed_version": data[2],
                                "available_version": data[3], "image_url": img['url'] + '?h=215&resize=1',
                                "installed": True, 'operation': None}))

        return content

    def get_available_content(self) -> list:
        content = []
        installed = self.get_installed_content()
        installed_ids = [app.content_id for app in installed]
        for line in subprocess.check_output(["legendary", "list-games", "--csv"]).splitlines()[1:]:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            data = line.split(',')
            if data[3] == 'True':  # exclude DLC
                continue
            if data[0] in installed_ids:
                continue

            with open(os.path.join(METADATA_DIR, data[0]+'.json')) as f:
                metadata = json.load(f)

            for img in metadata['metadata']['keyImages']:
                if img['type'] == 'DieselGameBox':
                    break
            content.append(dic({"content_id": data[0], "summary": "", "name": data[1], "installed_version": None,
                                "available_version": data[2], "image_url": img['url'] + '?h=215&resize=1',
                                "installed": False, 'operation': None}))

        return content

    def _update(self, content_id) -> subprocess:
        return subprocess.Popen(["legendary", "--yes", "update", content_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _install(self, content_id) -> subprocess:
        return subprocess.Popen(
            ["legendary", "--yes", "install", "--base-path", os.path.join(CONTENT_DIR, 'epic-store'), content_id],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _uninstall(self, content_id) -> subprocess:
        return subprocess.Popen(["legendary", "--yes", "uninstall", content_id],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

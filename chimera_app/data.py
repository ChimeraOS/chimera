"""Data handling for Chimera app"""
import os
import shutil
import json
import zipfile
import requests
import chimera_app.utils as utils


def update_data(force=False) -> bool:
    dl = Downloader()
    return dl.update(force=force)


class Downloader():
    """Downlaoder for data files from our repository
    Usage:
        dl = Downloader()
        dl.update()

    This will check for updates of the data repository and download it

    Update can be forced by giving the `force` flag:
        dl.update(force=True)
    """

    db_path: str
    channel: str

    def __init__(self,
                 channel='master',
                 db_path='~/.local/share/chimera/data'):
        """Setup this data doenloader with a database directory path"""
        self.channel = channel
        self.db_path = os.path.expanduser(db_path)

    def fetch_latest(self) -> None:
        """Checks online for available branches and version numbers and
        stores it into branches.json file
        """
        api_url = ('https://api.github.com/repos/chimeraos/'
                   'chimera-data/branches')
        resp = requests.get(api_url)
        db_path = os.path.join(self.db_path, "branches.json")
        utils.ensure_directory_for_file(db_path)
        branches = json.loads(resp.json())
        with open(db_path, 'w') as db_file:
            db_file.write(json.dumps(branches, sort_keys=True, indent=4))

    def get_installed(self) -> dict:
        """Returns a dictionary with installed branch and version number."""
        version_path = os.path.join(self.db_path, "versions.json")
        if not os.path.exists(version_path):
            return None

        version = {}
        with open(version_path) as version_file:
            version = json.load(version_file)
        return version

    def get_installed_version(self) -> str:
        """Checks installed data package version."""
        versions = self.get_installed()
        ver = None
        if versions:
            ver = versions['installed']['sha']
        return ver

    def get_available_versions(self) -> list:
        """Checks for available data packages versions."""
        branches_path = os.path.join(self.db_path, "branches.json")
        self.fetch_latest()
        if not os.path.exists(branches_path):
            return None

        versions = []
        with open(branches_path) as branches_file:
            branches = json.load(branches_file)
        for branch in branches:
            versions.append({
                "name": branch['name'],
                "sha": branch['commit']['sha']
                            })
        return versions

    def check_update(self) -> bool:
        available_versions = self.get_available_versions()
        installed_version = self.get_installed_version()
        if not available_versions:
            raise Exception("No available versions upstream")

        if not installed_version:
            return False

        updated = False
        for versions in available_versions:
            if self.channel == versions['name']:
                if (installed_version == versions['sha']):
                    updated = True
        return updated

    def get_update_sha(self) -> str:
        available_versions = self.get_available_versions()
        sha = None
        for versions in available_versions:
            if self.channel == versions['name']:
                sha = versions['sha']
        return sha

    def download_package(self, sha):
        url = ('https://github.com/ChimeraOS/chimera-data/archive/' +
               sha + '.zip')
        resp = requests.get(url, timeout=1)
        if resp.status_code == 200:
            zip_path = os.path.join(self.db_path, "data.zip")
            with open(zip_path, 'wb') as zip_file:
                zip_file.write(resp.content)
        else:
            raise Exception(f"File not found for sha: {sha}")

    def update(self, force=False) -> bool:
        updated = self.check_update()
        if not updated or force:
            self.fetch_latest()
            sha = self.get_update_sha()
            self.download_package(sha)
            zip_path = os.path.join(self.db_path, "data.zip")
            version_path = os.path.join(self.db_path, "versions.json")
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(self.db_path)
            dirname = os.path.join(self.db_path, 'chimera-data-' + sha)
            for data in os.listdir(dirname):
                src_path = os.path.join(dirname, data)
                dest_path = os.path.join(self.db_path, data)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path,
                                    dest_path,
                                    dirs_exist_ok=True)
                elif os.path.isfile(src_path):
                    shutil.copyfile(src_path, dest_path)
            shutil.rmtree(dirname)
            with open(version_path, 'w') as version_file:
                ver_content = {"installed":
                               {
                                   "name": self.channel,
                                   "sha": sha
                                }
                               }
                version_file.write(json.dumps(ver_content,
                                              sort_keys=True,
                                              indent=4)
                                   )
            updated = True
        return updated

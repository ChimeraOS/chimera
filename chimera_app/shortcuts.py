"""Module to manage shortcuts in the entire chimera toolset"""

import os
from typing import List
from datetime import date
from zlib import crc32
import vdf
import yaml
import chimera_app.context as context
import chimera_app.utils as utils
import chimera_app.steam_config as steam_config
from chimera_app.steam_collections import SteamCollections
from chimera_app.file_utils import ensure_directory_for_file


STATUS_TAGS = [ 'ChimeraOS Verified', 'ChimeraOS Playable', 'ChimeraOS Unsupported' ]

# a list of migrated commands: keys correspond to the command that was migrated to and values correspond to the previous command that was migrated away from
MIGRATIONS = { 'spsp' : 'psp' }


def create_all_shortcuts():
    """Convenience function to create all shortcuts with default parameters"""
    if not os.path.isdir(context.SHORTCUT_DIRS):
        print(f'Shortcuts directory does not exist ({context.SHORTCUT_DIRS})')
        return

    manager = ShortcutsManager()
    for user_dir in context.STEAM_USER_DIRS:
        # Should change the STEAM_USER_DIRS into USER_IDS
        manager.add_steam_file_for_user(os.path.basename(user_dir))

    for file in os.scandir(context.SHORTCUT_DIRS):
        if file.is_file():
            manager.add_shortcuts_file_from_path(file.path)

    manager.load_shortcut_entries()
    manager.create_shortcuts()
    manager.prune_deleted_shortcuts()
    manager.create_images()
    manager.register_compat_data()


def get_bpmbanner_id(exe, name):
    """Returns a full 64 bit crc to match banner file names"""
    crc_input = ''.join([exe, name])
    high_32 = crc32(crc_input.encode('utf-8')) | 0x80000000
    full_64 = (high_32 << 32) | 0x02000000
    return full_64


def get_compat_id(exe, name):
    """Returns the lower 32 bits of unsigned the appid. Used for compat
    tool matching
    """
    crc_input = ''.join([exe, name])
    return (crc32(crc_input.encode('utf-8')) & 0xffffffff) | 0x80000000


def get_shortcut_id(exe, name):
    """Returns the lower 32 bits of signed appid. Used for matching
    existing apps.
    """
    return get_compat_id(exe, name) - 2**32


def get_banner_id(exe, name):
    return str(get_compat_id(exe, name))


def get_poster_id(exe, name):
    return str(get_compat_id(exe, name)) + 'p'


def get_background_id(exe, name):
    return str(get_compat_id(exe, name)) + '_hero'


def get_logo_id(exe, name):
    return str(get_compat_id(exe, name)) + '_logo'


def get_image_id(type, exe, name):
    if type == 'bpmbanner':
        return get_bpmbanner_id(exe, name)
    elif type == 'banner':
        return get_banner_id(exe, name)
    elif type == 'poster':
        return get_poster_id(exe, name)
    elif type == 'background':
        return get_background_id(exe, name)
    elif type == 'logo':
        return get_logo_id(exe, name)


class SteamShortcutsFile():
    """Class to manage Steam shortcuts files for users"""

    path: str
    tags: dict
    user_id: str
    current_data: dict

    def __init__(self, user_id: str, auto_load: bool = True):
        self.user_id = user_id
        self.path = os.path.join(context.STEAM_DIR,
                                 'userdata',
                                 user_id,
                                 'config/shortcuts.vdf')
        self.current_data = {}
        self.tags = {}
        if auto_load:
            self.load_data()

    def exists(self) -> bool:
        """Returns True if this file exists. False otherwise"""
        return os.path.exists(self.path)

    def get_current_data(self) -> dict:
        """Returns this file's shortcut data as a list of dictionaries"""
        return self.current_data

    def load_data(self) -> None:
        """Reads shortcut data from this file. It returns a dictionary
        with the data. If the file does not exists, it will load an empty
        dictionary.
        """
        if not self.exists():
            self.current_data = {}
            return

        with open(self.path, 'rb') as vdf_file:
            data = vdf.binary_load(vdf_file)
            if 'shortcuts' in data:
                self.current_data = data['shortcuts']

    def match_app_id(self, app_id: str) -> dict:
        """Returns a copy of the shortcut dictionary of the given app_id.
        If not found returns a new empty dictionary.
        """
        if not self.current_data:
            self.load_data()

        data = self.current_data
        # Match shortcut dictionary and return a copy of it
        for index in data:
            entry = data[index]
            if 'appid' in entry and entry['appid'] == app_id:
                return entry.copy(), index

        # for new entries
        return {}, len(self.current_data)

    def save(self) -> None:
        """Save current file with current shortcuts data"""
        out = {}
        data = {}
        for index in self.current_data:
            data[str(index)] = self.current_data[index]
        out['shortcuts'] = data
        ensure_directory_for_file(self.path)
        with open(self.path, 'wb') as ss_file:
            ss_file.write(vdf.binary_dumps(out))

        col = SteamCollections(self.user_id)
        col.open()

        # clear all status tags for all games we are about to add - prevents games from having multiple statuses after status changes
        for xtag in STATUS_TAGS:
            for ytag in STATUS_TAGS:
                if ytag in self.tags:
                    col.remove(xtag, self.tags[ytag])

        for tag in self.tags:
            col.add(tag, self.tags[tag])
        col.save()

    def tag(self, tag, appid):
        if tag not in self.tags:
            self.tags[tag] = []
        self.tags[tag].append(appid)

    def add_shortcut(self, entry: dict):
        """Creates a new shortcut with given dictionary. Will try to match
        with an existing shortcut in this file. If no existing shortcut can
        be found, then create a new entry.
        """
        if 'name' not in entry:
            raise Exception('Entry missing required field "name".')
        if 'cmd' not in entry:
            raise Exception('Entry missing required field "cmd".')

        # remove old shortcuts after a change in 'cmd' which causes the game's id to change and matching to fail resulting in duplicate shortcuts
        if entry['cmd'] in MIGRATIONS.keys():
            shortcut_id = get_shortcut_id(MIGRATIONS[entry['cmd']], entry['name'])
            shortcut, index = self.match_app_id(shortcut_id)
            if shortcut:
                self.current_data.pop(index)

        shortcut_id = get_shortcut_id(entry['cmd'], entry['name'])
        shortcut, index = self.match_app_id(shortcut_id)

        if 'deleted' in entry and entry['deleted']:
            if shortcut:
                self.current_data.pop(index)
            return

        if 'hidden' in entry and entry['hidden']:
            if shortcut:
                self.current_data.pop(index)
            return

        shortcut['appid'] = shortcut_id
        shortcut['AppName'] = entry['name']
        shortcut['Exe'] = entry['cmd']
        shortcut['AllowDesktopConfig'] = 1
        shortcut['AllowOverlay'] = 1
        shortcut['OpenVR'] = 0

        if 'dir' in entry:
            shortcut['StartDir'] = entry['dir']
        else:
            shortcut['StartDir'] = "~"

        if 'params' in entry:
            shortcut['LaunchOptions'] = entry['params']

        if 'hidden' in entry:
            shortcut['isHidden'] = entry['hidden']

        if 'icon' in entry:
            shortcut['icon'] = entry['icon']

        if 'tags' not in shortcut:
            shortcut['tags'] = {}

        if 'tags' not in entry:
            entry['tags'] = []

        # preserve all tags except the status tags (to allow changes to status to be reflected)
        shortcut_tags = list(set(shortcut['tags'].values()) - set(STATUS_TAGS))

        TIME_WARP_TAG = 'Time Warp'
        TIME_WARP_DATE = None

        if context.TIME_WARP:
            TIME_WARP_DATE = utils.yearsago(int(context.TIME_WARP)).isoformat()

        if TIME_WARP_DATE:
            # handle the case where the time warp or release dates changed;
            # i.e. need to be able to remove the tag
            if TIME_WARP_TAG in shortcut_tags:
                shortcut_tags.remove(TIME_WARP_TAG)

            release_date = (entry['release_date']
                            if 'release_date' in entry
                            else None)
            if type(release_date) is date:
                release_date = release_date.isoformat()

            if type(release_date) is int:
                release_date = str(release_date)

            if (release_date and type(release_date) is str and
                    release_date <= TIME_WARP_DATE):
                entry['tags'].append(TIME_WARP_TAG)

        entry['tags'].extend(shortcut_tags)
        tags = set(entry['tags'])
        t = 0
        shortcut['tags'] = {}
        for tag in tags:
            self.tag(tag, get_compat_id(entry['cmd'], entry['name']))
            shortcut['tags'][str(t)] = tag
            t += 1

        self.current_data[index] = shortcut


class ShortcutsFile():
    """Class for managing our yaml shortcuts file"""

    path: str
    shortcuts_data: List[dict]

    def __init__(self, path: str, auto_load: bool = True):
        self.path = path
        self.shortcuts_data = []
        if auto_load:
            self.load_data()

    def exists(self) -> bool:
        """Returns true if this file exists. False otherwise"""
        return os.path.exists(self.path)

    def get_shortcuts_data(self) -> List[dict]:
        """Returns this file shortcuts in a list of dictionaries"""
        return self.shortcuts_data

    def load_data(self) -> None:
        """Load shortcuts from this file"""
        if not self.exists():
            self.shortcuts_data = []
            return

        with open(self.path) as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            if isinstance(data, dict):
                data = [data]
        self.shortcuts_data = data

    def add_shortcut(self, shortcut: dict) -> None:
        """Add a shortcut to the end of the shortcuts data list"""
        if 'name' not in shortcut or 'cmd' not in shortcut:
            raise Exception(f'Passed shortcut is not valid: {shortcut}')

        existing_shortcut = self.get_shortcut_match(shortcut['name'])
        is_existing_shortcut_marked_deleted = 'deleted' in existing_shortcut and existing_shortcut['deleted'] == True
        if existing_shortcut and not is_existing_shortcut_marked_deleted:
            raise Exception(f"File {self.path} already has a shortcut with "
                            f"name {shortcut['name']}")

        if existing_shortcut:
            self.shortcuts_data.remove(existing_shortcut)
        self.shortcuts_data.append(shortcut)

    def get_shortcut_match(self, name: str) -> dict:
        """Return a shortcut dictionary that matches 'name'.
        Returns empty if not found.
        """
        for s in self.shortcuts_data:
            if s['name'] == name:
                return s
        return {}

    def remove_shortcut(self, name: str) -> None:
        """Remove a shortcut that has a given 'name'"""
        for shortcut in self.shortcuts_data:
            if name == shortcut['name']:
                shortcut['deleted'] = True
                break

    def prune_deleted(self) -> None:
        """Prune any shortcuts marked deleted"""
        for shortcut in self.shortcuts_data:
            if 'deleted' in shortcut and shortcut['deleted'] == True:
                self.shortcuts_data.remove(shortcut)

    def save(self) -> None:
        """Save this file with current shortcuts data"""
        ensure_directory_for_file(self.path)
        with open(self.path, 'w') as file:
            yaml.dump(self.get_shortcuts_data(),
                      file,
                      default_flow_style=False)


class PlatformShortcutsFile(ShortcutsFile):
    """Manage a shortcuts file created for a specific platform"""

    platform: str

    def __init__(self, platform: str, auto_load: bool = True):
        self.platform = platform
        path = os.path.join(context.SHORTCUT_DIRS, f'chimera.{platform}.yaml')
        super().__init__(path, auto_load)


class ShortcutsManager():
    """Class to manage Shortcuts files and shortcut creation"""

    steam_files: List[SteamShortcutsFile]
    shortcut_files: List[ShortcutsFile]
    shortcut_entries: List[dict]

    def __init__(self,
                 steam_files: List[SteamShortcutsFile] = None,
                 shortcut_files: List[ShortcutsFile] = None):
        self.steam_files = steam_files if steam_files else []
        self.shortcut_files = shortcut_files if shortcut_files else []
        self.shortcut_entries = []

    def get_steam_files(self) -> List[SteamShortcutsFile]:
        """Returns the steam shortcuts files list"""
        return self.steam_files

    def get_shortcuts_files(self) -> List[ShortcutsFile]:
        """Returns the shortcuts files list"""
        return self.shortcut_files

    def add_steam_file(self, steam_file: SteamShortcutsFile) -> None:
        """Add a steam shortcut file to this manager"""
        self.steam_files.append(steam_file)

    def add_shortcuts_file(self, shortcuts_file: ShortcutsFile) -> None:
        """Add a shortcut file to this manager"""
        self.shortcut_files.append(shortcuts_file)

    def add_steam_file_for_user(self, user_id: str) -> None:
        """Add a steam shortcuts file for given user_id"""
        self.add_steam_file(SteamShortcutsFile(user_id))

    def add_shortcuts_file_from_path(self, path: str) -> None:
        """Add a shortcuts file for given path"""
        self.add_shortcuts_file(ShortcutsFile(path))

    def load_shortcut_entries(self) -> None:
        """Load all shortcuts files into entries"""
        for f in self.shortcut_files:
            f.load_data()
            self.shortcut_entries = (self.shortcut_entries
                                     + f.get_shortcuts_data())

    def prune_deleted_shortcuts(self) -> None:
        """Drop shortcuts marked as deleted from all YAML files"""
        for f in self.shortcut_files:
            f.load_data()
            f.prune_deleted()
            f.save()

    def create_shortcuts(self) -> None:
        """Create all shortcuts for current entries"""
        if not self.shortcut_entries:
            return

        for steam_file in self.steam_files:
            for entry in self.shortcut_entries:
                steam_file.add_shortcut(entry)
            steam_file.save()

    def create_image(self, entry, img_type_src, img_type_dst = None) -> None:
        if img_type_src not in entry:
            return

        if not img_type_dst:
            img_type_dst = img_type_src

        img_path = entry[img_type_src]
        img_id = get_image_id(img_type_dst, entry['cmd'], entry['name'])
        _, ext = os.path.splitext(img_path)
        for user_dir in context.STEAM_USER_DIRS:
            dst_dir = user_dir + '/config/grid/'
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            dst = dst_dir + str(img_id) + ext
            if os.path.islink(dst) or os.path.isfile(dst):
                os.remove(dst)
            os.symlink(img_path, dst)

    def create_images(self) -> None:
        """Create all image files for current entries"""
        if not self.shortcut_entries:
            return

        for entry in self.shortcut_entries:
            self.create_image(entry, 'banner', 'bpmbanner')
            self.create_image(entry, 'banner')
            self.create_image(entry, 'poster')
            self.create_image(entry, 'background')
            self.create_image(entry, 'logo')

    def register_compat_data(self) -> None:
        """Register all compatibility tools mapping for current entries"""
        compat_data = {}
        for entry in self.shortcut_entries:
            compat_id = get_compat_id(entry['cmd'], entry['name'])
            if 'compat_tool' in entry:
                if compat_id not in compat_data:
                    compat_data[compat_id] = {}
                compat_data[compat_id]['compat_tool'] = entry['compat_tool']
                if 'compat_config' in entry:
                    (compat_data[compat_id]
                                ['compat_config']) = entry['compat_config']

        config_file = steam_config.MainSteamConfig(auto_load=True)
        config_file.apply_tweaks(compat_data, priority=209)
        config_file.save()

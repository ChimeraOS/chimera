"""Module to manage shortcuts in the entire chimera toolset"""

import os
from datetime import date
from zlib import crc32
import vdf
import yaml
import chimera_app.context as context
from chimera_app.utils import yearsago


def create_all_shortcuts():
    """Convenience function to create all shortcuts with default parameters"""
    if (not os.path.isdir(context.SHORTCUT_DIRS)):
        print(f'Shortcuts directory does not exist ({context.SHORTCUT_DIRS})')
        return
    shortcuts = ChimeraShortcuts()
    shortcuts.get_all_shortcuts()
    shortcuts.write_all_shortcuts()


class ChimeraShortcuts:
    """This class is a collection of functions to manage shortcuts in the
    chimera toolset.
    """

    def __init__(self):
        self.shortcuts = None
        self.steam_shortcuts = None

    def get_all_shortcuts(self):
        data = []
        d = context.SHORTCUT_DIRS
        for f in os.listdir(d):
            file_name = os.path.join(d, f)
            data = data + self.load_shortcuts(file_name)
        self.shortcuts = data

    def write_all_shortcuts(self):
        if not self.shortcuts:
            return

        compat_data = {}
        # Get current shortcuts for each user
        for user_dir in context.STEAM_USER_DIRS:
            steam_shortcuts = self.get_steam_shortcuts(user_dir)

            sdict = {}
            n = 0
            for entry in self.shortcuts:
                s, c = ChimeraShortcuts.create_shortcut(entry,
                                                        steam_shortcuts)
                sdict[str(n)] = s
                compat_data.update(c)
                n += 1
            self.write_shortcuts(user_dir, sdict)

        yaml.dump(compat_data,
                  open(context.COMPAT_DATA_FILE, 'w'),
                  default_flow_style=False)

    @staticmethod
    def get_steam_shortcuts(user_dir):
        ss_file = user_dir + '/config/shortcuts.vdf'
        return ChimeraShortcuts.load_steam_shortcuts(ss_file)

    @staticmethod
    def write_shortcuts(user_dir, shortcuts):
        ss_file = user_dir + '/config/shortcuts.vdf'
        out = {}
        out['shortcuts'] = shortcuts
        file = open(ss_file, 'wb')
        file.write(vdf.binary_dumps(out))
        file.close()

    @staticmethod
    def get_banner_id(exe, name):
        """Returns a full 64 bit crc to match banner file names"""
        crc_input = ''.join([exe, name])
        high_32 = crc32(crc_input.encode('utf-8')) | 0x80000000
        full_64 = (high_32 << 32) | 0x02000000
        return full_64

    @staticmethod
    def get_compat_id(exe, name):
        """Returns the lower 32 bits of unsigned the appid. Used for compat
        tool matching
        """
        crc_input = ''.join([exe, name])
        return (crc32(crc_input.encode('utf-8')) & 0xffffffff) | 0x80000000

    @staticmethod
    def get_shortcut_id(exe, name):
        """Returns the lower 32 bits of signed appid. Used for matching
        existing apps.
        """
        return ChimeraShortcuts.get_compat_id(exe, name) - 2**32

    @staticmethod
    def load_shortcuts(yaml_file):
        """Reads shortcut data from yaml files. Can be used with a single
        file or a list. Returns a list of dictionaries with all read shortcut
        definitions.
        """
        data = []
        if os.path.exists(yaml_file):
            data = yaml.load(open(yaml_file, 'r'), Loader=yaml.FullLoader)
            if isinstance(data, dict):
                data = [data]
        return data

    @staticmethod
    def load_steam_shortcuts(vdf_file):
        """Reads shortcut data from a vdf file. It returns a dictionary
        with the data.
        """
        data = {}
        if os.path.exists(vdf_file):
            s = vdf.binary_load(open(vdf_file, 'rb'))
            if 'shortcuts' in s:
                data = s['shortcuts']
        return data

    @staticmethod
    def match_app_id(sc, app_id):
        """Returns the shortcut dictionary of the given app_id.
        If not found returns {}
        """
        for s in sc:
            if 'appid' in sc[s] and sc[s]['appid'] == app_id:
                return sc[s]
        return {}

    @staticmethod
    def create_shortcut(entry, steam_shortcuts):
        """Returns a new shortcut and compat_data dictionary that can be
        written later on the shortcut.vdf file and corresponding compat_data
        yaml file.
        If an application exists with the same app ID in the file, tries
        to update it.
        """
        if 'name' not in entry:
            print('shortcut missing required field "name"; skipping')
            return
        if 'cmd' not in entry:
            print('shortcut missing required field "cmd"; skipping')
            return

        shortcut_id = ChimeraShortcuts.get_shortcut_id(entry['cmd'],
                                                       entry['name'])
        banner_id = str(ChimeraShortcuts.get_banner_id(entry['cmd'],
                                                       entry['name']))
        compat_id = str(ChimeraShortcuts.get_compat_id(entry['cmd'],
                                                       entry['name']))

        shortcut = ChimeraShortcuts.match_app_id(steam_shortcuts, shortcut_id)
        shortcut['appid'] = shortcut_id
        shortcut['AppName'] = entry['name']
        shortcut['Exe'] = entry['cmd']

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

        shortcut['AllowDesktopConfig'] = 1
        shortcut['AllowOverlay'] = 1
        shortcut['OpenVR'] = 0

        if 'tags' not in shortcut:
            shortcut['tags'] = {}

        if 'tags' not in entry:
            entry['tags'] = []

        shortcut_tags = list(shortcut['tags'].values())

        TIME_WARP_TAG = 'Time Warp'
        TIME_WARP_DATE = None

        if context.TIME_WARP:
            TIME_WARP_DATE = yearsago(int(context.TIME_WARP)).isoformat()

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
            shortcut['tags'][str(t)] = tag
            t += 1

        if 'banner' in entry:
            _, ext = os.path.splitext(entry['banner'])
            for user_dir in context.STEAM_USER_DIRS:
                dst_dir = user_dir + '/config/grid/'
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                dst = dst_dir + banner_id + ext
                if os.path.islink(dst) or os.path.isfile(dst):
                    os.remove(dst)
                os.symlink(entry['banner'], dst)

        compat_data = {}
        if 'compat_tool' in entry:
            if compat_id not in compat_data:
                compat_data[compat_id] = {}
            compat_data[compat_id]['compat_tool'] = entry['compat_tool']
            if 'compat_config' in entry:
                (compat_data[compat_id]
                            ['compat_config']) = entry['compat_config']

        return shortcut, compat_data

"""Submodule to handle Steam configuration files related functions"""

import os
from abc import ABC
from abc import abstractmethod
import vdf
import yaml
import chimera_app.context as context
from chimera_app.config import GAMEDB
from chimera_app.file_utils import ensure_directory_for_file
from chimera_app.steam_collections import SteamCollections


def status_to_collection_name(status):
    if not status:
        return None
    elif status == 'verified':
        return 'ChimeraOS Verified'
    elif status == 'playable':
        return 'ChimeraOS Playable'
    elif status == 'unsupported':
        return 'ChimeraOS Unsupported'

    return None

def apply_status_collections(db, user_id):
    col = SteamCollections(user_id)
    col.open()
    for game_id in db:
        col.remove(status_to_collection_name('verified'), [ int(game_id) ] )
        col.remove(status_to_collection_name('playable'), [ int(game_id) ] )
        col.remove(status_to_collection_name('unsupported'), [ int(game_id) ] )
        if 'status' in db[game_id]:
            col_name = status_to_collection_name(db[game_id]['status'])
            if col_name:
                col.add(col_name, [ int(game_id) ])
    col.save()


def apply_all_tweaks():
    """Apply all tweaks if tweaks files exist"""
    if not GAMEDB or 'steam' not in GAMEDB:
        print('No tweaks to apply')
        return

    main_config = MainSteamConfig(auto_load=True)
    main_config.apply_tweaks(GAMEDB['steam'], priority=209)
    main_config.save()

    for user_dir in context.STEAM_USER_DIRS:
        user_id = os.path.basename(user_dir)
        user_config = LocalSteamConfig(user_id)
        user_config.apply_tweaks(GAMEDB['steam'])
        user_config.save()
        apply_status_collections(GAMEDB['steam'], user_id)


class TweaksFile:
    """Manage a tweaks file"""

    path: str
    tweaks_data: dict

    def __init__(self, path: str, auto_load=False):
        self.path = path
        self.tweaks_data = None
        if auto_load:
            self.load_data()

    def exists(self) -> bool:
        """Returns True if this tweaks file exists"""
        return os.path.exists(self.path)

    def load_data(self) -> None:
        """Load this file's data"""
        if not self.exists():
            return
        with open(self.path) as file:
            self.tweaks_data = yaml.load(file, Loader=yaml.FullLoader)

    def get_data(self) -> dict:
        """Return this file's data as a dictionary"""
        if not self.tweaks_data:
            self.load_data()
        return self.tweaks_data


class SteamConfigFile(ABC):
    """Class to represent a Steam configuration file"""

    path: str
    config_data: vdf.VDFDict

    def __init__(self, path: str, auto_load=False):
        self.path = path
        self.config_data = None
        if auto_load:
            self.load_data()

    def exists(self) -> bool:
        """Returns True if the file exists, False otherwise"""
        return os.path.exists(self.path)

    @abstractmethod
    def apply_tweaks(self, tweak_data: dict, priority: int) -> None:
        """Apply tweaks data to this configuration file"""

    @abstractmethod
    def load_data(self) -> None:
        """Load data contained in this file and return a dictionary"""

    def save(self) -> None:
        """Save the file"""
        conf = vdf.dumps(self.config_data, pretty=True)
        ensure_directory_for_file(self.path)
        with open(self.path, 'w') as file:
            file.write(conf)


class LocalSteamConfig(SteamConfigFile):
    """Handle local user Steam config file"""

    user_id: str

    def __init__(self, user_id: str, auto_load=False):
        self.user_id = user_id
        path_to_file = os.path.join(context.STEAM_DIR,
                                    'userdata',
                                    user_id,
                                    'config/localconfig.vdf'
                                    )
        super().__init__(path_to_file, auto_load)

    def load_data(self) -> None:
        if self.exists():
            data = vdf.load(open(self.path))
        else:
            data = vdf.VDFDict()
            data['UserLocalConfigStore'] = {'Software':
                                            {'Valve':
                                             {'Steam': {}
                                              }
                                             }
                                            }

        steam_input = data['UserLocalConfigStore']
        if 'Apps' not in steam_input:
            steam_input['Apps'] = {}

        launch_options = (data['UserLocalConfigStore']
                              ['Software']
                              ['Valve']
                              ['Steam'])
        if 'Apps' not in launch_options:
            launch_options['Apps'] = {}

        self.config_data = data

    def apply_tweaks(self, tweak_data: dict, priority=0) -> None:
        if not tweak_data:
            return
        if not self.config_data:
            self.load_data()

        steam_input_data = self.config_data['UserLocalConfigStore']['Apps']
        launch_options = (self.config_data['UserLocalConfigStore']
                                          ['Software']
                                          ['Valve']
                                          ['Steam']
                                          ['Apps'])

        for key in tweak_data:
            if ('steam_input' in tweak_data[key] and
                    tweak_data[key]['steam_input'] == 'enabled'):
                steam_input_data[key] = {
                    "UseSteamControllerConfig": "2",
                    "SteamControllerRumble": "-1",
                    "SteamControllerRumbleIntensity": "320",
                    "EnableSCTenFootOverlayCheckNew": "1"
                }

            if 'launch_options' in tweak_data[key]:
                if key not in launch_options:
                    launch_options[key] = {}
                launch_options[key]['LaunchOptions'] = (tweak_data[key]
                                                        ['launch_options'])


class MainSteamConfig(SteamConfigFile):
    """Handle main Steam config file"""

    def __init__(self, auto_load=False):
        path_to_file = os.path.join(context.STEAM_DIR, 'config/config.vdf')
        super().__init__(path_to_file, auto_load)

    def load_data(self) -> None:
        if self.exists():
            data = vdf.load(open(self.path))
        else:
            data = vdf.VDFDict()
            data['InstallConfigStore'] = {'Software':
                                          {'Valve':
                                           {'Steam': {}
                                            }
                                           }
                                          }

        steam = data['InstallConfigStore']['Software']['Valve']['Steam']

        if 'CompatToolMapping' not in steam:
            steam['CompatToolMapping'] = {}
        else:
            stale_entries = []

            for game in steam['CompatToolMapping']:
                # remove entries that were disabled in the Steam UI by the user
                if 'name' in steam['CompatToolMapping'][game] \
                    and 'config' in steam['CompatToolMapping'][game] \
                    and steam['CompatToolMapping'][game]['name'] == '' \
                    and steam['CompatToolMapping'][game]['config'] == '':
                        stale_entries.append(game)

                # remove all entries added by Chimera (they will be re-added if still configured)
                elif 'Priority' in steam['CompatToolMapping'][game] \
                    and (steam['CompatToolMapping'][game]['Priority'] == '209' \
                         or steam['CompatToolMapping'][game]['Priority'] == '229'):
                    stale_entries.append(game)

            for entry in stale_entries:
                del steam['CompatToolMapping'][entry]

        self.config_data = data

    def apply_tweaks(self, tweak_data: dict, priority=209) -> None:
        if not tweak_data:
            return
        if not self.config_data:
            self.load_data()
        compat = (self.config_data['InstallConfigStore']['Software']['Valve']
                                  ['Steam']['CompatToolMapping'])

        for key in tweak_data:
            key_priority = priority
            if 'priority' in tweak_data[key]:
                key_priority = tweak_data[key]['priority']

            if (key not in compat or
                    'Priority' not in compat[key] or
                    int(compat[key]['Priority']) <= key_priority):
                if 'compat_tool' in tweak_data[key]:
                    entry = {}
                    entry['name'] = tweak_data[key]['compat_tool']
                    if 'compat_config' in tweak_data[key]:
                        entry['config'] = tweak_data[key]['compat_config']
                    entry['Priority'] = key_priority
                    compat[key] = entry

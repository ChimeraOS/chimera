"""Submodule to handle Steam configuration files related functions"""

import os
from abc import ABC
from abc import abstractmethod
import vdf
import yaml
import chimera_app.context as context
from chimera_app.config import GAMEDB
from chimera_app.config import GameDbEntry
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
        if db[game_id].status:
            col_name = status_to_collection_name(db[game_id].status)
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
        if os.environ.get('APPLY_STATUS_COLLECTIONS'):
            print(f'Applying status collections for user: {user_id}')
            apply_status_collections(GAMEDB['steam'], user_id)


class TweaksFile:
    """Manage a tweaks file"""

    path: str
    tweaks_data: dict

    def __init__(self, path: str, auto_load=False):
        self.path = path
        self.tweaks_data = {}
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
        self.config_data = vdf.VDFDict()
        if auto_load:
            self.load_data()

    def exists(self) -> bool:
        """Returns True if the file exists, False otherwise"""
        return os.path.exists(self.path)

    @abstractmethod
    def apply_tweaks(self, tweak_data: dict[str, GameDbEntry], priority: int) -> None:
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
            data = vdf.VDFDict(vdf.load(open(self.path)))
        else:
            data = vdf.VDFDict()
            data['UserLocalConfigStore'] = {'Software':
                                            {'Valve':
                                             {'Steam': {}
                                              }
                                             }
                                            }

        steam_input = data['UserLocalConfigStore']
        if 'apps' not in steam_input:
            steam_input['apps'] = {}

        launch_options = (data['UserLocalConfigStore']
                              ['Software']
                              ['Valve']
                              ['Steam'])
        if 'apps' not in launch_options:
            launch_options['apps'] = {}

        self.config_data = data

    def apply_tweaks(self, tweak_data: dict[str, GameDbEntry], priority=0) -> None:
        if not tweak_data:
            return
        if not self.config_data:
            self.load_data()

        steam_input_data = self.config_data['UserLocalConfigStore']['apps']
        launch_options = (self.config_data['UserLocalConfigStore']
                                          ['Software']
                                          ['Valve']
                                          ['Steam']
                                          ['apps'])

        for key in tweak_data:
            entry = tweak_data[key]
            if (entry.steam_input == 'enabled'):
                steam_input_data[key] = {
                    "UseSteamControllerConfig": "2",
                    "SteamControllerRumble": "-1",
                    "SteamControllerRumbleIntensity": "320",
                    "EnableSCTenFootOverlayCheckNew": "1"
                }

            if entry.launch_options:
                if key not in launch_options:
                    launch_options[key] = {}
                launch_options[key]['LaunchOptions'] = (entry.launch_options)


class MainSteamConfig(SteamConfigFile):
    """Handle main Steam config file"""

    def __init__(self, auto_load=False):
        path_to_file = os.path.join(context.STEAM_DIR, 'config/config.vdf')
        super().__init__(path_to_file, auto_load)

    def load_data(self, clean=True) -> None:
        if self.exists():
            data = vdf.VDFDict(vdf.load(open(self.path)))
        else:
            data = vdf.VDFDict()
            data['InstallConfigStore'] = {'Software':
                                          {'Valve':
                                           {'Steam': {}
                                            }
                                           }
                                          }

        store = data['InstallConfigStore']
        steam = store['Software']['Valve']['Steam']

        # fix bluetooth in BPM by enabling bluetooth by default
        if 'System' not in store:
            store['System'] = {'Bluetooth' : {'enabled' : '1'}}
        elif 'Bluetooth' not in store['System']:
            store['System']['Bluetooth'] = {'enabled' : '1'}
        elif 'enabled' not in store['System']['Bluetooth']:
            store['System']['Bluetooth']['enabled'] = '1'

        if 'CompatToolMapping' not in steam:
            steam['CompatToolMapping'] = {}
        else:
            stale_entries = []

            for game in steam['CompatToolMapping']:
                priority_key = 'priority'
                if 'Priority' in steam['CompatToolMapping'][game]:
                    priority_key = 'Priority'

                # remove entries that were disabled in the Steam UI by the user
                if 'name' in steam['CompatToolMapping'][game] \
                    and 'config' in steam['CompatToolMapping'][game] \
                    and steam['CompatToolMapping'][game]['name'] == '' \
                    and steam['CompatToolMapping'][game]['config'] == '':
                        stale_entries.append(game)

                # remove all entries added by Chimera (they will be re-added if still configured)
                # covers the case where tweak entries were removed and so we want to remove them from the Steam config
                elif clean and priority_key in steam['CompatToolMapping'][game] \
                    and (steam['CompatToolMapping'][game][priority_key] == '209' \
                         or steam['CompatToolMapping'][game][priority_key] == '229'):
                    stale_entries.append(game)

            for entry in stale_entries:
                del steam['CompatToolMapping'][entry]

        self.config_data = data

    def apply_tweaks(self, tweak_data: dict[str, GameDbEntry], priority=209) -> None:
        if not tweak_data:
            return
        if not self.config_data:
            self.load_data()
        compat = (self.config_data['InstallConfigStore']['Software']['Valve']
                                  ['Steam']['CompatToolMapping'])

        for key in tweak_data:
            dbentry = tweak_data[key]

            priority_value = priority
            if dbentry.priority:
                priority_value = dbentry.priority

            priority_key = 'priority'
            if key in compat and 'Priority' in compat[key]:
                priority_key = 'Priority'

            if (key not in compat or
                    priority_key not in compat[key] or
                    int(compat[key][priority_key]) <= priority_value):
                if dbentry.compat_tool:
                    entry = {}
                    entry['name'] = dbentry.compat_tool
                    if dbentry.compat_config:
                        entry['config'] = dbentry.compat_config
                    entry[priority_key] = priority_value
                    compat[key] = entry

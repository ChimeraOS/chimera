"""Submodule to handle Steam configuration files related functions"""

import vdf
import time
import yaml
import shutil
import requests
from chimera_app.utils import ChimeraContext
from chimera_app.utils import ensure_directory_for_file
from chimera_app.utils import file_exists


class SteamConfig:
    """This class is menat to handle all steam configuration files.
    The basic usage would be:
        sc = SteamConfig()
        sc.update()
        sc.apply_tweaks()
    """

    _context = ChimeraContext()

    def update(self):
        self.download_tweaks_file(self._context.MAIN_TWEAKS_FILE,
                                  static_file=self._context.STATIC_TWEAKS_FILE)

    def apply_tweaks(self):
        sc = self._context
        ensure_directory_for_file(sc.STEAM_CONFIG_FILE)

        config_data = self.load_main(sc.STEAM_CONFIG_FILE)

        self.apply_to_main_config(sc.MAIN_TWEAKS_FILE,
                                  config_data,
                                  Priority=209)  # add global entries if file exists
        self.apply_to_main_config(sc.LOCAL_TWEAKS_FILE,
                                  config_data,
                                  Priority=229)  # add local entries if file exists
        self.apply_to_main_config(sc.COMPAT_DATA_FILE,
                                  config_data,
                                  Priority=209)  # add shortcut compat data
        self.write(config_data, sc.STEAM_CONFIG_FILE)

        for user_dir in sc.STEAM_USER_DIRS:
            config_file = user_dir + '/config/localconfig.vdf'

            ensure_directory_for_file(config_file)

            config_data = self.load_local(config_file)

            # Add global entries if file exists
            self.apply_to_local_config(sc.MAIN_TWEAKS_FILE, config_data)
            # Add local entries if file exists
            self.apply_to_local_config(sc.LOCAL_TWEAKS_FILE, config_data)

            self.write(config_data, config_file)

    @staticmethod
    def write(config_data, config_file):
        vdf.dump(config_data, open(config_file, 'w'), pretty=True)

    @staticmethod
    def load_main(path):
        if file_exists(path):
            data = vdf.load(open(path))
        else:
            data = vdf.VDFDict()
            data['InstallConfigStore'] = {'Software': {'Valve': {'Steam': {}}}}

        steam = data['InstallConfigStore']['Software']['Valve']['Steam']

        if 'CompatToolMapping' not in steam:
            steam['CompatToolMapping'] = {}
        else:
            stale_entries = []

            for game in steam['CompatToolMapping']:
                if ('name' in steam['CompatToolMapping'][game] and
                        'config' in steam['CompatToolMapping'][game]):
                    if (steam['CompatToolMapping'][game]['name'] == '' and
                            steam['CompatToolMapping'][game]['config'] == ''):
                        stale_entries.append(game)

            for entry in stale_entries:
                del steam['CompatToolMapping'][entry]

        return data

    @staticmethod
    def load_local(path):
        if file_exists(path):
            data = vdf.load(open(path))
        else:
            data = vdf.VDFDict()
            data['UserLocalConfigStore'] = {'Software': {'Valve': {'Steam': {}}}}

        steam_input = data['UserLocalConfigStore']
        if 'Apps' not in steam_input:
            steam_input['Apps'] = {}

        launch_options = data['UserLocalConfigStore']['Software']['Valve']['Steam']
        if 'Apps' not in launch_options:
            launch_options['Apps'] = {}

        return data

    @staticmethod
    def download_tweaks_file(file_path, num_atempts=5, static_file=None):
        """Downloads the latest tweak file from our server. It will try
        num_atempts or fail. If the file can't be reached after num_atempts
        then it will be replaced by a static file designated by static_file
        unless the file already exists.

        returns True if the procedure was successful by downloading the new
        file or by replacing with static_file
        """
        url = ('https://raw.githubusercontent.com/ChimeraOS/'
               'chimera/master/steam-tweaks.yaml')
        ret_val = False
        attempts = 0
        while (attempts < num_atempts):
            try:
                r = requests.get(url, timeout=1)
            except requests.Timeout:
                continue
            if r.status_code == 200:
                open(file_path, 'wb').write(r.content)
                ret_val = True
                break  # We succeeded, no need to continue

            time.sleep(1)
            attempts += 1

        if (not ret_val):
            if (static_file is not None):
                if file_exists(static_file):
                    shutil.copyfile(static_file, file_path)
                    ret_val = True
                else:
                    print(f'{file_path} does not exist')
            else:
                print(f'Could not get file from {url} in {num_atempts} atempts')
        else:
            print(f'Could not get file from {url} in {num_atempts} atempts')

        return ret_val

    @staticmethod
    def apply_to_main_config(tweaks_file, steam_data, priority=209):
        """write tweaks into Steam config data."""

        if not file_exists(tweaks_file):
            return

        compat = steam_data['InstallConfigStore']['Software']['Valve']['Steam']['CompatToolMapping']

        data = yaml.load(open(tweaks_file), Loader=yaml.FullLoader)
        for key in data:
            if (key not in compat or
                    'Priority' not in compat[key] or
                    int(compat[key]['Priority']) <= priority):
                if 'compat_tool' in data[key]:
                    entry = {}
                    entry['name'] = data[key]['compat_tool']
                    if 'compat_config' in data[key]:
                        entry['config'] = data[key]['compat_config']
                    entry['Priority'] = priority
                    compat[key] = entry

    @staticmethod
    def apply_to_local_config(tweaks_file, steam_data):
        if not file_exists(tweaks_file):
            return

        steam_input_data = steam_data['UserLocalConfigStore']['Apps']
        launch_options = steam_data['UserLocalConfigStore']['Software']['Valve']['Steam']['Apps']

        data = yaml.load(open(tweaks_file), Loader=yaml.FullLoader)
        for key in data:
            if ('steam_input' in data[key] and
                    data[key]['steam_input'] == 'enabled'):
                steam_input_data[key] = {
                    "UseSteamControllerConfig": "2",
                    "SteamControllerRumble": "-1",
                    "SteamControllerRumbleIntensity": "320",
                    "EnableSCTenFootOverlayCheckNew": "1"
                }

            if 'launch_options' in data[key]:
                if key not in launch_options:
                    launch_options[key] = {}
                launch_options[key]['LaunchOptions'] = data[key]['launch_options']


"""Submodule to handle Steam configuration files related functions"""

import os
import vdf
import yaml
import chimera_app.context as context
from chimera_app.utils import ensure_directory_for_file


def apply_all_tweaks():
    if (not os.path.exists(context.MAIN_TWEAKS_FILE)
            and not os.path.exists(context.LOCAL_TWEAKS_FILE)):
        print('No tweaks to apply')
        return
    sc = SteamConfig()
    sc.apply_tweaks()


class SteamConfig:
    """This class is menat to handle all steam configuration files.
    The basic usage would be:
        sc = SteamConfig()
        sc.update()
        sc.apply_tweaks()
    """

    def apply_tweaks(self):
        ensure_directory_for_file(context.STEAM_CONFIG_FILE)

        config_data = self.load_main(context.STEAM_CONFIG_FILE)

        # add global entries if file exists
        self.apply_to_main_config(context.MAIN_TWEAKS_FILE,
                                  config_data,
                                  priority=209)
        # add local entries if file exists
        self.apply_to_main_config(context.LOCAL_TWEAKS_FILE,
                                  config_data,
                                  priority=229)
        # add shortcut compat data
        self.apply_to_main_config(context.COMPAT_DATA_FILE,
                                  config_data,
                                  priority=209)
        self.write(config_data, context.STEAM_CONFIG_FILE)

        for user_dir in context.STEAM_USER_DIRS:
            config_file = user_dir + '/config/localconfig.vdf'

            ensure_directory_for_file(config_file)

            config_data = self.load_local(config_file)

            # Add global entries if file exists
            self.apply_to_local_config(context.MAIN_TWEAKS_FILE, config_data)
            # Add local entries if file exists
            self.apply_to_local_config(context.LOCAL_TWEAKS_FILE, config_data)

            self.write(config_data, config_file)

    @staticmethod
    def write(config_data, config_file):
        conf = vdf.dumps(config_data, pretty=True)
        with open(config_file, 'w') as file:
            file.write(conf)

    @staticmethod
    def load_main(path):
        if os.path.exists(path):
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
        if os.path.exists(path):
            data = vdf.load(open(path))
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

        launch_options = (data['UserLocalConfigStore']['Software']['Valve']
                          ['Steam'])
        if 'Apps' not in launch_options:
            launch_options['Apps'] = {}

        return data

    @staticmethod
    def apply_to_main_config(tweaks_file, steam_data, priority=209):
        """write tweaks into Steam config data."""

        if not os.path.exists(tweaks_file):
            return

        compat = (steam_data['InstallConfigStore']['Software']['Valve']
                  ['Steam']['CompatToolMapping'])

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
        if not os.path.exists(tweaks_file):
            return

        steam_input_data = steam_data['UserLocalConfigStore']['Apps']
        launch_options = (steam_data['UserLocalConfigStore']['Software']
                          ['Valve']['Steam']['Apps'])

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
                launch_options[key]['LaunchOptions'] = (data[key]
                                                        ['launch_options'])

"""Utilities for the chimera_app tools"""
import os
from datetime import datetime


def ensure_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)


def ensure_directory_for_file(file):
    d = os.path.dirname(file)
    ensure_directory(d)


def file_exists(file):
    return os.path.exists(file)


def directory_exists(directory):
    return os.path.isdir(directory)


def yearsago(years):
    from_date = datetime.now().date()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        return from_date.replace(month=2, day=28, year=from_date.year - years)


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


class ChimeraContext:
    """Singleton class to manage the Steam environment.
    It contains variables and common functions to be used in all
    chimera tools"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChimeraContext, cls).__new__(cls)
            cls._instance.__init()
        return cls._instance

    def __init(self):
        """Initialize all directories and common file names"""
        self.STATIC_DATA = self.__get_static_data_dir()
        self.CACHE_HOME = self.__get_cache_home_dir()
        self.CONFIG_HOME = self.__get_config_home_dir()
        self.DATA_HOME = self.__get_data_home_dir()
        self.COMPAT_DATA_FILE = self.__get_compat_data_file()
        self.SHORTCUT_DIRS = self.__get_shortcut_dirs()
        self.STATIC_COMPAT_TOOLS = self.__get_static_compat_tools_dir()
        self.STEAM_DIR = self.__get_steam_dir()
        self.STEAM_APPS_DIR = self.__get_steam_apps_dir()
        self.STEAM_USER_DIRS = self.__get_steam_user_dirs()
        self.STEAM_COMPAT_TOOLS = self.__get_steam_compat_tools_dir()
        self.STEAM_CONFIG_FILE = self.__get_steam_config_file()
        self.STATIC_TWEAKS_FILE = self.__get_static_tweaks_file()
        self.MAIN_TWEAKS_FILE = self.__get_main_tweaks_file()
        self.LOCAL_TWEAKS_FILE = self.__get_local_tweaks_file()
        self.TIME_WARP = os.environ.get('TIME_WARP')

    def __get_static_data_dir(self):
        return '/usr/share/chimera'

    def __get_cache_home_dir(self):
        if 'XDG_CACHE_HOME' in os.environ:
            cache = os.environ['XDG_CACHE_HOME']
        else:
            cache = os.environ['HOME'] + '/.cache'
        return cache

    def __get_config_home_dir(self):
        if 'XDG_CONFIG_HOME' in os.environ:
            config = os.environ['XDG_CONFIG_HOME']
        else:
            config = os.environ['HOME'] + '/.config'
        return config

    def __get_data_home_dir(self):
        if 'XDG_DATA_HOME' in os.environ:
            data_home = os.environ['XDG_DATA_HOME']
        else:
            data_home = os.environ['HOME'] + '/.local/share'
        return data_home

    def __get_compat_data_file(self):
        return self.CACHE_HOME + '/steam-shortcuts-compat.yaml'

    def __get_shortcut_dirs(self):
        return self.DATA_HOME + '/chimera/shortcuts'

    def __get_static_compat_tools_dir(self):
        return '/usr/share/chimera/compat-tools'

    def __get_steam_dir(self):
        return self.DATA_HOME + '/Steam'

    def __get_steam_apps_dir(self):
        return self.STEAM_DIR + '/steamapps/common'

    def __get_steam_user_dirs(self):
        base = self.STEAM_DIR + '/userdata'
        ensure_directory(base)
        user_dirs = []
        for d in os.listdir(base):
            if d not in ['anonymous', 'ac', '0']:
                user_dirs.append('/'.join([base, d]))
        return user_dirs

    def __get_steam_compat_tools_dir(self):
        return self.STEAM_DIR + '/compatibilitytools.d'

    def __get_steam_config_file(self):
        return self.STEAM_DIR + '/config/config.vdf'

    def __get_main_tweaks_file(self):
        return self.DATA_HOME + '/chimera/steam-tweaks.yaml'

    def __get_local_tweaks_file(self):
        return self.CONFIG_HOME + '/steam-tweaks.yaml'

    def __get_static_tweaks_file(self):
        return '/usr/share/chimera/steam-tweaks.yaml'

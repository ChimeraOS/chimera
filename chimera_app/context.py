"""Context variables for all Chimera tools"""

import os


def __get_steam_user_dirs(steam_dir):
    base = os.path.join(steam_dir, 'userdata')
    user_dirs = []
    if os.path.isdir(base):
        for d in os.listdir(base):
            if d not in ['anonymous', 'ac', '0']:
                user_dirs.append(os.path.join(base, d))
    return user_dirs


CACHE_HOME = os.path.expanduser('~/.cache')
CONFIG_HOME = os.path.expanduser('~/.config')
DATA_HOME = os.path.expanduser('~/.local/share')
COMPAT_DATA_FILE = os.path.join(CACHE_HOME, 'steam-shortcuts-compat.yaml')
SHORTCUT_DIRS = os.path.join(DATA_HOME, 'chimera/shortcuts')
TOOLS_DIR = os.path.join(DATA_HOME, 'chimera/data/compat/tools')
TOOLS_TEMPLATE_FILE = os.path.join(DATA_HOME, 'chimera/data/compat/tool-stub.tpl')
PATCH_DIR = os.path.join(DATA_HOME, 'chimera/data/patch')
TIME_WARP = os.environ.get('TIME_WARP')
STEAM_DIR = os.path.join(DATA_HOME, 'Steam')
STEAM_APPS_DIR = os.path.join(STEAM_DIR, 'steamapps/common')
STEAM_USER_DIRS = __get_steam_user_dirs(STEAM_DIR)
STEAM_COMPAT_TOOLS = os.path.join(STEAM_DIR, 'compatibilitytools.d')
STEAM_CONFIG_FILE = os.path.join(STEAM_DIR, 'config/config.vdf')

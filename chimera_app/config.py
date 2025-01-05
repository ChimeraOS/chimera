import os
import yaml
from dataclasses import dataclass
from chimera_app.settings import Settings
import chimera_app.context as context
from chimera_app.ftp.server import Server as FTPServer
from chimera_app.authenticator import Authenticator, generate_password
from chimera_app.ssh_keys import SSHKeys
from chimera_app.steamgrid.steamgrid import Steamgrid
from chimera_app.storage import StorageConfig


def merge_single_level(src1, src2):
    keys = src1.keys() | src2.keys()

    result = {}
    for key in keys:
            if key in src1 and key in src2:
                    result[key] = src1[key] | src2[key]
            elif key in src1:
                    result[key] = src1[key]
            else:
                    result[key] = src2[key]

    return result


RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
    RESOURCE_DIR = "/usr/share/chimera"

BIN_PATH = os.path.abspath('libexec')
if not os.path.isdir(BIN_PATH):
    BIN_PATH = "/usr/libexec/chimera"

BANNER_DIR = context.DATA_HOME + '/chimera/images'
DATA_DIR = context.DATA_HOME + '/chimera/data'
CONTENT_DIR = context.DATA_HOME + '/chimera/content'
SETTINGS_DIR = context.CONFIG_HOME + '/chimera'
UPLOADS_DIR = os.path.join(context.CACHE_HOME, 'chimera', 'uploads')

SETTINGS_DEFAULT = {
    "enable_remote_launch": False,
    "enable_content_sharing": False,
    "enable_ftp_server": False,
    "ftp_username": "gamer",
    "ftp_password": generate_password(12),
    "ftp_port": 2121,
    "keep_password": False,
}

SESSION_OPTIONS = {
    'session.cookie_expires': True,
    'session.httponly': True,
    'session.timeout': 3600 * 2,
    'session.type': 'memory',
    'session.validate_key': True,
}

SETTINGS_HANDLER = Settings(SETTINGS_DIR, SETTINGS_DEFAULT)

AUTHENTICATOR = Authenticator(BIN_PATH, password_length=5)

FTP_SERVER = FTPServer(SETTINGS_HANDLER)

SSH_KEY_HANDLER = SSHKeys(os.path.expanduser('~/.ssh/authorized_keys'))

STEAMGRID_HANDLER = Steamgrid("423ef7be0f4b9f8cfa1a471149c5b72c")

STORAGE_HANDLER = StorageConfig()

PLATFORMS_DEFAULT = {
    "32x": {
        "name": "32X",
        "enabled": True,
    },
    "3do": {
        "name": "3DO",
        "enabled": True,
    },
    "appimage": {
        "name": "AppImage",
        "enabled": False,
    },
    "arcade": {
        "name": "Arcade",
        "enabled": True,
    },
    "atari-2600": {
        "name": "Atari 2600",
        "enabled": True,
    },
    "atari-7800": {
        "name": "Atari 7800",
        "enabled": True,
    },
    "dreamcast": {
        "name": "Dreamcast",
        "enabled": True,
    },
    "epic-store": {
        "name": "Epic Games Store",
        "enabled": True,
    },
    "flathub": {
        "name": "Flathub",
        "enabled": True,
    },
    "gb": {
        "name": "Game Boy",
        "enabled": True,
    },
    "gba": {
        "name": "Game Boy Advance",
        "enabled": True,
    },
    "gbc": {
        "name": "Game Boy Color",
        "enabled": True,
    },
    "ngc": {
        "name": "GameCube",
        "enabled": True,
    },
    "sgg": {
        "name": "Game Gear",
        "enabled": True,
    },
    "genesis": {
        "name": "Genesis",
        "enabled": True,
    },
    "gog": {
        "name": "GOG",
        "enabled": True,
    },
    "jaguar": {
        "name": "Jaguar",
        "enabled": True,
    },
    "sms": {
        "name": "Master System",
        "enabled": True,
    },
    "msdos": {
        "name": "MS DOS",
        "enabled": False,
    },
    "neo-geo": {
        "name": "Neo Geo",
        "enabled": True,
    },
    "n3ds": {
        "name": "Nintendo 3DS",
        "enabled": False,
    },
    "nds": {
        "name": "Nintendo DS",
        "enabled": True,
    },
    "nes": {
        "name": "Nintendo",
        "enabled": True,
    },
    "n64": {
        "name": "Nintendo 64",
        "enabled": True,
    },
    "ps1": {
        "name": "PlayStation",
        "enabled": True,
    },
    "ps2": {
        "name": "PlayStation 2",
        "enabled": True,
    },
    "spsp": {
        "name": "PlayStation Portable",
        "enabled": True,
    },
    "saturn": {
        "name": "Saturn",
        "enabled": True,
    },
    "sega-cd": {
        "name": "Sega CD",
        "enabled": True,
    },
    "sgb": {
        "name": "Super Game Boy",
        "enabled": False,
    },
    "snes": {
        "name": "Super Nintendo",
        "enabled": True,
    },
    "snesmsu1": {
        "name": "Super Nintendo MSU1",
        "enabled": False,
    },
    "tg-16": {
        "name": "TurboGrafx-16",
        "enabled": True,
    },
    "wii": {
        "name": "Wii",
        "enabled": True,
    },
    "switch": {
        "name": "Switch",
        "enabled": True,
    },
}

# set a default cmd property on all default platforms
for platform_id in PLATFORMS_DEFAULT:
    PLATFORMS_DEFAULT[platform_id]['cmd'] = platform_id

# merge user settings with default platforms
PLATFORMS = PLATFORMS_DEFAULT
PLATFORM_SETTINGS = SETTINGS_HANDLER.get_setting('platforms')
if PLATFORM_SETTINGS:
    PLATFORMS = merge_single_level(PLATFORMS_DEFAULT, PLATFORM_SETTINGS)

# set id property on all platforms
for platform_id in PLATFORMS:
    PLATFORMS[platform_id]['id'] = platform_id

# drop disabled and invalid platforms
FILTERED_PLATFORMS = {}
for key, value in PLATFORMS.items():
    if 'enabled' not in value or not value['enabled'] or 'name' not in value or 'cmd' not in value:
        continue

    FILTERED_PLATFORMS[key] = value

PLATFORMS = dict(sorted(FILTERED_PLATFORMS.items(), key=lambda item: item[1]['name']))


GAMEDB = {
    'gog' : {},
    'epic-store' : {},
    'flathub' : {},
    'steam' : {},
}

@dataclass
class GameDbEntry:
    name: str
    platform: str
    id: str
    banner: str | None
    poster: str | None
    background: str | None
    logo: str | None
    icon: str | None
    compat_tool: str | None
    compat_config: str | None
    launch_options: str | None
    status: str | None
    store: str | None
    steam_input: str | None
    notes: list[str] | None

    @property
    def status_icon(self):
        if self.status == 'verified':
            return '🟢'
        elif self.status == 'playable':
            return '🟡'
        elif self.status == 'unsupported':
            return '🔴'
        else:
            return '⚫'


try:
    with open(os.path.join(DATA_DIR, 'gamedb.yaml')) as yaml_file:
        game_list = yaml.load(yaml_file, Loader=yaml.FullLoader)

        for game in game_list:
            if 'id' in game:
                game['id'] = str(game['id'])
                GAMEDB[game['platform']][game['id']] = GameDbEntry(
                    name=game['name'],
                    platform=game['platform'],
                    id=game['id'],
                    banner=game['banner'] if 'banner' in game else None,
                    poster=game['poster'] if 'poster' in game else None,
                    background=game['background'] if 'background' in game else None,
                    logo=game['logo'] if 'logo' in game else None,
                    icon=game['icon'] if 'icon' in game else None,
                    compat_tool=game['compat_tool'] if 'compat_tool' in game else None,
                    compat_config=game['compat_config'] if 'compat_config' in game else None,
                    launch_options=game['launch_options'] if 'launch_options' in game else None,
                    status=game['status'] if 'status' in game else None,
                    store=game['store'] if 'store' in game else None,
                    steam_input=game['steam_input'] if 'steam_input' in game else None,
                    notes=game['notes'] if 'notes' in game else None
                )
except:
    print('WARNING: Failed to load game database')

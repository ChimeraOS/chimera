import os
import yaml
from chimera_app.settings import Settings
import chimera_app.context as context
from chimera_app.ftp.server import Server as FTPServer
from chimera_app.authenticator import Authenticator, generate_password
from chimera_app.ssh_keys import SSHKeys
from chimera_app.steamgrid.steamgrid import Steamgrid
from chimera_app.storage import StorageConfig
from chimera_app.streaming import StreamServer
from chimera_app.mangohud_config import MangoHudConfig


RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
    RESOURCE_DIR = "/usr/share/chimera"

BIN_PATH = os.path.abspath('bin')
if not os.path.isdir(BIN_PATH):
    BIN_PATH = "/usr/share/chimera/bin"

SHORTCUT_DIR = context.SHORTCUT_DIRS
BANNER_DIR = context.DATA_HOME + '/chimera/images'
DATA_DIR = context.DATA_HOME + '/chimera/data'
CONTENT_DIR = context.DATA_HOME + '/chimera/content'
RECORDINGS_DIR = context.DATA_HOME + '/chimera/recordings'
SETTINGS_DIR = context.CONFIG_HOME + '/chimera'
UPLOADS_DIR = os.path.join(context.CACHE_HOME, 'chimera', 'uploads')
MANGOHUD_DIR = context.CONFIG_HOME + "/MangoHud"

PLATFORMS = {
    "32x":         "32X",
    "3do":         "3DO",
    "arcade":      "Arcade",
    "atari-2600":  "Atari 2600",
    "dreamcast":   "Dreamcast",
    "epic-store":  "Epic Games Store",
    "flathub":     "Flathub",
    "gb":          "Game Boy",
    "gba":         "Game Boy Advance",
    "gbc":         "Game Boy Color",
    "ngc":         "GameCube",
    "sgg":         "Game Gear",
    "genesis":     "Genesis",
    "gog":         "GOG",
    "jaguar":      "Jaguar",
    "sms":         "Master System",
	"nds":         "Nintendo DS",    
    "neo-geo":     "Neo Geo",
    "nes":         "Nintendo",
    "n64":         "Nintendo 64",
    "ps1":         "PlayStation",
    "ps2":         "PlayStation 2",
    "psp":         "PlayStation Portable",
    "saturn":      "Saturn",
    "sega-cd":     "Sega CD",
    "snes":        "Super Nintendo",
    "tg-16":       "TurboGrafx-16",
    "wii":         "Wii"
}

SETTINGS_DEFAULT = {
    "enable_ftp_server": False,
    "ftp_username": "gamer",
    "ftp_password": generate_password(12),
    "ftp_port": 2121,
    "keep_password": False,
    "recordings_dir": RECORDINGS_DIR,
    "sls_conf_file": RESOURCE_DIR + "/config/sls.conf",
    "ffmpeg_inputs":
        ["-f x11grab -i :0",
         "-f alsa -i pulse"],
    "ffmpeg_vcodec": "",
    "ffmpeg_acodec": ""
}

SESSION_OPTIONS = {
    'session.cookie_expires': True,
    'session.httponly': True,
    'session.timeout': 3600 * 2,
    'session.type': 'memory',
    'session.validate_key': True,
}

SETTINGS_HANDLER = Settings(SETTINGS_DIR, SETTINGS_DEFAULT)

AUTHENTICATOR = Authenticator(BIN_PATH, password_length=8)

FTP_SERVER = FTPServer(SETTINGS_HANDLER)

SSH_KEY_HANDLER = SSHKeys(os.path.expanduser('~/.ssh/authorized_keys'))

STEAMGRID_HANDLER = Steamgrid("423ef7be0f4b9f8cfa1a471149c5b72c")

STREAMING_HANDLER = StreamServer(SETTINGS_HANDLER)

MANGOHUD_HANDLER = MangoHudConfig(MANGOHUD_DIR)

STORAGE_HANDLER = StorageConfig()

if SETTINGS_HANDLER.get_setting('platforms'):
    PLATFORMS = SETTINGS_HANDLER.get_setting('platforms')


GAMEDB = {
    'gog' : {},
    'epic-store' : {},
    'flathub' : {},
    'steam' : {},
}

try:
    with open(os.path.join(DATA_DIR, 'gamedb.yaml')) as yaml_file:
        game_list = yaml.load(yaml_file, Loader=yaml.FullLoader)

        for game in game_list:
            if 'id' in game:
                game['id'] = str(game['id'])
                GAMEDB[game['platform']][game['id']] = game
except:
    print('WARNING: Failed to load game database')

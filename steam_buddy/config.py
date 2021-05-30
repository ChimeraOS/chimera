import os
from steam_buddy.settings import Settings
from steam_buddy.ftp.server import Server as FTPServer
from steam_buddy.authenticator import Authenticator, generate_password
from steam_buddy.ssh_keys import SSHKeys
from steam_buddy.steamgrid.steamgrid import Steamgrid
from steam_buddy.streaming import StreamServer
from steam_buddy.mangohud_config import MangoHudConfig

DATA_DIR = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
CACHE_DIR = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))

RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
    RESOURCE_DIR = "/usr/share/steam-buddy"

AUTHENTICATOR_PATH = os.path.abspath('bin/steam-buddy-authenticator')
if not os.path.isfile(AUTHENTICATOR_PATH):
    AUTHENTICATOR_PATH = "/usr/share/steam-buddy/bin/steam-buddy-authenticator"

SHORTCUT_DIR = DATA_DIR + '/steam-shortcuts'
BANNER_DIR = DATA_DIR + '/steam-buddy/banners'
CONTENT_DIR = DATA_DIR + '/steam-buddy/content'
RECORDINGS_DIR = DATA_DIR + '/steam-buddy/recordings'
SETTINGS_DIR = DATA_DIR + '/steam-buddy/settings'
UPLOADS_DIR = os.path.join(CACHE_DIR, 'steam-buddy', 'uploads')
MANGOHUD_DIR = CONFIG_DIR + "/MangoHud"

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
    "gc":          "GameCube",
    "gog":         "GOG",
    "sgg":         "Game Gear",
    "genesis":     "Genesis",
    "jaguar":      "Jaguar",
    "sms":         "Master System",
    "neo-geo":     "Neo Geo",
    "nes":         "Nintendo",
    "n64":         "Nintendo 64",
    "ps1":         "PlayStation",
    "ps2":         "PlayStation 2",
    "psp":         "PlayStation Portable",
    "saturn":      "Saturn",
    "sega-cd":     "Sega CD",
    "snes":        "Super Nintendo",
    "tg-16":       "TurboGrafx-16"
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

AUTHENTICATOR = Authenticator(AUTHENTICATOR_PATH, password_length=8)

FTP_SERVER = FTPServer(SETTINGS_HANDLER)

SSH_KEY_HANDLER = SSHKeys(os.path.expanduser('~/.ssh/authorized_keys'))

STEAMGRID_HANDLER = Steamgrid("f092e3045f4f041c4bf8a9db2cb8c25c")

STREAMING_HANDLER = StreamServer(SETTINGS_HANDLER)

MANGOHUD_HANDLER = MangoHudConfig(MANGOHUD_DIR)

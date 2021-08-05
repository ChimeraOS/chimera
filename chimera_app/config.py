import os
from chimera_app.settings import Settings
import chimera_app.context as context
from chimera_app.ftp.server import Server as FTPServer
from chimera_app.authenticator import Authenticator, generate_password
from chimera_app.ssh_keys import SSHKeys
from chimera_app.steamgrid.steamgrid import Steamgrid
from chimera_app.streaming import StreamServer
from chimera_app.mangohud_config import MangoHudConfig


RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
    RESOURCE_DIR = "/usr/share/chimera"

AUTHENTICATOR_PATH = os.path.abspath('bin/chimera-authenticator')
if not os.path.isfile(AUTHENTICATOR_PATH):
    AUTHENTICATOR_PATH = "/usr/share/chimera/bin/chimera-authenticator"

SHORTCUT_DIR = context.SHORTCUT_DIRS
BANNER_DIR = context.DATA_HOME + '/chimera/banners'
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

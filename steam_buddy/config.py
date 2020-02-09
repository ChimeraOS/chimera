import os
from steam_buddy.flathub import Flathub
from steam_buddy.settings import Settings
from steam_buddy.ftp.server import Server as FTPServer

DATA_DIR = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
	RESOURCE_DIR = "/usr/share/steam-buddy"

SHORTCUT_DIR = DATA_DIR + '/steam-shortcuts'
BANNER_DIR = DATA_DIR + '/steam-buddy/banners'
CONTENT_DIR = DATA_DIR + '/steam-buddy/content'
SETTINGS_DIR = DATA_DIR + '/steam-buddy/settings'

PLATFORMS = {
	"atari-2600" : "Atari 2600",
	"flathub"    : "Flathub",
	"gb"         : "Game Boy",
	"gba"        : "Game Boy Advance",
	"gbc"        : "Game Boy Color",
	"sgg"        : "Game Gear",
	"genesis"    : "Genesis",
	"sms"        : "Master System",
	"nes"        : "Nintendo",
	"n64"        : "Nintendo 64",
	"snes"       : "Super Nintendo",
	"tg-16"      : "TurboGrafx-16"
}

SETTINGS_DEFAULT = {
	"enable_ftp_server": False,
	"ftp_username": "gamer",
	"ftp_password": "gamer",
	"ftp_port": 2121
}

FLATHUB_HANDLER = Flathub()

SETTINGS_HANDLER = Settings(SETTINGS_DIR, SETTINGS_DEFAULT)

FTP_SERVER = FTPServer(SETTINGS_HANDLER)

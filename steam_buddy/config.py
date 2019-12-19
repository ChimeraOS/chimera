import os
from steam_buddy.flathub import Flathub

DATA_DIR = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

RESOURCE_DIR = os.getcwd()
if not os.path.isfile(os.path.join(RESOURCE_DIR, 'views/base.tpl')):
	RESOURCE_DIR = "/usr/share/steam-buddy"

SHORTCUT_DIR = DATA_DIR + '/steam-shortcuts'
BANNER_DIR = DATA_DIR + '/steam-buddy/banners'
CONTENT_DIR = DATA_DIR + '/steam-buddy/content'

PLATFORMS = {
	"flathub": 	"Flathub",
	"gb":		"Game Boy",
	"gba":		"Game Boy Advance",
	"gbc":		"Game Boy Color",
	"sgg":		"Game Gear",
	"genesis": 	"Genesis",
	"sms": 		"Master System",
	"nes": 		"Nintendo",
	"snes": 	"Super Nintendo",
	"tg-16":	"TurboGrafx-16"
}

FLATHUB_HANDLER = Flathub()

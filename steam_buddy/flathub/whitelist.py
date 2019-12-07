import os

def listdir(path):
	if os.path.isdir(path):
		return os.listdir(path)
	else:
		return []

local = os.path.join(os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'steam-buddy/banners/flathub')
files = listdir('images/flathub') + listdir(local) + listdir('/usr/share/steam-buddy/images/flathub/')
whitelist = [ os.path.splitext(f)[0] for f in files ]

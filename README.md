## What is it?
Steam Buddy is a web-based tool for installing non-Steam software to your Linux based couch gaming system. It was primarily developed for GamerOS.


## Features

### Install Flathub apps
Only a limited set of applications are available for immediate installation from Flathub. Many applications on Flathub have compatibility issues with the GamerOS compositor and require testing. The set of available applications will be expanded over time.

Steam Buddy also looks in `~/.local/share/steam-buddy/banners/flathub/` for a list of additionally allowed Flathub applications. Just add a PNG or JPEG image of size 460x215 or 920x430 with the Flathub app id as the file name under that directory. The Flathub app id can be obtained from the last part of the URL of the Flathub page for the application. For example, the id for Minecraft is `com.mojang.Minecraft`.

If the application works well please create a new issue with the app id and grid image for permanent whitelisting.


### Upload ROMs

You can upload ROMs and banner images to Steam Buddy and they will be added to Steam. The emulators are pre-configured and ready to play out of the box with almost any controller.

The following platforms are currently supported:
- Atari 2600
- Game Boy
- Game Boy Advance
- Game Boy Color
- Game Gear
- Genesis/Mega Drive
- Master System
- Nintendo
- Nintendo 64
- Super Nintendo
- TurboGrafx-16

More platforms will be added over time.

## Installation

Steam Buddy is installed and configured out of the box on GamerOS.

It is also available for Arch from the AUR as `steam-buddy`.
After installing the `steam-buddy` package, you must run the following commands as root to enable it and then restart your system:
```
    systemctl enable steam-buddy@<your username>.service
    systemctl enable steam-buddy-proxy@<your username>.service
    systemctl enable steam-buddy-proxy@<your username>.socket
```

## Usage
You can connect to Steam Buddy on GamerOS by opening a browser on another computer and entering `gameros.local`. If that does not work, then determine the IP address of your GamerOS system by looking at the network settings and enter it directly into your browser.

After installing any app, you must restart Steam for the newly installed application or game to appear in the Steam Big Picture UI.
To restart Steam you can click on the cog icon in the top right of the Steam Buddy UI and select the "Restart Steam" option.


## Screenshots

![Platforms](screenshots/platforms.png?raw=true)
![Flathub](screenshots/flathub.png?raw=true)

## What is it?
Chimera is a web app for remotely installing non-Steam software to your Linux based couch gaming system. It was primarily developed for ChimeraOS.

## Features

 - install games from GOG, Epic Games Store, and Flathub
 - upload ROMs for supported console emulators
 - quick actions
   - adjust audio volume
   - toggle performance overlay (MangoHud)
   - toggle Steam overlay
   - load/save emulator state
   - toggle window mode (switch between SteamOS compositor and Openbox)
   - restart steam
   - suspend/reboot/power off
 - virtual keyboard
 - performance overlay configuration (MangoHud)
 - built-in FTP server
 - enable SSH access

## Installation
On Arch Linux install the `chimera` package from the AUR. On ChimeraOS the package is pre-installed

After installing the `chimera` package, you must run the following commands to enable the web interface and then restart your system:
```
    systemctl --user enable chimera.service
    sudo systemctl enable chimera-proxy.service
    sudo systemctl enable chimera-proxy.socket
```

To have game patches be applied, you must also run the following command
```
   systemctl --user enable steam-patch
```

## Usage

### Web interface
You can connect to Chimera on ChimeraOS by opening a browser on another computer and entering `chimeraos.local`. If that does not work, then determine the IP address of your ChimeraOS system by looking at the network settings and enter it directly into your browser.

After installing any app, you must restart Steam for the newly installed application or game to appear in the Steam Big Picture UI.

To restart Steam you can open the menu, click on "Actions", then select the "Restart Steam".

### Command line interface
If you use ChimeraOS or use `steamos-compositor-plus` and have `chimera` installed the required commands apply game tweaks and shortcuts to Steam will run automatically when the Steam session starts.

Otherwise, you will need to run `chimera --update --tweaks` while Steam is not running because any changes applied while Steam is running will be overwritten by Steam.

## Configuration
For console platforms, Chimera creates shortcuts in Steam which launch each game with RetroArch. The default RetroArch configuration files are located under `/usr/share/chimera/config/`. You can override the default configuration by creating corresponding files under `~/.config/chimera/`.

## Screenshots

![Platforms](screenshots/platforms.png?raw=true)
![Flathub](screenshots/flathub.png?raw=true)
![Actions](screenshots/actions.png?raw=true)

## Feature Details

### Install Flathub apps
Only a limited set of applications are available for immediate installation from Flathub. Many applications on Flathub have compatibility issues with the ChimeraOS compositor and require testing. The set of available applications will be expanded over time.

Chimera also looks in `~/.local/share/chimera/banners/flathub/` for a list of additionally allowed Flathub applications. Just add a PNG or JPEG image of size 460x215 or 920x430 with the Flathub app id as the file name under that directory. The Flathub app id can be obtained from the last part of the URL of the Flathub page for the application. For example, the id for Minecraft is `com.mojang.Minecraft`.

If the application works well please create a new issue with the app id and grid image so it can be added to the set of installable default apps.

### Install games from the Epic Games Store
After logging in to your Epic account, you can download and install any of your games from the Epic Games Store.

Games are automatically started with Proton. Not all games will work.

### Install games from GOG
After logging in to your GOG account, you can download and install any of your games from GOG.

GOG support currently has a few limitations:
 - No support for Dosbox based games
 - Installation progress is not displayed
 - Games cannot be updated directly


### Upload ROMs

You can upload ROMs and banner images to Chimera and they will be added to Steam. The emulators are pre-configured and ready to play out of the box with almost any controller.

The following platforms are currently supported:
- 3DO (requires BIOS file)
- Arcade
- Atari 2600
- Dreamcast
- Game Boy
- Game Boy Advance
- Game Boy Color
- Game Gear
- GameCube
- Genesis/Mega Drive
- Jaguar
- Master System
- Neo Geo (requires BIOS file)
- Nintendo
- Nintendo 64
- PlayStation (requires BIOS file)
- PlayStation 2
- PlayStation Portable
- Sega 32X (requires BIOS file)
- Sega/Mega CD (requires BIOS file)
- Saturn (BIOS file optional)
- Super Nintendo
- TurboGrafx-16

More platforms will be added over time.

#### Supported formats

CD based platforms usually require use of CHD formatted game files, but may also work with ISO files.
CHD files can be created easily from cue/bin format using the `chdman` tool.

#### BIOS files

BIOS files can be uploaded the same as games. However, the name of the shortcut should reflect the name of the file that the emulator is looking for without the file extension.

Also, select the "Hide" option so the BIOS file is not shown in Steam along with other games.


## Command line details
### Data updater (chimera --update)
This command updates the compatibility tool, tweaks and patch database from the [chimera-data](https://github.com/chimeraos/chimera-data) repo.

### Steam Compat Tools (chimera --compat)
This command generates stub files for compatibility tools (currently various versions of Proton GE), which are then downloaded automatically when a game that utilizes the tool is first run.

### Steam Config (chimera --config)
Configures Steam games according to the automatically downloaded tweaks database, or the local override file if found at `~/.config/steam-tweaks.yaml`.

Extends Valve's Steam Play/Proton whitelist, specifying the compatibility tool, launch options and whether Steam Input is enabled on a per-game basis. Many games are already configured to work out of the box, with more being added over time. Please help by testing the games you own and submitting your configurations.

#### Game tweak entry format
 - **compat_tool**: the compatibility tool to be used for the specified game, e.g. `proton_42`, `steamlinuxruntime`
 - **compat_config**: the configuration for the compatibility tool specified, e.g. for proton: `d9vk`, `noesync`, etc; see the [Proton docs](https://github.com/ValveSoftware/Proton#runtime-config-options) for the full list of available options
 - **launch_options**: the launch options to be used
 - **steam_input**: a value of `enabled` will force the use of Steam Input for the specified game

#### Example entry
```
"321040":
  compat_tool: proton_411
  compat_config: noesync
  launch_options: MY_VARIABLE=1 %command%
  steam_input: enabled
```

Each game is specified by its Steam app id. Note that the app id MUST be quoted.

### Steam Shortcuts (chimera --shortcuts)
Reads one or more YAML formatted shortcut definition files stored under `~/.local/share/chimera/shortcuts/` and adds the shortcuts to all available Steam accounts.
NOTE: any existing shortcut data will be lost and replaced with shortcuts specified in the shortcut definition files.

#### Single shortcut per file example
```
name: Firefox                   # name of the shortcut as it will appear in Steam (required)
cmd: firefox                    # the command to execute (required)
dir: /full/path/to/working/dir  # the directory from which to execute the command
params: github.com              # any parameters to invoke the command with
banner: /path/to/image.png      # the horizontal banner image to use (460x215)
poster: /path/to/image.png      # the vertical poster image to use (600x900)
background: /path/to/image.png  # the background/hero image to use (1920x620)
logo: /path/to/image.png        # the logo image to use (overlayed on top of background image)
icon: firefox                   # small icon to show in Steam
compat_tool: proton_411         # use the given compatibility tool, useful for running Windows executables
compat_config: noesync          # use the given compatibility tool options
hidden: false                   # 'false' to show the shortcut in Steam, 'true' to hide it
tags:                           # a list of tags to be assigned to the shortcut in Steam
  - Browser
  - Custom Shortcut
```

#### Multiple shortcuts per file example
```
- name: Firefox
  cmd: firefox
  ...
- name: Chromium
  cmd: chromium
  ...
```

## What is it?

Chimera is a web app for remotely installing non-Steam software to your Linux based couch gaming system. It was primarily developed for ChimeraOS.

## Features

- install games from GOG, Epic Games Store, and Flathub
- upload ROMs for supported console emulators
- share ROMs across multiple systems
- quick actions
  - adjust audio volume
  - toggle the performance overlay
  - load/save emulator state
  - restart steam
  - suspend/reboot/power off
- built-in FTP server
- enable SSH access

## Installation

On Arch Linux install the `chimera` package from the AUR. On ChimeraOS the package is pre-installed

After installing the `chimera` package, you must run the following commands to enable the web interface and then restart your system:

```bash
    systemctl --user enable chimera.service
    sudo systemctl enable chimera-proxy.service
    sudo systemctl enable chimera-proxy.socket
```

To have game patches be applied, you must also run the following command

```bash
   systemctl --user enable steam-patch
```

## Usage

### Web interface

You can connect to Chimera on ChimeraOS by opening a browser on another computer and entering `chimeraos.local:8844`. If that does not work, then determine the IP address of your ChimeraOS system by looking at the network settings and enter it directly into your browser along with the port number, for example: `192.168.10.120:8844`.

After installing any app, you must restart Steam for the newly installed application or game to appear in the Steam Big Picture UI.

To restart Steam you can open the menu, click on "Actions", then select "Restart Steam".

### Command line interface

If you use ChimeraOS or use `gamescope-session` and have `chimera` installed, the required commands to apply game tweaks and shortcuts to Steam will run automatically when the Steam session starts.

Otherwise, you will need to run `chimera --update` and `chimera --tweaks` while Steam is not running because any changes applied while Steam is running will be overwritten by Steam.

## Emulation Content Sharing

Content sharing allows a single chimera instance to act as a host for ROM files and related artwork. Other instances can then install games directly from the host device without having to re-upload ROM files and select artwork.

Content sharing can be enabled under `System` by clicking on the `Enable Content Sharing` toggle and restarting the service. Please make sure to only enable this feature on a single device in your network, otherwise you may experience issues with connecting to the wrong host.

Once enabled, other chimera instances will automatically connect to the content sharing host. If you click on any emulation platform in the Library, you will see an additional blue `+` button with a radio/transmitter logo in the corner. Clicking on it will bring you to a page where you can install the shared content for that platform to your device.

It is strongly recommended to run the [Chimera Container](#chimera-container) on a home server to host your emulation content.

## Chimera Container

For convenience and to allow for running a chimera server on any OS supporting Docker, a container image is provided.

This container is dedicated to hosting games as shared content for other chimera instances on the same network.
When running the container, you can login to the app with the default password `gamer`. It is recommended to change the password immediately.

Here is a sample docker compose file for running the container version of chimera:
```
services:
  chimera:
    image: ghcr.io/chimeraos/chimera:0.23.1
    volumes:
      - ./chimera:/data/chimera
    network_mode: host
    restart: unless-stopped
```

NOTE: host network mode is required for other chimera instances to be able to discover the content sharing chimera server.

## Configuration

For console platforms, Chimera creates shortcuts in Steam which launch each game with RetroArch. The default RetroArch configuration files are located under `/usr/share/chimera/config/`. You can override the default configuration by creating corresponding files under `~/.config/chimera/`.

## Screenshots

### Library page

![Library](screenshots/platforms.png?raw=true)

### Flathub library page

![Flathub](screenshots/flathub.png?raw=true)

### Flathub game page

![Flathub Game](screenshots/flathub-game.png?raw=true)

### Actions page

![Actions](screenshots/actions.png?raw=true)

## Feature Details

### Non-Steam stores

GOG, Epic, and Flathub applications and games are evaluated for compatibility and assigned a rating of "Unsupported", "Playable", and "Verified", reflecting the Steam Deck ratings. You can contribute to these ratings by submitting a PR against [chimera-data](https://github.com/chimeraos/chimera-data) or commenting in the `compatibility-reports` channel on the [ChimeraOS Discord](https://discord.gg/fKsUbrt).

### Install Flathub apps

You can install any application on Flathub by going to `Library`, then selecting `Flathub`.

Chimera also looks in `~/.local/share/chimera/banners/flathub/` for a list of additionally allowed Flathub applications. Just add a PNG or JPEG image of size 460x215 or 920x430 with the Flathub app ID as the file name under that directory. The Flathub app ID can be obtained from the last part of the URL of the Flathub page for the application. For example, the ID for Minecraft is `com.mojang.Minecraft`.

If the application works well please create a new issue with the app ID and grid image so it can be added to the set of installable default apps.

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

You can upload ROMs and banner images to Chimera, and they will be added to Steam. The emulators are pre-configured and ready to play out of the box with almost any controller.

The following platforms are currently supported:

- 32X (requires BIOS file)
- 3DO (requires BIOS file)
- Arcade
- Atari 2600
- Dreamcast
- Game Boy
- Game Boy Advance
- Game Boy Color
- GameCube
- Game Gear
- Genesis/Mega Drive
- Jaguar
- Master System
- Neo Geo (requires BIOS file)
- Nintendo
- Nintendo 64
- PlayStation (requires BIOS file)
- PlayStation 2
- PlayStation Portable
- Saturn (requires BIOS file)
- Sega/Mega CD (requires BIOS file)
- Super Nintendo
- TurboGrafx-16/PC Engine

More platforms will be added over time.

#### Supported formats

CD based platforms usually require use of CHD formatted game files, but may also work with ISO files.
CHD files can be created easily from cue/bin format using the `chdman` tool.

#### BIOS files

BIOS files can be uploaded the same as games. However, the name of the shortcut should reflect the name of the file that the emulator is looking for without the file extension.

Also, select the "Hide" option, so the BIOS file is not shown in Steam along with other games.

### System

You can access some system settings via the "System" page, reachable at <http://chimeraos.local:8844/system>.

#### Storage

TBD

#### Logging in

Every time you use the web application, you'll be prompted for a custom password which will be displayed by the system running ChimeraOS. If you want, you can change this behavior and configure a fixed password instead.

#### SSH

SSH allows you to access the command line of your ChimeraOS machine remotely.\
You can add your public key by pasting it in the relevant field, then click on "Save" at the bottom of the page. If the operation is successful, you'll see your public key listed below the "Add public key" field once tha page reloads.

**NOTE:** the application will only accept public keys that match the following criteria:

- the key is made of _three_ components, space separated:
  - the key type (e.g. ssh-rsa, ssh-ed25519, etc.)
  - the base64-encoded key
  - a comment
- the key type starts with `ssh-`

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
- **compat_config**: the configuration for the compatibility tool specified, e.g. for proton: `d9vk`, `noesync`, etc. see the [Proton docs](https://github.com/ValveSoftware/Proton#runtime-config-options) for the full list of available options
- **launch_options**: the launch options to be used
- **steam_input**: a value of `enabled` will force the use of Steam Input for the specified game

#### Example entry

```yaml
"321040":
  compat_tool: proton_411
  compat_config: noesync
  launch_options: MY_VARIABLE=1 %command%
  steam_input: enabled
```

Each game is specified by its Steam app ID. Note that the app ID MUST be quoted.

### Steam Shortcuts (chimera --shortcuts)

Reads one or more YAML formatted shortcut definition files stored under `~/.local/share/chimera/shortcuts/` and adds the shortcuts to all available Steam accounts.

#### Single shortcut per file example

```yaml
name: Firefox                   # name of the shortcut as it will appear in Steam (required)
cmd: firefox                    # the command to execute (required)
dir: /full/path/to/working/dir  # the directory from which to execute the command
params: github.com              # any parameters to invoke the command with
banner: /path/to/image.png      # the horizontal banner image to use (460x215)
poster: /path/to/image.png      # the vertical poster image to use (600x900)
background: /path/to/image.png  # the background/hero image to use (1920x620)
logo: /path/to/image.png        # the logo image to use (overlaid on top of background image)
icon: firefox                   # small icon to show in Steam
compat_tool: proton_9           # use the given compatibility tool, useful for running Windows executables
compat_config: noesync          # use the given compatibility tool options
hidden: false                   # 'false' to show the shortcut in Steam, 'true' to hide it
tags:                           # a list of tags to be assigned to the shortcut in Steam
  - Browser
  - Custom Shortcut
```

#### Multiple shortcuts per file example

```yaml
- name: Firefox
  cmd: firefox
  ...
- name: Chromium
  cmd: chromium
  ...
```

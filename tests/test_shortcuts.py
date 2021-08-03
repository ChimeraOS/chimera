"""Unit tests for relevant shortcuts module functions"""

import os
import pytest
import chimera_app.context as context
import chimera_app.shortcuts as shortcuts
from chimera_app.shortcuts import ShortcutsFile
from chimera_app.shortcuts import SteamShortcutsFile


@pytest.fixture
def empty_data(fs):
    fs.create_dir(os.path.expanduser('~'))
    yield fs


@pytest.fixture
def fake_data(fs,
              monkeypatch):
    files_path = os.path.join(os.path.dirname(__file__), 'files')

    fs.create_dir(os.path.expanduser('~/.cache'))
    fs.create_dir(os.path.expanduser('~/.local/share/chimera'))
    fs.create_dir(os.path.expanduser('~/.local/share/Steam/config'))
    fs.create_dir(os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678'))
    fs.add_real_file(os.path.join(files_path, 'steam-tweaks.yaml'),
                     target_path=os.path.expanduser(
                         '~/.local/share/chimera/data/tweaks/steam.yaml')
                     )
    fs.add_real_file(os.path.join(files_path, 'test-shortcuts-single.yaml'),
                     target_path=os.path.expanduser(
                         '~/.local/share/chimera/shortcuts/single.yaml')
                     )
    fs.add_real_file(os.path.join(files_path, 'test-shortcuts-multi.yaml'),
                     target_path=os.path.expanduser(
                         '~/.local/share/chimera/shortcuts/multi.yaml')
                     )

    # Patch STEAM_USER_DIRS as per pyfakefs limitations
    monkeypatch.setattr(context, 'STEAM_USER_DIRS',
                        [os.path.expanduser(
                            '~/.local/share/Steam/userdata/12345678')]
                        )
    yield fs


def test_steam_shortcuts_load_empty(empty_data):
    steam_short = SteamShortcutsFile('12345678')

    assert(not steam_short.exists())

    steam_short.load_data()

    assert(steam_short.get_shortcuts_data() == {})


def test_shortcuts_load_data_single(fake_data):
    shortcut_path = os.path.expanduser(
        '~/.local/share/chimera/shortcuts/single.yaml')

    file = ShortcutsFile(shortcut_path)
    file.load_data()

    assert(file.shortcuts_data[0]['name'] == 'Firefox')
    assert(file.shortcuts_data[0]['cmd'] == 'firefox')
    assert(file.shortcuts_data[0]['dir'] == '~')
    assert(file.shortcuts_data[0]['tags'] == ['Native'])


def test_shortcuts_load_data_multi(fake_data):
    shortcut_path = os.path.expanduser(
        '~/.local/share/chimera/shortcuts/multi.yaml')

    file = ShortcutsFile(shortcut_path)
    file.load_data()

    assert(file.shortcuts_data[0]['name'] == 'SuperTux Native')
    assert(file.shortcuts_data[0]['cmd'] == 'supertux2')
    assert(file.shortcuts_data[0]['dir'] == '~')
    assert(file.shortcuts_data[0]['tags'] == ['Native'])

    assert(file.shortcuts_data[1]['name'] == 'SuperTux')
    assert(file.shortcuts_data[1]['cmd'] == 'flatpak run')
    assert(file.shortcuts_data[1]['dir'] == '~')
    assert(file.shortcuts_data[1]['tags'] == ['Flathub'])


def test_static_get_banner_id():
    exe = "flatpak run"
    name = "SuperTuxKart"

    # banner id: 10898728827895152640
    assert(shortcuts.get_banner_id(exe, name) == 10898728827895152640)


def test_static_get_compat_id():
    exe = "$(gog-launcher 1207659723)"
    name = "Flight of the Amazon Queen"

    # compat id: 2967756109
    assert(shortcuts.get_compat_id(exe, name) == 2967756109)


def test_static_get_shortcut_id():
    exe = "flatpak run"
    name = "SuperTuxKart"

    # shortcut id: -1757409248
    assert(shortcuts.get_shortcut_id(exe, name) == -1757409248)

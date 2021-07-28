"""Unit tests for relevant shortcuts module functions"""

import os
import tempfile
from chimera_app.shortcuts import ChimeraShortcuts as CShort


def test_static_load_shortcuts():
    yaml_content = '\n'.join(
        ['- name: Firefox',
         '  cmd: firefox',
         '- name: Chromium',
         '  cmd: chromium']
    )
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(yaml_content.encode())
    tmp_file.close()

    # Read the file
    s = CShort.load_shortcuts(tmp_file.name)
    try:
        assert(s[0]['name'] == 'Firefox')
        assert(s[0]['cmd'] == 'firefox')
        assert(s[1]['name'] == 'Chromium')
        assert(s[1]['cmd'] == 'chromium')
    finally:
        tmp_file.close()
        os.unlink(tmp_file.name)


def test_static_load_steam_shortcuts():
    yaml_content = '\n'.join(
        ['- name: Firefox',
         '  cmd: firefox',
         '- name: Chromium',
         '  cmd: chromium']
    )
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(yaml_content.encode())
    tmp_file.close()

    # Read the file
    s = CShort.load_shortcuts(tmp_file.name)
    try:
        assert(s[0]['name'] == 'Firefox')
        assert(s[0]['cmd'] == 'firefox')
        assert(s[1]['name'] == 'Chromium')
        assert(s[1]['cmd'] == 'chromium')
    finally:
        tmp_file.close()
        os.unlink(tmp_file.name)


def test_static_get_banner_id():
    exe = "flatpak run"
    name = "SuperTuxKart"

    # banner id: 10898728827895152640
    assert(CShort.get_banner_id(exe, name) == 10898728827895152640)


def test_static_get_compat_id():
    exe = "$(gog-launcher 1207659723)"
    name = "Flight of the Amazon Queen"

    # banner id: 10898728827895152640
    assert(CShort.get_compat_id(exe, name) == 2967756109)


def test_static_get_shortcut_id():
    exe = "flatpak run"
    name = "SuperTuxKart"

    # banner id: 10898728827895152640
    assert(CShort.get_shortcut_id(exe, name) == -1757409248)

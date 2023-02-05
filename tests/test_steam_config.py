"""Unit tests for steam_config module relevant functions"""

import os
import pytest
import vdf
import chimera_app.context as context
from chimera_app.steam_config import MainSteamConfig
from chimera_app.steam_config import LocalSteamConfig
from chimera_app.steam_config import TweaksFile


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

    # Patch STEAM_USER_DIRS as per pyfakefs limitations
    monkeypatch.setattr(context, 'STEAM_USER_DIRS',
                        [os.path.expanduser(
                            '~/.local/share/Steam/userdata/12345678')]
                        )
    yield fs


def test_main_config_file_empty(empty_data):
    main_config = MainSteamConfig()

    assert(not main_config.exists())

    main_config.load_data()
    main_config.save()

    assert(main_config.exists())

    with open(context.STEAM_CONFIG_FILE) as config_file:
        config_data = vdf.load(config_file)

    assert('CompatToolMapping' in config_data['InstallConfigStore']
                                             ['Software']
                                             ['Valve']
                                             ['Steam'])


def test_local_config_file_empty(empty_data):
    local_config = LocalSteamConfig('12345678')

    assert(not local_config.exists())

    local_config.load_data()
    local_config.save()

    assert(local_config.exists())

    with open(local_config.path) as config_file:
        config_data = vdf.load(config_file)

    assert('apps' in config_data['UserLocalConfigStore'])
    assert('apps' in config_data['UserLocalConfigStore']
                                ['Software']
                                ['Valve']
                                ['Steam'])


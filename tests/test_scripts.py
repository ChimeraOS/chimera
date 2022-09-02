"Integration tests for our scripts"

import os
import json
import vdf
import pytest
import chimera_app
import chimera_app.shortcuts as shortcuts
import chimera_app.compat_tools as compat_tools
import chimera_app.data as chimera_data


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
    fs.add_real_directory(os.path.join(files_path,
                                       'tools',
                                       'Proton-6.10-GE-1'),
                          target_path=os.path.expanduser(
                              ('~/.local/share/chimera/data/'
                               'compat/tools/Proton-6.10-GE-1')
                                                         )
                          )
    fs.add_real_file(os.path.join(files_path, 'steam-tweaks.yaml'),
                     target_path=os.path.expanduser(
                         '~/.local/share/chimera/data/tweaks/steam.yaml')
                     )
    fs.add_real_file(os.path.join(files_path, 'tool-stub.tpl'),
                     target_path=os.path.expanduser(
                         ('~/.local/share/chimera/data/'
                          'compat/tool-stub.tpl')
                                                    )
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
    monkeypatch.setattr(chimera_app.context, 'STEAM_USER_DIRS',
                        [os.path.expanduser(
                            '~/.local/share/Steam/userdata/12345678')]
                        )
    yield fs


@pytest.fixture
def branches_content():
    files_path = os.path.join(os.path.dirname(__file__), 'files')
    branches_mock = os.path.join(files_path, "branches.json")
    with open(branches_mock) as branches_file:
        content = json.load(branches_file)
    yield content


@pytest.fixture
def zip_content():
    files_path = os.path.join(os.path.dirname(__file__), 'files')
    zip_mock = os.path.join(files_path, "test.zip")
    yield open(zip_mock, 'rb').read()


@pytest.fixture
def branches_mock(requests_mock,
                  branches_content):
    api_url = 'https://api.github.com/repos/chimeraos/chimera-data/branches'
    requests_mock.get(api_url,
                      json=branches_content)
    yield requests_mock


@pytest.fixture
def data_mock(requests_mock,
              zip_content):
    api_url = ('https://github.com/chimeraos/chimera-data/archive/'
               '6fd2a1af5ae6cd0acef222908374fe6ba8164083.zip')
    requests_mock.get(api_url,
                      content=zip_content)
    yield requests_mock


def test_update_with_empty(branches_mock,
                           branches_content,
                           data_mock,
                           zip_content,
                           empty_data):
    version_file = os.path.expanduser(
        "~/.local/share/chimera/data/versions.json"
    )
    branches_file = os.path.expanduser(
        "~/.local/share/chimera/data/branches.json"
    )
    assert (not os.path.exists(version_file))
    assert (not os.path.exists(branches_file))

    chimera_data.update_data()

    assert (os.path.exists(version_file))
    assert (os.path.exists(branches_file))

    with open(branches_file) as file:
        branches = json.load(file)

    assert (branches == branches_content)


def test_compat_with_empty(empty_data):
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')

    compat_tools.install_all_compat_tools()

    assert (not os.path.exists(compat_tools_dir))
    assert (not os.path.exists(proton_ge_dir))


def test_shortcuts_with_empty(empty_data):
    shortcuts_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/shortcuts.vdf')

    shortcuts.create_all_shortcuts()

    assert (not os.path.exists(shortcuts_file))


def test_compat_with_data(fake_data):
    "Test compat-tools installation effects"
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')

    compat_tools.install_all_compat_tools()

    assert (os.path.exists(proton_ge_dir))
    assert (os.path.exists(os.path.join(proton_ge_dir, 'proton')))
    assert (os.path.exists(os.path.join(proton_ge_dir, 'toolmanifest.vdf')))
    assert (os.path.exists(os.path.join(proton_ge_dir,
                                        'compatibilitytool.vdf')))


def test_shortcuts_with_data(fake_data):
    shortcuts_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/shortcuts.vdf')

    shortcuts.create_all_shortcuts()

    assert (os.path.exists(shortcuts_file))
    sh_data = vdf.binary_load(open(shortcuts_file, 'rb'))
    assert (sh_data['shortcuts']['0']['AppName'] == 'Firefox')
    assert (sh_data['shortcuts']['1']['AppName'] == 'SuperTux Native')
    assert (sh_data['shortcuts']['2']['AppName'] == 'SuperTux')

"Integration tests for our scripts"

import os
import vdf
import pytest
import chimera_app
import chimera_app.shortcuts as shortcuts
import chimera_app.steam_config as steam_config
import chimera_app.compat_tools as compat_tools


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
                          'compat/tools/tool-stub.tpl')
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


def test_config_with_empty(empty_data):
    config_file = os.path.expanduser(
        '~/.local/share/Steam/config/config.vdf')
    user_config_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/localconfig.vdf')

    steam_config.apply_all_tweaks()

    assert(not os.path.exists(config_file))
    assert(not os.path.exists(user_config_file))


def test_compat_with_empty(empty_data):
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')

    compat_tools.install_all_compat_tools()

    assert(not os.path.exists(proton_ge_dir))


def test_shortcuts_with_empty(empty_data):
    shortcuts_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/shortcuts.vdf')

    shortcuts.create_all_shortcuts()

    assert(not os.path.exists(shortcuts_file))


def test_config_with_data(fake_data):
    "Test effects of tweaks with downloaded files"

    config_file = os.path.expanduser(
        '~/.local/share/Steam/config/config.vdf')
    user_config_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/localconfig.vdf')

    steam_config.apply_all_tweaks()

    assert(os.path.exists(config_file))
    conf_vdf = vdf.load(open(config_file))
    compat = (conf_vdf['InstallConfigStore']['Software']['Valve']['Steam']
              ['CompatToolMapping'])
    assert(compat['221380']['name'] == 'proton_411')
    assert(compat['409710']['name'] == 'proton_513')
    assert(compat['409710']['config'] == 'noesync,nofsync')

    assert(os.path.exists(user_config_file))
    conf_vdf = vdf.load(open(user_config_file))
    launch_options = (conf_vdf['UserLocalConfigStore']['Software']['Valve']
                      ['Steam']['Apps'])
    assert(launch_options['285820']['LaunchOptions'] ==
           'LD_LIBRARY_PATH= %command%')
    assert(launch_options['331870']['LaunchOptions'] ==
           '%command% -screen-fullscreen 0')
    assert(launch_options['409710']['LaunchOptions'] == '-nointro')

    steam_input = conf_vdf['UserLocalConfigStore']['Apps']
    assert(steam_input['285820']['UseSteamControllerConfig'] == '2')


def test_compat_with_data(fake_data):
    "Test compat-tools installation effects"
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')

    compat_tools.install_all_compat_tools()

    assert(os.path.exists(proton_ge_dir))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'proton')))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'toolmanifest.vdf')))
    assert(os.path.exists(os.path.join(proton_ge_dir,
                                       'compatibilitytool.vdf')))


def test_shortcuts_with_data(fake_data):
    shortcuts_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/12345678/config/shortcuts.vdf')

    shortcuts.create_all_shortcuts()

    assert(os.path.exists(shortcuts_file))
    sh_data = vdf.binary_load(open(shortcuts_file, 'rb'))
    assert(sh_data['shortcuts']['0']['AppName'] == 'Firefox')
    assert(sh_data['shortcuts']['1']['AppName'] == 'SuperTux Native')
    assert(sh_data['shortcuts']['2']['AppName'] == 'SuperTux')

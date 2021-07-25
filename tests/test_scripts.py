"Integration tests for our scripts"

import time
import os
import pytest
import vdf
from chimera_app.steam_config import SteamConfig as SC
from chimera_app.steam_config import apply_all_tweaks
from chimera_app.compat_tools import install_all_compat_tools
from chimera_app.utils import ChimeraContext as CC


@pytest.fixture
def fake_data(monkeypatch,
              fs):
    files_path = os.path.join(os.path.dirname(__file__), 'files')

    fs.add_real_file(os.path.join(files_path, 'steam-tweaks.yaml'),
                     target_path='/usr/share/chimera/steam-tweaks.yaml')
    fs.add_real_file(os.path.join(files_path,
                                  '..',
                                  '..',
                                  'steam-compat-tool-stub.tpl'),
                     target_path='/usr/share/chimera/steam-compat-tool-stub.tpl')
    fs.add_real_directory(os.path.join(files_path,
                                       '..',
                                       '..',
                                       'compat-tools',
                                       'Proton-6.10-GE-1'),
                          target_path='/usr/share/chimera/compat-tools/Proton-6.10-GE-1')
    fs.create_dir(os.path.expanduser('~/.local/share/chimera'))
    fs.create_dir(os.path.expanduser('~/.local/share/Steam/config'))
    fs.create_dir(os.path.expanduser('~/.local/share/Steam/userdata/user-id/'))

    yield fs


def test_config_static(monkeypatch,
                       requests_mock,
                       fake_data):
    "Test effects of tweaks with static file"

    url = ('https://raw.githubusercontent.com/ChimeraOS/'
           'chimera/master/steam-tweaks.yaml')
    tweaks_file = os.path.expanduser(
        '~/.local/share/chimera/steam-tweaks.yaml')
    static_file = '/usr/share/chimera/steam-tweaks.yaml'

    config_file = os.path.expanduser(
        '~/.local/share/Steam/config/config.vdf')
    user_config_file = os.path.expanduser(
        '~/.local/share/Steam/userdata/user-id/config/localconfig.vdf')

    monkeypatch.setattr(time, 'sleep', lambda s: None)
    requests_mock.get(url, status_code=404)

    apply_all_tweaks()

    assert(os.path.exists(tweaks_file))
    assert(open(tweaks_file).read() == open(static_file).read())

    assert(os.path.exists(config_file))
    conf_vdf = vdf.load(open(config_file))
    compat = conf_vdf['InstallConfigStore']['Software']['Valve']['Steam']['CompatToolMapping']
    assert(compat['221380']['name'] == 'proton_411')
    assert(compat['409710']['name'] == 'proton_513')
    assert(compat['409710']['config'] == 'noesync,nofsync')

    assert(os.path.exists(user_config_file))
    conf_vdf = vdf.load(open(user_config_file))
    launch_options = conf_vdf['UserLocalConfigStore']['Software']['Valve']['Steam']['Apps']
    assert(launch_options['285820']['LaunchOptions'] == 'LD_LIBRARY_PATH= %command%')
    assert(launch_options['331870']['LaunchOptions'] == '%command% -screen-fullscreen 0')
    assert(launch_options['409710']['LaunchOptions'] == '-nointro')

    steam_input = conf_vdf['UserLocalConfigStore']['Apps']
    assert(steam_input['285820']['UseSteamControllerConfig'] == '2')


def test_compat_static(fake_data):
    "Test compat-tools installation effects"
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')

    install_all_compat_tools()

    assert(os.path.exists(proton_ge_dir))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'proton')))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'toolmanifest.vdf')))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'compatibilitytool.vdf')))

import os
import time
import tempfile
import pytest
import vdf
from chimera_app.steam_config import SteamConfig as SC


@pytest.fixture
def tweaks_url():
    """Returns the url used to fetch the online tweaks file"""
    url = ('https://raw.githubusercontent.com/ChimeraOS/'
           'chimera/master/steam-tweaks.yaml')
    return url


@pytest.fixture
def main_config_content():
    """Returns a VDF content of an example steam config.vdf file"""
    data = {
        'InstallConfigStore': {
            'Software': {
                'Valve': {
                    'Steam': {
                        'CompatToolMapping': {
                            '654321': {
                                'name': 'proton_411',
                                'config': 'noesync,nofsync',
                                'Priority': '209'
                            }
                        }
                    }
                }
            }
        }
    }
    return vdf.VDFDict(data)


@pytest.fixture
def local_config_content():
    """Returns a VDF content of an example steam config.vdf file"""
    data = {
        'UserLocalConfigStore': {
            'Software': {
                'Valve': {
                    'Steam': {
                        'Apps': {
                            '654321': {
                                'LaunchOptions': '--option'
                            }
                        }
                    }
                }
            },
            'Apps': {
                '654321': {
                    'UseSteamControllerConfig': '1',
                    'SteamControllerRumble': '-1',
                    'SteamControllerRumbleIntensity': '320',
                    'EnableSCTenFootOverlayCheckNew': '1'
                }
            }
        }
    }
    return vdf.VDFDict(data)


@pytest.fixture
def main_config_file(main_config_content):
    tmp_file_static = tempfile.NamedTemporaryFile(delete=False)
    vdf.dump(main_config_content,
             open(tmp_file_static.name, 'w'),
             pretty=True)
    tmp_file_static.close()
    yield tmp_file_static
    tmp_file_static.close()
    os.unlink(tmp_file_static.name)


@pytest.fixture
def local_config_file(local_config_content):
    tmp_file_static = tempfile.NamedTemporaryFile(delete=False)
    vdf.dump(local_config_content,
             open(tmp_file_static.name, 'w'),
             pretty=True)
    tmp_file_static.close()
    yield tmp_file_static
    tmp_file_static.close()
    os.unlink(tmp_file_static.name)


@pytest.fixture
def local_config_file_empty():
    """This fixture will yield a temporary file to use as local config file"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    yield tmp_file
    tmp_file.close()
    os.unlink(tmp_file.name)


@pytest.fixture
def main_config_file_empty():
    """This fixture will yield a temporary file to use as main config file"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    yield tmp_file
    tmp_file.close()
    os.unlink(tmp_file.name)


@pytest.fixture
def tweaks_content():
    """This will return a test content for a tweaks file"""
    yaml_content = '\n'.join(
        ['"12345678":',
         '  compat_tool: compat_tool',
         '',
         '"321040":',
         '  compat_tool: proton_411',
         '  compat_config: noesync',
         '  launch_options: MY_VARIABLE=1 %command%',
         '  steam_input: enabled']
    )
    return yaml_content


@pytest.fixture
def tweaks_url_content(requests_mock,
                       tweaks_url,
                       tweaks_content):
    """This mocks the content of a tweaks file downloaded from our site"""
    requests_mock.get(tweaks_url, content=tweaks_content.encode())


@pytest.fixture
def tweaks_not_found(requests_mock,
                     monkeypatch,
                     tweaks_url):
    """Mock a 404 code when searching for the tweaks file online"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    requests_mock.get(tweaks_url, status_code=404)


@pytest.fixture
def tweaks_file_empty():
    """This fixture will yield a temporary file to use as user tweaks file"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    yield tmp_file
    tmp_file.close()
    os.unlink(tmp_file.name)


@pytest.fixture
def static_tweaks_file(tweaks_content):
    """This fixture will yield a static tweaks file as if where delivered
    with the chimera package
    """
    tmp_file_static = tempfile.NamedTemporaryFile(delete=False)
    open(tmp_file_static.name, 'wb').write(tweaks_content.encode())
    tmp_file_static.close()
    yield tmp_file_static
    tmp_file_static.close()
    os.unlink(tmp_file_static.name)


def test_success_download_tweaks_file(tweaks_content,
                                      tweaks_url_content,
                                      tweaks_file_empty):
    """Test a successful download"""
    assert(SC.download_tweaks_file(tweaks_file_empty.name))
    assert(tweaks_file_empty.read() == tweaks_content.encode())


def test_failure_download_tweaks_file(tweaks_not_found,
                                      tweaks_file_empty):
    """Test a download failure of tweaks file with no static fallback"""
    assert(not SC.download_tweaks_file(tweaks_file_empty.name,
                                    num_attempts=1)
           )


def test_static_download_tweaks_file(tweaks_content,
                                     tweaks_not_found,
                                     tweaks_file_empty,
                                     static_tweaks_file):
    """Test a download failure of tweaks file with static file fallback"""
    assert(SC.download_tweaks_file(tweaks_file_empty.name,
                                   num_attempts=1,
                                   static_file=static_tweaks_file.name
                                   )
           )
    assert(open(tweaks_file_empty.name).read() == tweaks_content)


def test_load_main(main_config_file,
                   main_config_content):
    config = SC.load_main(main_config_file.name)
    assert(vdf.load(open(main_config_file.name)) == config)


def test_load_local(local_config_file,
                    local_config_content):
    config = SC.load_local(local_config_file.name)
    assert(vdf.load(open(local_config_file.name)) == config)


def test_write(local_config_content,
               main_config_content,
               local_config_file_empty,
               main_config_file_empty):
    SC.write(local_config_content,
             local_config_file_empty.name)
    SC.write(main_config_content,
             main_config_file_empty.name)

    mf_content = vdf.load(open(main_config_file_empty.name))
    assert(mf_content['InstallConfigStore'] == main_config_content['InstallConfigStore'])
    steam_file = mf_content['InstallConfigStore']['Software']['Valve']['Steam']
    steam_data = main_config_content['InstallConfigStore']['Software']['Valve']['Steam']
    assert(steam_file['CompatToolMapping'] == steam_data['CompatToolMapping'])

    lf_content = vdf.load(open(local_config_file_empty.name))
    assert(lf_content['UserLocalConfigStore'] == local_config_content['UserLocalConfigStore'])


def test_apply_to_main_config(static_tweaks_file,
                              main_config_content):
    SC.apply_to_main_config(static_tweaks_file.name, main_config_content, priority=209)

    compat = main_config_content['InstallConfigStore']['Software']['Valve']['Steam']['CompatToolMapping']
    assert(compat['12345678']['name'] == 'compat_tool')
    assert(compat['12345678']['Priority'] == 209)


def test_apply_to_local_config(static_tweaks_file,
                               local_config_content):
    SC.apply_to_local_config(static_tweaks_file.name, local_config_content)

    launch_options = local_config_content['UserLocalConfigStore']['Software']['Valve']['Steam']['Apps']
    assert(launch_options['321040']['LaunchOptions'] == 'MY_VARIABLE=1 %command%')

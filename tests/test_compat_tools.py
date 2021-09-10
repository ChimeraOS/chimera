"""Test relevant compat_tools module functions"""

import os
import pytest
from chimera_app.compat_tools import ExternalCompatTool


@pytest.fixture
def fake_data(fs,
              monkeypatch):
    files_path = os.path.join(os.path.dirname(__file__), 'files')

    fs.create_dir(os.path.expanduser('~/.cache'))
    fs.create_dir(os.path.expanduser('~/.local/share/chimera'))
    fs.add_real_directory(os.path.join(files_path,
                                       'tools',
                                       'Proton-6.10-GE-1'),
                          target_path=os.path.expanduser(
                              ('~/.local/share/chimera/data/'
                               'compat/tools/Proton-6.10-GE-1')
                                                         )
                          )
    fs.add_real_file(os.path.join(files_path, 'tool-stub.tpl'),
                     target_path=os.path.expanduser(
                         ('~/.local/share/chimera/data/'
                          'compat/tool-stub.tpl')
                                                    )
                     )

    yield fs


def test_external_compat_tool_install(fake_data):
    compat_tools_dir = os.path.expanduser(
        '~/.local/share/Steam/compatibilitytools.d')
    proton_ge_dir = os.path.join(compat_tools_dir, 'Proton-6.10-GE-1')
    chimera_data_tools = os.path.expanduser(
        '~/.local/share/chimera/data/compat/tools'
    )
    stub_tpl_path = os.path.expanduser('~/.local/share/chimera/data/compat/tool-stub.tpl')

    tool = ExternalCompatTool('Proton-6.10-GE-1',
                              ExternalCompatTool.load_stub_info(
                                  'Proton-6.10-GE-1',
                                  stub_tpl_path)
                              )
    tool.install()

    assert(os.path.exists(proton_ge_dir))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'proton')))
    assert(os.path.exists(os.path.join(proton_ge_dir, 'toolmanifest.vdf')))
    assert(os.path.exists(os.path.join(proton_ge_dir,
                                       'compatibilitytool.vdf')))

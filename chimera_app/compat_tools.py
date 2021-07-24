"""Submodule to handle compatibility tools related functions"""

import os
import shutil
from chimera_app.utils import ChimeraContext
from chimera_app.utils import ensure_directory
from chimera_app.utils import directory_exists
from chimera_app.utils import replace_all


def install_all_compat_tools():
    cc = ChimeraContext()
    ensure_directory(cc.STEAM_COMPAT_TOOLS)
    for tool_dir in os.listdir(cc.STATIC_COMPAT_TOOLS):
        steam_tool = os.path.join(cc.STEAM_COMPAT_TOOLS, tool_dir)
        static_tool = os.path.join(cc.STATIC_COMPAT_TOOLS, tool_dir)
        if not directory_exists(steam_tool):
            shutil.copytree(static_tool,
                            steam_tool)
            si = CompatToolStubInfo.load_stub_info(os.path.join(static_tool, 'stub.info'))
            ct = CompatTool(si)
            ct.write_stub(steam_tool)


class CompatToolStubInfo():
    """Compat tool stub info"""
    url: str
    md5sum: str
    cmd: str

    def __init__(self, url, md5sum, cmd):
        self.url = url
        self.md5sum = md5sum
        self.cmd = cmd

    @classmethod
    def load_stub_info(cls, stub_path):
        """Read a stub.info file from stub_path and parse it into a
        CompatToolStubInfo object.
        """
        data = {}
        with open(stub_path) as f:
            for line in f.readlines():
                key, value = line.rstrip("\n").split("=")
                data[key] = value
        return CompatToolStubInfo(data['TOOL_URL'],
                                  data['TOOL_MD5SUM'],
                                  data['TOOL_CMD'])


class CompatTool():
    """Class to manage compatibility tools"""

    _context: ChimeraContext
    _template: str
    stub: CompatToolStubInfo

    def __init__(self, stub_info):
        self._context = ChimeraContext()
        self._template = open(os.path.join(self._context.STATIC_DATA,
                              'steam-compat-tool-stub.tpl'),
                              'r').read()
        self.stub = stub_info

    def write_stub(self,
                   path):
        replacements = {
            '%TOOL_URL%': self.stub.url,
            '%TOOL_MD5SUM%': self.stub.md5sum,
            '%TOOL_CMD%': self.stub.cmd
        }
        stub_path = os.path.join(path, self.stub.cmd)
        with open(stub_path, 'w') as stub_file:
            stub_file.write(replace_all(self._template, replacements))
        os.chmod(stub_path, 0o775)

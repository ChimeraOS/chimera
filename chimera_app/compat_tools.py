"""Submodule to handle compatibility tools related functions"""

import os
import shutil
import chimera_app.context as context
from chimera_app.utils import ensure_directory
from chimera_app.utils import replace_all


def install_all_compat_tools():
    tools_dir = context.TOOLS_DIR
    stub_file = os.path.join(tools_dir, 'tool-stub.tpl')
    if (not os.path.isdir(tools_dir)
            or (not os.path.isfile(stub_file))):
        print(f'No tools to install from {tools_dir} or missing stub template')
        return

    ensure_directory(context.STEAM_COMPAT_TOOLS)
    for tool_dir in os.listdir(tools_dir):
        steam_tool = os.path.join(context.STEAM_COMPAT_TOOLS, tool_dir)
        tool = os.path.join(context.TOOLS_DIR, tool_dir)
        if not os.path.isdir(tool):
            continue
        if not os.path.isdir(steam_tool):
            shutil.copytree(tool,
                            steam_tool)
            si = CompatToolStubInfo.load_stub_info(
                os.path.join(tool, 'stub.info'))
            ct = CompatTool(stub_file, si)
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

    _template: str
    stub: CompatToolStubInfo

    def __init__(self, template_path, stub_info):
        self._template = open(template_path, 'r').read()
        self.stub = stub_info

    def write_stub(self,
                   tool_path):
        replacements = {
            '%TOOL_URL%': self.stub.url,
            '%TOOL_MD5SUM%': self.stub.md5sum,
            '%TOOL_CMD%': self.stub.cmd
        }
        stub_path = os.path.join(tool_path, self.stub.cmd)
        with open(stub_path, 'w') as stub_file:
            stub_file.write(replace_all(self._template, replacements))
        os.chmod(stub_path, 0o775)

"""Submodule to handle compatibility tools related functions"""

import os
import shutil
from abc import ABC
from abc import abstractmethod
import chimera_app.context as context
from chimera_app.file_utils import ensure_directory
from chimera_app.utils import replace_all
from chimera_app.utils import client_running
from chimera_app.utils import install_by_id


# Hardcode this for now (taken from setamdb.info),
# should be read from downloaded data.
OFFICIAL_COMPAT_TOOLS = {
    "proton_37":            "858280",
    "proton_37_beta":       "930400",
    "proton_316":           "961940",
    "proton_316_beta":      "996510",
    "proton_42":            "1054830",
    "proton_411":           "1113280",
    "proton_5":             "1245040",
    "proton_513":           "1420170",
    "proton_experimental":  "1493710",
    "proton_63":            "1580130",
    "proton_7":             "1887720",
    "proton_8":             "2348590"
}


def install_all_compat_tools() -> bool:
    """Install all external compatibility tools downloaded by chimera.
    If there are no compatibility tools to install or the stub template is
    missing this will take no action.

    Tools are installed in a lazy way leaving a stub for the real install
    process to begin when the tool is needed (at first run with a game that
    uses it). If a tool is found with the same name already installed it will
    take no action.

    Returns True if sucessful or False if there are no tools to install.
    """
    tools_dir = context.TOOLS_DIR
    if (not os.path.isdir(tools_dir)
            or (not os.path.isfile(context.TOOLS_TEMPLATE_FILE))):
        print(f'No tools to install from {tools_dir} or missing stub template')
        return False

    for entry in os.scandir(tools_dir):
        if not entry.is_dir():
            continue
        tool_name = entry.name
        tool = ExternalCompatTool(tool_name,
                                  ExternalCompatTool.load_stub_info(
                                      tool_name,
                                      context.TOOLS_TEMPLATE_FILE)
                                  )
        if not os.path.exists(tool.get_install_path()):
            tool.install()

    return True


class CompatToolStub():
    """Compat tool stub info"""
    url: str
    md5sum: str
    cmd: str
    _template: str

    def __init__(self, tpl_path: str, url: str, md5sum: str, cmd: str):
        self.url = url
        self.md5sum = md5sum
        self.cmd = cmd
        with open(tpl_path) as tpl_file:
            self._template = tpl_file.read()

    def install_stub(self, tool_path: str):
        """Install stub file on give tool_path"""
        replacements = {
            '%TOOL_URL%': self.url,
            '%TOOL_MD5SUM%': self.md5sum,
            '%TOOL_CMD%': self.cmd
        }
        stub_path = os.path.join(tool_path, self.cmd)
        with open(stub_path, 'w') as stub_file:
            stub_file.write(replace_all(self._template, replacements))
        os.chmod(stub_path, 0o775)


class AbsCompatTool(ABC):
    """Abstract class to represent compatibility tools"""

    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def install(self):
        """Install this compatibility tool"""


class OfficialCompatTool(AbsCompatTool):
    """Steam official compatibility tool"""

    tool_id: str

    def __init__(self, name: str, tool_id: str):
        self.tool_id = tool_id
        super().__init__(name)

    def install(self):
        if client_running():
            install_by_id(self.tool_id)
        else:
            raise Exception('Steam client not running')


class ExternalCompatTool(AbsCompatTool):
    """Additional compatibility tool that Steam can use"""

    tool_stub: CompatToolStub

    def __init__(self, name: str, tool_stub: CompatToolStub):
        self.tool_stub = tool_stub
        super().__init__(name)

    def get_install_path(self):
        return os.path.join(context.STEAM_COMPAT_TOOLS, self.name)

    def install(self):
        ensure_directory(context.STEAM_COMPAT_TOOLS)
        install_path = self.get_install_path()
        shutil.copytree(os.path.join(context.TOOLS_DIR, self.name),
                        install_path)
        self.tool_stub.install_stub(install_path)

    @staticmethod
    def load_stub_info(tool_name: str, tpl_path: str) -> CompatToolStub:
        """Read a stub.info file from stub_path and parse it into a
        CompatToolStubInfo object.
        """
        data = {}
        stub_path = os.path.join(context.TOOLS_DIR, tool_name, 'stub.info')
        with open(stub_path) as stub_file:
            for line in stub_file.readlines():
                key, value = line.rstrip("\n").split("=")
                data[key] = value
        return CompatToolStub(tpl_path,
                              data['TOOL_URL'],
                              data['TOOL_MD5SUM'],
                              data['TOOL_CMD'])

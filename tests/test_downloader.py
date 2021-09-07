import os
import json
import pytest
from chimera_app.data import Downloader


@pytest.fixture
def empty_data(fs):
    "Mock an empty home directory as it should be on the first run"
    fs.create_dir(os.path.expanduser('~'))
    yield fs


@pytest.fixture
def updatable_fs(empty_data):
    files_path = os.path.join(os.path.dirname(__file__), 'files')
    empty_data.add_real_file(os.path.join(files_path, 'versions.json'),
                             target_path=os.path.expanduser(
                                '~/.local/share/chimera/data/versions.json'),
                             read_only=False,
                             )
    empty_data.add_real_file(os.path.join(files_path, 'branches.json'),
                             target_path=os.path.expanduser(
                                '~/.local/share/chimera/data/branches.json'),
                             read_only=False
                             )

    yield empty_data


@pytest.fixture
def branches_content():
    files_path = os.path.join(os.path.dirname(__file__), 'files')
    branches_mock = os.path.join(files_path, "branches.json")
    yield open(branches_mock).read()


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


def test_fetch_latest(branches_mock,
                      branches_content,
                      empty_data):
    branches_file = os.path.expanduser(
        '~/.local/share/chimera/data/branches.json')

    downloader = Downloader()
    downloader.fetch_latest()
    assert(os.path.exists(branches_file))
    with open(branches_file) as file:
        branches = json.load(file)

    branches_json = json.loads(branches_content)

    assert(branches == branches_json)


def test_download_updated(branches_mock,
                          updatable_fs):
    downloader = Downloader()
    assert(not downloader.check_update())


def test_download_package(data_mock,
                          updatable_fs):
    data_path = os.path.expanduser('~/.local/share/chimera/data/data.zip')

    downloader = Downloader()
    downloader.download_package('6fd2a1af5ae6cd0acef222908374fe6ba8164083')
    assert(os.path.exists(data_path))


def test_download_update(branches_mock,
                         data_mock,
                         updatable_fs):
    downloader = Downloader()
    assert(not downloader.check_update())
    assert(downloader.update())

    assert(downloader.get_installed_version() ==
           '6fd2a1af5ae6cd0acef222908374fe6ba8164083')

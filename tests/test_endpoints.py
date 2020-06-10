import os
from webtest import TestApp
from steam_buddy import server
from steam_buddy.config import PLATFORMS, AUTHENTICATOR_PATH


def test_runs(monkeypatch):
    def mock_launch(self):
        if not os.path.isfile(AUTHENTICATOR_PATH):
            raise FileNotFoundError("Authenticator not found at path {}".format(AUTHENTICATOR_PATH))

    from steam_buddy.authenticator import Authenticator
    monkeypatch.setattr(Authenticator, 'launch', mock_launch)

    app = TestApp(server)
    assert app.get('/login').status == '200 OK'


def test_platform_images():
    app = TestApp(server)
    for platform, name in PLATFORMS.items():
        assert app.get('/images/{}.png'.format(platform)).status == '200 OK'

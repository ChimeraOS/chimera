from webtest import TestApp
from steam_buddy import server
from steam_buddy.config import PLATFORMS


def test_runs(monkeypatch):
    def mock_launch(self):
        pass

    from steam_buddy.authenticator import Authenticator
    monkeypatch.setattr(Authenticator, 'launch', mock_launch)

    app = TestApp(server)
    assert app.get('/login').status == '200 OK'


def test_platform_images():
    app = TestApp(server)
    for platform, name in PLATFORMS.items():
        assert app.get('/images/{}.png'.format(platform)).status == '200 OK'

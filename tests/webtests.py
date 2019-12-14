import unittest
from webtest import TestApp
from steam_buddy import server
from steam_buddy.config import PLATFORMS


class WebTests(unittest.TestCase):

    def test_home(self):
        app = TestApp(server)

        assert app.get('/').status == '200 OK'

    def test_platform_pages(self):
        app = TestApp(server)
        for platform, name in PLATFORMS.items():
            assert app.get('/platforms/{}'.format(platform)).status == '200 OK'

    def test_platform_images(self):
        app = TestApp(server)
        for platform, name in PLATFORMS.items():
            assert app.get('/images/{}.png'.format(platform)).status == '200 OK'


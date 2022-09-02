import os
import pytest
import subprocess
from webtest import TestApp
from chimera_app.server import server
from chimera_app.server import PLATFORM_HANDLERS
from chimera_app.config import PLATFORMS
from chimera_app.config import BIN_PATH


# Prevent pytest from trying to collect webtest's TestApp as tests:
TestApp.__test__ = False


@pytest.fixture
def unauthorized_app(monkeypatch):
    def mock_launch(self):
        if not os.path.isdir(BIN_PATH):
            raise FileNotFoundError(
                f'Authenticator not found at path {BIN_PATH}'
            )

    from chimera_app.authenticator import Authenticator
    monkeypatch.setattr(Authenticator, 'launch', mock_launch)
    monkeypatch.delattr(subprocess, "call", raising=True)
    monkeypatch.delattr(os, "system", raising=True)

    yield TestApp(server)


def test_login_page(unauthorized_app):
    assert (unauthorized_app.get('/login').status == '200 OK')


def test_root(unauthorized_app):
    resp = unauthorized_app.get('/')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_page(unauthorized_app):
    for platform in PLATFORMS:
        resp = unauthorized_app.get(f'/library/{platform}')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_authenticate(unauthorized_app):
    for platform in PLATFORM_HANDLERS:
        resp = unauthorized_app.post(f'/library/{platform}/authenticate')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_new(unauthorized_app):
    for platform in PLATFORMS:
        resp = unauthorized_app.get('/library/{platform}/new')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_edit(unauthorized_app):
    for platform in PLATFORMS:
        resp = unauthorized_app.get('/library/{platform}/edit/giberish')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_flathub_images(unauthorized_app):
    resp = unauthorized_app.get('/images/flathub/giberish')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_create(unauthorized_app):
    resp = unauthorized_app.post('/shortcuts/new')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_edit(unauthorized_app):
    resp = unauthorized_app.post('/shortcuts/edit')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_delete(unauthorized_app):
    resp = unauthorized_app.post('/shortcuts/delete')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_file_upload_post(unauthorized_app):
    resp = unauthorized_app.post('/shortcuts/file-upload')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_file_upload_patch(unauthorized_app):
    resp = unauthorized_app.patch('/shortcuts/file-upload')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_file_upload_head(unauthorized_app):
    resp = unauthorized_app.head('/shortcuts/file-upload')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_shortcuts_file_upload_delete(unauthorized_app):
    resp = unauthorized_app.delete('/shortcuts/file-upload')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_install(unauthorized_app):
    for platform in PLATFORM_HANDLERS:
        resp = unauthorized_app.get(f'/{platform}/install/giberish')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_uninstall(unauthorized_app):
    for platform in PLATFORM_HANDLERS:
        resp = unauthorized_app.get(f'/{platform}/uninstall/giberish')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_update(unauthorized_app):
    for platform in PLATFORM_HANDLERS:
        resp = unauthorized_app.get(f'/{platform}/update/giberish')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_platform_progress(unauthorized_app):
    for platform in PLATFORM_HANDLERS:
        resp = unauthorized_app.get(f'/{platform}/update/giberish')
        assert(resp.status_code == 302)
        assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_settings(unauthorized_app):
    resp = unauthorized_app.get('/system')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_settings_update(unauthorized_app):
    resp = unauthorized_app.post('/system/update')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_mangohud_reset(unauthorized_app):
    resp = unauthorized_app.post('/system/reset_mangohud')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_steam_restart(unauthorized_app):
    resp = unauthorized_app.get('/actions/steam/restart')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_steam_compositor(unauthorized_app):
    resp = unauthorized_app.get('/actions/steam/compositor')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_steam_overlay(unauthorized_app):
    resp = unauthorized_app.get('/actions/steam/overlay')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_mangohud(unauthorized_app):
    resp = unauthorized_app.get('/actions/mangohud')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming(unauthorized_app):
    resp = unauthorized_app.get('/streaming')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_config(unauthorized_app):
    resp = unauthorized_app.get('/streaming/config')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_add_input(unauthorized_app):
    resp = unauthorized_app.post('/streaming/add_input')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_remove_input(unauthorized_app):
    resp = unauthorized_app.post('/streaming/remove_input/123456')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_add_vcodec(unauthorized_app):
    resp = unauthorized_app.post('/streaming/add_vcodec')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_remove_vcodec(unauthorized_app):
    resp = unauthorized_app.post('/streaming/remove_vcodec/123456')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_add_acodec(unauthorized_app):
    resp = unauthorized_app.post('/streaming/add_acodec')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_streaming_remove_acodec(unauthorized_app):
    resp = unauthorized_app.post('/streaming/remove_acodec/123456')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_record_start(unauthorized_app):
    resp = unauthorized_app.get('/record/start')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_record_stop(unauthorized_app):
    resp = unauthorized_app.get('/record/stop')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_mangohud_save_config(unauthorized_app):
    resp = unauthorized_app.post('/system/mangohud/save_config')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_mangohud_edit_config(unauthorized_app):
    resp = unauthorized_app.get('/system/mangohud/edit_config')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_retroarch_load_state(unauthorized_app):
    resp = unauthorized_app.get('/actions/retroarch/load_state')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_retroarch_save_state(unauthorized_app):
    resp = unauthorized_app.get('/actions/retroarch/save_state')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_virtual_keyboard(unauthorized_app):
    resp = unauthorized_app.get('/virtual_keyboard')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_virtual_keyboard_string(unauthorized_app):
    resp = unauthorized_app.post('/virtual_keyboard/string')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_reboot_system(unauthorized_app):
    resp = unauthorized_app.get('/actions/reboot')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_poweroff(unauthorized_app):
    resp = unauthorized_app.get('/actions/poweroff')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_suspend(unauthorized_app):
    resp = unauthorized_app.get('/actions/suspend')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_toggle_mute(unauthorized_app):
    resp = unauthorized_app.get('/actions/audio/toggle_mute')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_volume_up(unauthorized_app):
    resp = unauthorized_app.get('/actions/audio/volume_up')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_volume_down(unauthorized_app):
    resp = unauthorized_app.get('/actions/audio/volume_down')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')


def test_audio_profile(unauthorized_app):
    resp = unauthorized_app.get('/audio/profile')
    assert(resp.status_code == 302)
    assert(resp.headers['Location'] == 'http://localhost:80/login')

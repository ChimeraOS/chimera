import os
import sys
import importlib
from tidylib import tidy_document
from bottle import request
sys.modules["chimera_app.auth_decorator"] = \
        importlib.import_module("tests.stubs.auth_decorator")
from chimera_app.server import \
        platforms, \
        platform_page, \
        new, \
        settings, \
        logout, \
        login, \
        mangohud_edit, \
        streaming_config, \
        virtual_keyboard
from chimera_app.config import PLATFORMS, BIN_PATH


def validate_html(endpoint, document):
    """
    This function can be used to make sure HTML returned is valid
    It raises an exception describing what's wrong then non-valid HTML was
    entered
    :param endpoint: name of the function which returned the html content
    :param document: the html content
    :return: None
    """
    _, errors = tidy_document(document, options={"show-warnings": "no"})
    if errors:
        raise SystemError(
            f"Errors were found in the following HTML returned by function"
            f" {endpoint}:\n"
            f"{document}\n\n"
            f"Errors:\n{errors}"
        )


def test_platforms():
    document = platforms()
    validate_html("platforms", document)


def test_platform():
    for p in PLATFORMS:
        if p != 'epic-store' and p != 'flathub':
            document = platform_page(p)
            validate_html("platform({})".format(p), document)


def test_new():
    for p in PLATFORMS:
        if p not in ['epic-store', 'flathub', 'gog']:
            document = new(p)
            validate_html("new({})".format(p), document)


def test_settings():
    request.environ["HTTP_HOST"] = "localhost:8844"
    document = settings()
    validate_html("settings", document)


def test_mangohud_edit():
    document = mangohud_edit()
    validate_html('mangohud_edit', document)


def test_streaming_config():
    document = streaming_config()
    validate_html('streaming_config', document)


def test_virtual_keyoard():
    document = virtual_keyboard()
    validate_html('virtual_keyboard', document)


def test_logout():
    class mock_session:
        def delete(self):
            pass
    request.environ["beaker.session"] = mock_session()
    document = logout()
    validate_html("logout", document)


def test_login(monkeypatch):
    def mock_launch(self):
        if not os.path.isdir(BIN_PATH):
            raise FileNotFoundError(f"No authenticators at path {BIN_PATH}")

    from chimera_app.authenticator import Authenticator
    monkeypatch.setattr(Authenticator, 'launch', mock_launch)

    document = login()
    validate_html("login", document)

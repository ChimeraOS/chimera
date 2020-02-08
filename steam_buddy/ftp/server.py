import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class Server:

    def __init__(self, settings):
        self.settings = settings
        self.username = self.settings.get_setting("ftp_username")
        self.password = self.settings.get_setting("ftp_password")
        self.port = self.settings.get_setting("ftp_port")
        self.enabled = self.settings.get_setting("enable_ftp_server")
        self.__server = None

    def run(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, os.environ['HOME'], perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer

        self.__server = FTPServer(('0.0.0.0', self.port), handler)

        if self.enabled:
            ftp_thread = threading.Thread(target=self.__server.serve_forever)
            ftp_thread.daemon = True
            ftp_thread.start()

    def stop(self):
        if self.__server:
            self.__server.close_all()

    def reload(self):
        new_enabled = self.settings.get_setting("enable_ftp_server")
        new_username = self.settings.get_setting("ftp_username")
        new_password = self.settings.get_setting("ftp_password")
        new_port = self.settings.get_setting("ftp_port")

        # Check if any of the values were changed
        settings_were_changed = False
        if new_enabled != self.enabled:
            self.enabled = new_enabled
            settings_were_changed = True
        if new_username != self.username:
            self.username = new_username
            settings_were_changed = True
        if new_password != self.password:
            self.password = new_password
            settings_were_changed = True
        if new_port != self.port:
            self.port = new_port
            settings_were_changed = True

        # Reload the server if any changes were found
        if settings_were_changed:
            self.stop()
            self.run()

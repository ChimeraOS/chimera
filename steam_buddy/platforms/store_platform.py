import subprocess
import threading
from io import BytesIO


# allow accessing dictionary items as object attributes
class dic(object):
    def __init__(self, d):
        self.__dict__ = d


class StorePlatform:
    def __init__(self):
        self.tasks = {}

    def get_installed_content(self) -> list:
        pass

    def get_available_content(self) -> list:
        pass

    def get_content(self, content_id):
        app = None
        apps = self.get_installed_content()
        results = list(filter(lambda app: app.content_id == content_id, apps))
        if len(results) > 0:
            app = results[0]

        if not app:
            apps = self.get_available_content()
            apps = list(filter(lambda app: app.content_id == content_id, apps))
            if len(apps) < 1:
                return
            app = apps[0]

        app.progress = None
        app.operation = None
        if content_id in self.tasks:
            app.progress = self.tasks[content_id].progress
            app.operation = self.tasks[content_id].operation

        return app

    def uninstall_content(self, content_id):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._uninstall(content_id), content_id, 'Uninstalling'))
        thread.start()

    def install_content(self, content_id):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._install(content_id), content_id, 'Installing'))
        thread.start()

    def update_content(self, content_id):
        thread = threading.Thread(target=self._update_progress,
                                  args=(self._update(content_id), content_id, 'Updating'))
        thread.start()

    def get_shortcut(self, content):
        pass

    def _update_progress(self, sp: subprocess, content_id, opName):
        if content_id in self.tasks or sp is None:
            return
        task = dic({'progress': -1, 'operation': opName})
        self.tasks[content_id] = task
        buf = BytesIO()
        while sp.poll() is None:
            out = sp.stdout.read(1)
            buf.write(out)
            if out in (b'\r', b'\n'):
                for value in buf.getvalue().split():
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    if "%" in value:
                        task.progress = int(value.replace("%", "").split('.')[0])
                buf.truncate(0)
        del self.tasks[content_id]

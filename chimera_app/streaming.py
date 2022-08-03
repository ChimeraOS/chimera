from shlex import split
from os.path import expanduser
from subprocess import Popen
from subprocess import TimeoutExpired
from chimera_app.file_utils import ensure_directory


class StreamServer:

    def __init__(self, settings_handler):
        self.settings = settings_handler
        self._ffmpeg = None

    def __start_ffmpeg(self, local=False):
        recordings_dir = self.settings.get_setting("recordings_dir")
        ensure_directory(recordings_dir)

        INPUTS = self.settings.get_setting("ffmpeg_inputs")
        VCODEC = self.settings.get_setting("ffmpeg_vcodec")
        ACODEC = self.settings.get_setting("ffmpeg_acodec")
        OUTPUT_FORMAT = "-f matroska"
        STREAM = "screen_" + str(time.strftime("%Y%m%d_%H%M%S")) + ".mkv"

        # Build the ffmpeg command line
        cmd = ["ffmpeg"]
        for i in INPUTS:
            cmd.append(i)
        cmd.append(VCODEC)
        cmd.append(ACODEC)
        cmd.append(OUTPUT_FORMAT)
        cmd.append(STREAM)

        print(cmd)
        args = split(" ".join(cmd))
        print(args)
        if self._ffmpeg is None:
            self._ffmpeg = Popen(args,
                                 cwd=expanduser(recordings_dir))
        else:
            raise(Exception("Error starting FFMpeg: Already started"))

    def __stop_ffmpeg(self):
        self._ffmpeg.terminate()
        try:
            self._ffmpeg.wait(5)
        except TimeoutExpired:
            self._ffmpeg.kill()
        self._ffmpeg = None

    def record_screen(self):
        self.__start_ffmpeg(local=True)

    def stop_record(self):
        self.__stop_ffmpeg()

    def is_recording(self):
        return True if (self._ffmpeg and not self._sls) else False

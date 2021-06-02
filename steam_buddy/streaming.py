from shlex import split
from time import strftime
from os.path import expanduser
from subprocess import Popen
from subprocess import TimeoutExpired
from steam_buddy.utils import ensure_directory


class StreamServer:

    def __init__(self, settings_handler):
        self.settings = settings_handler
        self._sls = None
        self._ffmpeg = None

    def __generate_sls_conf(self):
        pass

    def __start_sls(self):
        sls_conf_file = self.settings.get_setting("sls_conf_file")
        if self._sls is None:
            self._sls = Popen(['sls', '-c', sls_conf_file])
        else:
            raise(Exception("Error starting SLS: Already started"))

    def __stop_sls(self):
        self._sls.terminate()
        try:
            self._sls.wait(5)
        except TimeoutExpired:
            self._sls.kill()
        self._sls = None

    def __start_ffmpeg(self, local=False):
        recordings_dir = self.settings.get_setting("recordings_dir")
        ensure_directory(recordings_dir)

        INPUTS = self.settings.get_setting("ffmpeg_inputs")
        VCODEC = self.settings.get_setting("ffmpeg_vcodec")
        ACODEC = self.settings.get_setting("ffmpeg_acodec")

        if local:
            OUTPUT_FORMAT = "-f matroska"
            STREAM = "screen_" + \
                str(time.strftime("%Y%m%d_%H%M%S")) + \
                ".mkv"
        else:
            OUTPUT_FORMAT = "-f mpegts -flush_packets 0"
            STREAM = '"srt://localhost:8080?streamid=uplive.gameros/live/stream"'

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

    def stream_to_lan(self):
        self.__start_sls()
        self.__start_ffmpeg()

    def stop_stream(self):
        self.__stop_ffmpeg()
        self.__stop_sls()

    def record_screen(self):
        self.__start_ffmpeg(local=True)

    def stop_record(self):
        self.__stop_ffmpeg()

    def is_recording(self):
        return True if (self._ffmpeg and not self._sls) else False

    def is_streaming(self):
        return True if (self._ffmpeg and self._sls) else False

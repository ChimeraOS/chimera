import os
import shlex
import time
import subprocess as sp


class StreamServer:

    def __init__(self, sls_conf_file):
        self.sls_conf_file = sls_conf_file
        self._sls = None
        self._ffmpeg = None

    def __generate_sls_conf(self):
        pass

    def __start_sls(self):
        if self._sls is None:
            self._sls = sp.Popen(['sls', '-c', self.sls_conf_file])
        else:
            raise(Exception("Error starting SLS: Already started"))

    def __stop_sls(self):
        self._sls.terminate()
        try:
            self._sls.wait(5)
        except sp.TimeoutExpired:
            self._sls.kill()
        self._sls = None

    def __start_ffmpeg(self, local=False):
        VCODEC = "libx264"
        VCODEC_OPTIONS = "-preset ultrafast -tune zerolatency"
        VSIZE = "1920x1080"
        ACODEC = "libmp3lame"
        ACODEC_OPTIONS = ""
        FPS = "60"

        if local:
            STREAM = "screen_" + \
                    str(time.strftime("%Y%m%d_%H%M%S")) + \
                    ".mp4"
        else:
            STREAM = '"srt://localhost:8080?streamid=uplive.gameros/live/stream"'

        cmd = ["ffmpeg",
               "-f x11grab -framerate", FPS, "-i :0",
               "-f alsa -ac 2 -i pulse",
               "-vcodec", VCODEC, VCODEC_OPTIONS,
               "-acodec", ACODEC, ACODEC_OPTIONS,
               "-video_size", VSIZE,
               "-flush_packets 0",
               "-f mpegts",
               STREAM]
        args = shlex.split(" ".join(cmd))
        if self._ffmpeg is None:
            self._ffmpeg = sp.Popen(args, cwd=os.path.expanduser("~"))
        else:
            raise(Exception("Error starting FFMpeg: Already started"))

    def __stop_ffmpeg(self):
        self._ffmpeg.terminate()
        try:
            self._ffmpeg.wait(5)
        except sp.TimeoutExpired:
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

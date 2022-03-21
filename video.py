from time import time
from skvideo.io import FFmpegWriter


class VideoWriter:
    def __init__(self, root, fps, ext="mp4") -> None:
        self.root = root
        self.started = False
        self.fps = fps
        self.ext = ext

    def write_color(self, data):
        self.writer_color.writeFrame(data)

    def write_depth(self, data):
        self.writer_depth.writeFrame(data)

    def start(self):
        timestamp = str(int(time()))
        self.writer_color = FFmpegWriter(
            f"{self.root}/{timestamp}_color.{self.ext}",
            inputdict={"-r": str(self.fps)},
            outputdict={"-r": str(self.fps), "-vcodec": "libx264"},
        )
        self.writer_depth = FFmpegWriter(
            f"{self.root}/{timestamp}_depth.{self.ext}",
            inputdict={"-r": str(self.fps)},
            outputdict={"-r": str(self.fps), "-vcodec": "libx264"},
        )
        self.started = True

    def end(self):
        self.writer_color.close()
        self.writer_depth.close()
        self.started = False

    def toggle(self):
        if self.started:
            self.end()
        else:
            self.start()

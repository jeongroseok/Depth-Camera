from time import time


class VideoWriter:
    def __init__(self, root) -> None:
        self.root = root
        self.started = False

    def write(self, qEncoderRgb, qEncoderDepth):
        while qEncoderRgb.has():
            qEncoderRgb.get().getData().tofile(self.videoFileRgb)

        while qEncoderDepth.has():
            qEncoderDepth.get().getData().tofile(self.videoFileDepth)

    def start(self):
        timestamp = str(int(time()))
        self.videoFileRgb = open(f"{self.root}/{timestamp}_color.mp4", "wb")
        self.videoFileDepth = open(f"{self.root}/{timestamp}_depth.mp4", "wb")
        self.started = True

    def end(self):
        self.videoFileRgb.close()
        self.videoFileDepth.close()
        self.started = False

    def toggle(self):
        if self.started:
            self.end()
        else:
            self.start()

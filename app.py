import json
from time import time

from guizero import App, Box, Picture, PushButton
from PIL import Image

from camera import create_device

SCREEN = (480, 320)
FPS = 24


class VideoSaver:
    def __init__(self, root) -> None:
        self.root = root
        self.started = False

    def push_center(self, data):
        data.tofile(self.file_center)

    def push_stereo(self, data):
        data.tofile(self.file_stereo)

    def start(self):
        timestamp = str(int(time()))
        self.file_center = open(f"{self.root}/{timestamp}_center.mp4", "wb")
        self.file_stereo = open(f"{self.root}/{timestamp}_stereo.mp4", "wb")
        self.started = True

    def end(self):
        self.file_center.close()
        self.file_stereo.close()
        self.started = False

    def toggle(self):
        if self.started:
            self.end()
        else:
            self.start()


def main():
    with open("config.json") as file:
        root = json.load(file)["path"]

    with create_device(FPS, SCREEN) as device:
        video_saver = VideoSaver(root)

        # setup queues
        queue_center = device.getOutputQueue(name="center", maxSize=FPS, blocking=True)
        queue_stereo = device.getOutputQueue(name="stereo", maxSize=FPS, blocking=True)
        queue_preview = device.getOutputQueue(
            name="center_preview", maxSize=1, blocking=False
        )

        # setup gui
        app = App(title="Camera", width=SCREEN[0], height=SCREEN[1])
        box = Box(app, width="fill", align="bottom")
        button = PushButton(box, width="fill", text="Start", command=video_saver.toggle)
        picture = Picture(app, align="top")

        def update():
            button.text = "STOP" if video_saver.started else "START"
            if video_saver.started:
                while queue_center.has():
                    video_saver.push_center(queue_center.get().getData())
                while queue_stereo.has():
                    video_saver.push_stereo(queue_stereo.get().getData())

            if queue_preview.has():
                image = queue_preview.get().getCvFrame()
                image = Image.fromarray(image)
                picture.image = image

        app.repeat(int(1000 / FPS), update)
        app.display()


if __name__ == "__main__":
    main()

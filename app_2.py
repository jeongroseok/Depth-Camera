from display import clear, print
from button import get_button_value
from camera import create_device
from time import time

with create_device() as device:
    queue_center = device.getOutputQueue(name="center", maxSize=30, blocking=True)
    queue_stereo = device.getOutputQueue(name="stereo", maxSize=30, blocking=True)

    while True:
        if get_button_value():
            timestamp = str(int(time()))
            with open(f"home/pi/{timestamp}_center.mp4", "wb") as file_center, open(
                f"home/pi/{timestamp}_stereo.mp4", "wb"
            ) as file_stereo:
                while get_button_value():
                    print(f"STATUS:RECORDING\nNAME:{timestamp}")
                    while queue_center.has():
                        queue_center.get().getData().tofile(file_center)
                    while queue_stereo.has():
                        queue_stereo.get().getData().tofile(file_stereo)
        else:
            print("STATUS:READY    \n                ")


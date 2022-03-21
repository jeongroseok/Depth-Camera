import argparse

import cv2
import depthai as dai
from depthai_sdk.managers import PipelineManager
from depthai_sdk.previews import Previews

from pairing_system import PairingSystem
from video import VideoWriter

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", type=str, default=".", help="save path")
parser.add_argument("-f", "--fps", type=float, default=8, help="fps")
parser.add_argument(
    "-sc", "--screen_size", type=tuple, default=(480, 320), help="screeen size"
)

args = parser.parse_args()

cam_list = {
    Previews.color.name: 0,
    Previews.disparity.name: 1,
}

# Start defining a pipeline
pipeline_manager = PipelineManager()

pipeline_manager.createColorCam(
    previewSize=(1280, 720),
    res=dai.ColorCameraProperties.SensorResolution.THE_1080_P,
    fps=args.fps,
    xout=True,
)
pipeline_manager.createLeftCam(
    res=dai.MonoCameraProperties.SensorResolution.THE_720_P, fps=args.fps
)
pipeline_manager.createRightCam(
    res=dai.MonoCameraProperties.SensorResolution.THE_720_P, fps=args.fps
)
pipeline_manager.createDepth(useDisparity=True)

video_writer = VideoWriter(args.path, args.fps)


def on_mouse(event, x, y, flags, params):
    global video_writer
    if event == cv2.EVENT_LBUTTONUP:
        video_writer.toggle()
    pass


# Pipeline defined, now the device is assigned and pipeline is started
with dai.Device(pipeline_manager.pipeline) as device:
    queues = {}
    for key, value in cam_list.items():
        queues[key] = device.getOutputQueue(name=key, maxSize=4, blocking=False)
    ps = PairingSystem(allowed_instances=list(cam_list.values()))

    window_title = "Camera"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_title, args.screen_size)
    cv2.setMouseCallback(window_title, on_mouse)

    while True:
        for c in cam_list:
            ps.add_packet(queues[c].tryGet())

        for synced in ps.get_pairs():
            frame, seqnum, tstamp = {}, {}, {}
            for c in cam_list:
                pkt = synced[cam_list[c]]
                frame[c] = pkt.getCvFrame()
                seqnum[c] = pkt.getSequenceNum()

            if not (seqnum[Previews.color.name] == seqnum[Previews.disparity.name]):
                print("ERROR: out of sync!!!")

            if video_writer.started:
                color = cv2.cvtColor(frame[Previews.color.name], cv2.COLOR_BGR2RGB)
                video_writer.write_color(color)
                depth = cv2.cvtColor(frame[Previews.disparity.name], cv2.COLOR_GRAY2RGB)
                video_writer.write_depth(depth)

            output = cv2.resize(frame[Previews.color.name], args.screen_size)
            output = cv2.putText(
                output,
                "STOP" if video_writer.started else "START",
                (0, args.screen_size[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(window_title, output)

            key = cv2.waitKey(int(1000 / args.fps))

#!/usr/bin/env python3
import argparse

import cv2
import depthai as dai

from utils import VideoWriter

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", type=str, default=".", help="save path")
parser.add_argument("-f", "--fps", type=float, default=8, help="fps")
args = parser.parse_args()

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
rgb = pipeline.create(dai.node.ColorCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
monoLeft = pipeline.create(dai.node.MonoCamera)
depth = pipeline.create(dai.node.StereoDepth)
encoderRgb = pipeline.create(dai.node.VideoEncoder)
encoderDepth = pipeline.create(dai.node.VideoEncoder)

xoutVideoRgb = pipeline.create(dai.node.XLinkOut)
xoutVideoDepth = pipeline.create(dai.node.XLinkOut)
xoutRgb = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")
xoutVideoRgb.setStreamName("video_rgb")
xoutVideoDepth.setStreamName("video_depth")

# Properties
rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
rgb.setFps(args.fps)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
monoRight.setFps(args.fps)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
monoLeft.setFps(args.fps)
encoderRgb.setDefaultProfilePreset(
    fps=args.fps, profile=dai.VideoEncoderProperties.Profile.H264_HIGH
)
encoderDepth.setDefaultProfilePreset(
    fps=args.fps, profile=dai.VideoEncoderProperties.Profile.H264_HIGH
)

depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
depth.setRectifyEdgeFillColor(0)  # Black, to better see the cutout

# Linking
rgb.isp.link(xoutRgb.input)
rgb.video.link(encoderRgb.input)
monoRight.out.link(depth.right)
monoLeft.out.link(depth.left)
depth.disparity.link(encoderDepth.input)
encoderRgb.bitstream.link(xoutVideoRgb.input)
encoderDepth.bitstream.link(xoutVideoDepth.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue("rgb", 1, blocking=False)
    qEncoderRgb = device.getOutputQueue("video_rgb", maxSize=30, blocking=False)
    qEncoderDepth = device.getOutputQueue("video_depth", maxSize=30, blocking=False)

    frame = None

    videoWriter = VideoWriter(args.path)

    def on_click(event, x, y, flags, params):
        global videoWriter
        if event == cv2.EVENT_LBUTTONUP:
            videoWriter.toggle()
        pass

    window_title = "CAM"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_title, on_click)

    while True:
        inRgb = qRgb.tryGet()

        if inRgb is not None:
            frame = inRgb.getCvFrame()

        if videoWriter.started:
            videoWriter.write(qEncoderRgb, qEncoderDepth)

        if frame is not None:
            output = cv2.resize(frame, (300, 200))
            output = cv2.putText(
                output,
                "STOP" if videoWriter.started else "START",
                (0, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(window_title, output)

        if cv2.waitKey(1) == ord("q"):
            break

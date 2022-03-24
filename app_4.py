#!/usr/bin/env python3
import argparse

import cv2
import depthai as dai

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", type=str, default=".", help="save path")
parser.add_argument("-f", "--fps", type=float, default=8, help="fps")

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
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
encoderRgb.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)
encoderDepth.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)

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
    qEncoderRgb = device.getOutputQueue("video_rgb", maxSize=30, blocking=True)
    qEncoderDepth = device.getOutputQueue("video_depth", maxSize=30, blocking=True)

    frame = None

    started = False
    videoFileRgb = open("../../../video.mp4", "wb")
    videoFileDepth = open("../../../video_d.mp4", "wb")

    def on_mouse(event, x, y, flags, params):
        global started
        if event == cv2.EVENT_LBUTTONUP:
            started = not started
        pass
    cv2.setMouseCallback(window_title, on_mouse)

    while True:
        inRgb = qRgb.tryGet()

        while qEncoderRgb.has():
            qEncoderRgb.get().getData().tofile(videoFileRgb)

        while qEncoderDepth.has():
            qEncoderDepth.get().getData().tofile(videoFileDepth)

        if inRgb is not None:
            frame = inRgb.getCvFrame()

        if frame is not None:
            output = cv2.resize(frame, (300, 200))
            output = cv2.putText(
                output,
                "STOP" if started else "START",
                (0, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("rgb", output)

        if cv2.waitKey(1) == ord("q"):
            break

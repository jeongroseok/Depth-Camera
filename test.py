import cv2
import numpy as np
import depthai
import depthai.node
import http.server
import socketserver
from os.path import expanduser
from time import time

PORT = 80
EXTENDED_DISPARITY = False
SUBPIXEL = False
LR_CHECK = True


def main():
    pipeline = depthai.Pipeline()

    # Define sources and outputs
    color = pipeline.create(depthai.node.ColorCamera)
    mono_left: depthai.node.MonoCamera = pipeline.create(depthai.node.MonoCamera)
    mono_right: depthai.node.MonoCamera = pipeline.create(depthai.node.MonoCamera)
    depth: depthai.node.StereoDepth = pipeline.create(depthai.node.StereoDepth)
    depth_out: depthai.node.XLinkOut = pipeline.create(depthai.node.XLinkOut)
    rgb_out: depthai.node.XLinkOut = pipeline.create(depthai.node.XLinkOut)

    depth_out.setStreamName("disparity")
    rgb_out.setStreamName("rgb")

    # Properties
    color.setPreviewSize(640, 480)
    color.setInterleaved(False)
    color.setColorOrder(depthai.ColorCameraProperties.ColorOrder.RGB)
    color.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)

    mono_left.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_left.setBoardSocket(depthai.CameraBoardSocket.LEFT)

    mono_right.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setBoardSocket(depthai.CameraBoardSocket.RIGHT)

    depth.setDefaultProfilePreset(depthai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    depth.initialConfig.setMedianFilter(depthai.MedianFilter.KERNEL_7x7)
    depth.setLeftRightCheck(LR_CHECK)
    depth.setExtendedDisparity(EXTENDED_DISPARITY)
    depth.setSubpixel(SUBPIXEL)

    # Linking
    mono_left.out.link(depth.left)
    mono_right.out.link(depth.right)
    depth.disparity.link(depth_out.input)
    color.video.link(rgb_out.input)

    with depthai.Device(pipeline) as device:
        print("device created")
        queue_disparity = device.getOutputQueue(
            name="disparity", maxSize=4, blocking=False
        )
        queue_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                path = self.path.split("?")[0]
                if path == "/images":
                    self.send_response(302)
                    self.send_header("Location", "/")
                    self.end_headers()

                    timestamp = time()

                    frame_rgb = queue_rgb.get().getCvFrame()
                    cv2.imwrite(f"{expanduser('~')}/{timestamp}c.png", frame_rgb)

                    frame_disparity = queue_disparity.get().getFrame()
                    frame_disparity = (
                        frame_disparity
                        * (255.0 / depth.initialConfig.getMaxDisparity())
                    ).astype(np.uint8)
                    cv2.imwrite(f"{timestamp}d.png", frame_disparity)

            def do_GET(self):
                path = self.path.split("?")[0]
                if path == "/depth":
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()

                    frame_disparity = queue_disparity.get().getFrame()
                    frame_disparity = (
                        frame_disparity
                        * (255.0 / depth.initialConfig.getMaxDisparity())
                    ).astype(np.uint8)
                    result, buffer = cv2.imencode(".png", frame_disparity)
                    self.wfile.write(buffer.tobytes())
                elif path == "/rgb":
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()

                    frame_rgb = queue_rgb.get().getCvFrame()
                    result, buffer = cv2.imencode(".png", frame_rgb)
                    self.wfile.write(buffer.tobytes())
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    content = open("index.html").read().encode("utf-8")
                    self.wfile.write(content)

        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server listening on port {PORT}...")
            httpd.serve_forever()


if __name__ == "__main__":
    main()

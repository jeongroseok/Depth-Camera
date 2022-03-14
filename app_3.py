from depthai import (
    Device,
    Pipeline,
    ColorCameraProperties,
    MonoCameraProperties,
    VideoEncoderProperties,
    CameraBoardSocket,
    MedianFilter,
)
from depthai.node import ColorCamera, MonoCamera, XLinkOut, StereoDepth, VideoEncoder


def main():
    fps = 24
    pipeline = Pipeline()

    # setup outs
    out_center = pipeline.create(XLinkOut)
    out_center.setStreamName("center")
    out_stereo = pipeline.create(XLinkOut)
    out_stereo.setStreamName("stereo")

    # setup center camera
    center = pipeline.create(ColorCamera)
    center.setBoardSocket(CameraBoardSocket.RGB)
    center.setResolution(ColorCameraProperties.SensorResolution.THE_1080_P)
    center.setFps(fps)

    # setup left mono camera
    left = pipeline.create(MonoCamera)
    left.setBoardSocket(CameraBoardSocket.LEFT)
    left.setResolution(MonoCameraProperties.SensorResolution.THE_720_P)
    left.setFps(fps)

    # setup left mono camera
    right = pipeline.create(MonoCamera)
    right.setBoardSocket(CameraBoardSocket.RIGHT)
    right.setResolution(MonoCameraProperties.SensorResolution.THE_720_P)
    right.setFps(fps)

    # setup stereo camera
    stereo = pipeline.create(StereoDepth)
    stereo.setDefaultProfilePreset(StereoDepth.PresetMode.HIGH_DENSITY)
    stereo.setLeftRightCheck(True)
    stereo.setDepthAlign(CameraBoardSocket.RGB)
    stereo.initialConfig.setMedianFilter(MedianFilter.KERNEL_7x7)
    stereo.setExtendedDisparity(False)
    stereo.setSubpixel(False)

    # setup video encoder
    encoder_center = pipeline.create(VideoEncoder)
    encoder_center.setDefaultProfilePreset(
        center.getFps(), VideoEncoderProperties.Profile.H264_MAIN
    )
    encoder_stereo = pipeline.create(VideoEncoder)
    encoder_stereo.setDefaultProfilePreset(
        center.getFps(), VideoEncoderProperties.Profile.H264_MAIN
    )

    # linking
    center.video.link(encoder_center.input)
    left.out.link(stereo.left)
    right.out.link(stereo.right)
    stereo.disparity.link(encoder_stereo.input)
    encoder_center.bitstream.link(out_center.input)
    encoder_stereo.bitstream.link(out_stereo.input)

    with Device(pipeline) as device:
        queue_center = device.getOutputQueue(name="center")
        queue_stereo = device.getOutputQueue(name="stereo")

        with open("center.mp4", "wb") as file_center, open(
            "stereo.mp4", "wb"
        ) as file_stereo:
            while True:
                try:
                    while queue_center.has():
                        queue_center.get().getData().tofile(file_center)
                    while queue_stereo.has():
                        queue_stereo.get().getData().tofile(file_stereo)
                except KeyboardInterrupt:
                    break


if __name__ == "__main__":
    main()

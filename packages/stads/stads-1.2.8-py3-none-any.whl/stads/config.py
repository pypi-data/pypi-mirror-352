import importlib.resources
from .read_images import get_frames_from_mp4


# Now load the reference frames
SIGMA = 4
KERNEL_SIZE = int(SIGMA * 3) + 1

with importlib.resources.path("stads.ground_truth", "dendrites_one.mp4") as video_path:
    REFERENCE_VIDEO_SEQUENCE = get_frames_from_mp4(str(video_path), 100)
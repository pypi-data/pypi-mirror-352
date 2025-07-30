import numpy as np
from .config import REFERENCE_VIDEO_SEQUENCE


def sample_image_from_video_sequence(yCoords, xCoords, imageShape, frameNumber):
    sampledImage = np.zeros(imageShape)
    sampledImage[yCoords, xCoords] = REFERENCE_VIDEO_SEQUENCE[frameNumber][yCoords, xCoords]
    return sampledImage

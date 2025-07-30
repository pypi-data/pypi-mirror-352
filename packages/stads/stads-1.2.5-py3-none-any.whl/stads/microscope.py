import numpy as np
from .config import REFERENCE_VIDEO_SEQUENCE


def sample_image_from_video_sequence(yCoords, xCoords, imageShape, frameNumber):
    frame = REFERENCE_VIDEO_SEQUENCE[frameNumber]
    croppedFrame = frame[:imageShape[0], :imageShape[1]]

    if imageShape[0] > frame.shape[0] or imageShape[1] > frame.shape[1]:
        raise ValueError(
            f"imageShape {imageShape} exceeds frame dimensions {frame.shape}"
        )

    sampledImage = np.zeros(imageShape, dtype=frame.dtype)

    if np.any(yCoords >= imageShape[0]) or np.any(xCoords >= imageShape[1]):
        raise IndexError("Provided coordinates exceed imageShape bounds.")

    sampledImage[yCoords, xCoords] = croppedFrame[yCoords, xCoords]
    return sampledImage

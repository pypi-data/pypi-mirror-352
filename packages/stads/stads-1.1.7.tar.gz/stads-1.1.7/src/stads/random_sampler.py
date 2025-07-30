import numpy as np
from concurrent.futures import ProcessPoolExecutor

from .config import REFERENCE_VIDEO_SEQUENCE
from . import evaluation
from .image_processing import generate_random_pixel_locations, compute_sample_size
from .interpolator import ImageInterpolator
from .microscope import sample_image_from_video_sequence


class RandomSampler:
    def __init__(self, imageShape, interpolMethod, sparsityPercent, numberOfFrames = 1):

        self.imageShape = imageShape
        self.sparsityPercent = sparsityPercent
        self.interpolMethod = interpolMethod
        self.numberOfFrames = numberOfFrames

        self.validate_inputs()

        self.numberOfSamples = compute_sample_size(imageShape, sparsityPercent)

        self.reconstructedFrames = []
        self.psnrs = []
        self.ssims = []

    def validate_inputs(self):
        if not isinstance(self.imageShape, (tuple, list)) or len(self.imageShape) != 2:
            raise ValueError("Image shape must be a tuple or list of two integers.")
        if not all(isinstance(x, int) and x > 0 for x in self.imageShape):
            raise ValueError("Image dimensions must be positive integers.")

        if not isinstance(self.sparsityPercent, (int, float)):
            raise ValueError("Sparsity percent must be a number.")
        if not (0 <= self.sparsityPercent <= 100):
            raise ValueError("Sparsity percent must be between 0 and 100.")

        # interpolMethod validation
        valid_methods = {"linear", "nearest", "cubic"}
        if not isinstance(self.interpolMethod, str) or self.interpolMethod not in valid_methods:
            raise ValueError(f"Interpolation method must be one of {valid_methods}.")

    def get_coordinates(self):
        return generate_random_pixel_locations(self.imageShape, self.sparsityPercent)


    def process_frame(self, frameNumber):
        yCoords, xCoords = self.get_coordinates()
        sampledImage = sample_image_from_video_sequence(yCoords, xCoords, self.imageShape, frameNumber)
        pixelIntensities = sampledImage[yCoords, xCoords]

        knownPoints = np.column_stack((yCoords, xCoords))
        imageInterpolator = ImageInterpolator(self.imageShape, knownPoints, pixelIntensities, self.interpolMethod)
        reconstructedImage = imageInterpolator.interpolate_image()
        reconstructedImage = np.clip(reconstructedImage, 0, 255).astype(np.uint8)

        psnr = evaluation.calculate_psnr(REFERENCE_VIDEO_SEQUENCE[frameNumber], reconstructedImage)
        ssim = evaluation.calculate_ssim(reconstructedImage, REFERENCE_VIDEO_SEQUENCE[frameNumber])

        return reconstructedImage, psnr, ssim


    def run(self):
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(self.process_frame, range(self.numberOfFrames)))

        self.reconstructedFrames, self.psnrs, self.ssims = zip(*results)
        return np.array(self.reconstructedFrames), list(self.psnrs), list(self.ssims)
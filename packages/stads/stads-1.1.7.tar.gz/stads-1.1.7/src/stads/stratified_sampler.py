from concurrent.futures import ProcessPoolExecutor

import numpy as np

from multiprocessing import Pool, cpu_count

from . import evaluation
from .config import REFERENCE_VIDEO_SEQUENCE
from .image_processing import rasterize_coordinates
from .interpolator import ImageInterpolator
from .microscope import sample_image_from_video_sequence
from .stratified_sampler_helpers import sample_child, direct_child_buckets, is_leaf, random_rejection_sampling, \
    deterministic_sample_counts, non_deterministic_sample_counts
from .utility_functions import compute_sample_size, calculate_area_fractions_of_buckets


class StratifiedSampler:
    def __init__(self, imageShape, interpolMethod, sparsityPercent, numberOfFrames = 1):

        self.imageShape = imageShape
        self.sparsityPercent = sparsityPercent
        self.interpolMethod = interpolMethod
        self.numberOfFrames = numberOfFrames

        self.validate_inputs()

        self.parentBucket = np.array([[0, 0], [imageShape[0] - 1, imageShape[1] - 1]])
        self.numberOfSamples = compute_sample_size(imageShape, sparsityPercent)

        self.ssims = []
        self.psnrs = []
        self.reconstructedFrames = []


    def validate_inputs(self):
        if not isinstance(self.imageShape, (tuple, list)) or len(self.imageShape) != 2:
            raise ValueError("Image shape must be a tuple or list of two integers.")
        if not all(isinstance(x, int) and x > 0 for x in self.imageShape):
            raise ValueError("Image dimensions must be positive integers.")
        if not (0 <= self.sparsityPercent <= 100):
            raise ValueError("Sparsity percent must be between 0 and 100.")
        if not isinstance(self.sparsityPercent, (int, float)):
            raise ValueError("Sparsity percent must be a number.")
        if not (0 <= self.sparsityPercent <= 100):
            raise ValueError("Sparsity percent must be between 0 and 100.")

    def get_coordinates(self):
        if self.numberOfSamples == 0:
            return np.array([], dtype=np.uint8), np.array([], dtype=np.uint8)

        stratifiedPixels = self.stratified_sampling(self.parentBucket, self.numberOfSamples)
        yCoords, xCoords = np.array(stratifiedPixels).T
        return rasterize_coordinates(self.imageShape, yCoords, xCoords)

    def stratified_sampling(self, bucket, numberOfSamples):

        children = direct_child_buckets(bucket)
        if is_leaf(children):
            return random_rejection_sampling(bucket, numberOfSamples)

        areaFractions = calculate_area_fractions_of_buckets(children, bucket)
        deterministic = deterministic_sample_counts(areaFractions, numberOfSamples)
        remainder = numberOfSamples - np.sum(deterministic)
        nondeterministic = non_deterministic_sample_counts(areaFractions, remainder)
        total = np.add(deterministic, nondeterministic)

        samplingArguments = [(child, samples, self.imageShape)
                for child, samples in zip(children, total) if samples > 0]

        if len(samplingArguments) > 0:
            with Pool(min(cpu_count(), len(samplingArguments))) as pool:
                results = pool.map(sample_child, samplingArguments)
                return np.vstack(results)

    def process_frame(self, frameNumber):
        yCoords, xCoords = self.get_coordinates()
        sampledImage = sample_image_from_video_sequence(yCoords, xCoords, self.imageShape, frameNumber)
        pixelIntensities = sampledImage[yCoords, xCoords]

        knownPoints = np.column_stack((yCoords, xCoords))
        interpolator = ImageInterpolator(self.imageShape, knownPoints, pixelIntensities, self.interpolMethod)
        reconstructedImage = interpolator.interpolate_image()
        reconstructedImage = np.clip(reconstructedImage, 0, 255).astype(np.uint8)

        psnr = evaluation.calculate_psnr(REFERENCE_VIDEO_SEQUENCE[frameNumber], reconstructedImage)
        ssim = evaluation.calculate_ssim(reconstructedImage, REFERENCE_VIDEO_SEQUENCE[frameNumber])

        return reconstructedImage, psnr, ssim


    def run(self):
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(self.process_frame, range(self.numberOfFrames)))

        self.reconstructedFrames, self.psnrs, self.ssims = zip(*results)
        return np.array(self.reconstructedFrames), list(self.psnrs), list(self.ssims)


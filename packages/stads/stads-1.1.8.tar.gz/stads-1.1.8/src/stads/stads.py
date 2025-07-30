import numpy as np
import logging

from .config import REFERENCE_VIDEO_SEQUENCE
from . import evaluation

from .image_processing import generate_scan_pattern_from_pdf
from .interpolator import ImageInterpolator
from .stads_helpers import compute_local_moments_of_image, compute_pdf_from_gradients_image, \
    compute_local_temporal_variance, compute_optical_flow
from .microscope import sample_image_from_video_sequence
from .random_sampler import RandomSampler
from .stratified_sampler import StratifiedSampler

logging.basicConfig(level=logging.INFO)

class AdaptiveSampler:
    def __init__(self, imageShape, initialSampling, interpolMethod, sparsityPercent, numberOfFrames,
                 withTemporal=True, learn_parameters=False):

        self.windowSize = 32
        self.imageShape = imageShape
        self.initialSampling = initialSampling
        self.interpolMethod = interpolMethod
        self.sparsityPercent = sparsityPercent
        self.numberOfFrames = numberOfFrames
        self.withTemporal = withTemporal
        self.learn_parameters = learn_parameters

        self.reconstructedFrames = []
        self.gradientsMaps = []
        self.yCoords, self.xCoords = self.initialize_sampling()

        self.flowMap = np.zeros(imageShape)
        self.temporalVarianceMap = np.ones(imageShape)
        self.spatialVarianceMap = np.ones(imageShape)

        self.psnrs = []
        self.ssims = []

    def initialize_sampling(self):
        if self.initialSampling == 'uniform':
            randomSampler = RandomSampler(self.imageShape, self.interpolMethod, self.sparsityPercent)
            return randomSampler.get_coordinates()
        elif self.initialSampling == 'stratified':
            stratifiedSampler = StratifiedSampler(self.imageShape, self.interpolMethod, self.sparsityPercent)
            return stratifiedSampler.get_coordinates()
        else:
            raise ValueError("Invalid initial sampling method. Choose 'uniform' or 'stratified'.")

    def get_samples(self, frameNumber=0):
        sampledImage = sample_image_from_video_sequence(self.yCoords, self.xCoords, self.imageShape, frameNumber)
        pixelIntensities = sampledImage[self.yCoords, self.xCoords]
        return pixelIntensities

    def interpolate_sparse_image(self, pixelIntensities):
        knownPoints = np.column_stack((self.yCoords, self.xCoords))
        imageInterpolator = ImageInterpolator(self.imageShape, knownPoints, pixelIntensities, self.interpolMethod)
        reconstructedImage = imageInterpolator.interpolate_image()
        reconstructedImage = np.clip(reconstructedImage, 0, 255).astype(np.uint8)
        return reconstructedImage

    def update_reconstructed_frames(self, reconstructedImage):
        self.reconstructedFrames.append(reconstructedImage)

    def update_gradients_maps(self, gradientsMap):
        self.gradientsMaps.append(gradientsMap)

    def compute_pmf_based_on_spatiotemporal_stats(self, samplingMap):
        samplingVarianceMap = compute_pdf_from_gradients_image(samplingMap)
        flowDensityMap = compute_pdf_from_gradients_image(self.flowMap)
        return compute_pdf_from_gradients_image(0.5 * (samplingVarianceMap + flowDensityMap))

    def update_scan_pattern(self, pdf):
        self.yCoords, self.xCoords = generate_scan_pattern_from_pdf(pdf, self.sparsityPercent)

    def update_flow_map(self, frameNumber=1):
        self.flowMap = compute_optical_flow(self.gradientsMaps[frameNumber - 1], self.gradientsMaps[frameNumber],
                                            self.windowSize)

    def update_temporal_variance_map(self, frameNumber=0):
        self.temporalVarianceMap = compute_local_temporal_variance(
            self.reconstructedFrames[frameNumber - 1], self.reconstructedFrames[frameNumber], self.windowSize)

    def compute_spatiotemporal_variance_map(self, spatialVarianceMap):
        return spatialVarianceMap + self.temporalVarianceMap

    def generate_scan_pattern_for_next_frame(self, frameNumber):
        pixelIntensities = self.get_samples(frameNumber)
        reconstructedImage = self.interpolate_sparse_image(pixelIntensities)
        self.update_reconstructed_frames(reconstructedImage)

        if frameNumber < self.numberOfFrames - 1:
            meanMap, gradientMap, spatiotemporalVariance = compute_local_moments_of_image(reconstructedImage, self.windowSize)
            self.update_gradients_maps(gradientMap)
            self.spatialVarianceMap = spatiotemporalVariance
            spatiotemporalVariance = self.compute_spatiotemporal_variance_map(self.spatialVarianceMap)

            if self.withTemporal and frameNumber > 0:
                self.update_flow_map(frameNumber)
                self.update_temporal_variance_map(frameNumber)


            pdf = self.compute_pmf_based_on_spatiotemporal_stats(spatiotemporalVariance)
            self.update_scan_pattern(pdf)

    def run(self):
        for frameNumber in range(self.numberOfFrames):
            self.generate_scan_pattern_for_next_frame(frameNumber)

            psnr = evaluation.calculate_psnr(REFERENCE_VIDEO_SEQUENCE[frameNumber], self.reconstructedFrames[frameNumber])
            ssim = evaluation.calculate_ssim(self.reconstructedFrames[frameNumber], REFERENCE_VIDEO_SEQUENCE[frameNumber])
            self.psnrs.append(psnr)
            self.ssims.append(ssim)

        return np.array(self.reconstructedFrames), self.psnrs, self.ssims

import os
from multiprocessing import cpu_count
from .config import REFERENCE_VIDEO_SEQUENCE
from .evaluation import calculate_psnr, calculate_ssim


def evaluate_frame(ground_truth, reconstructed):
    psnr = calculate_psnr(ground_truth, reconstructed)
    ssim = calculate_ssim(reconstructed, ground_truth)
    return psnr, ssim


def get_max_parallel_processes():
    try:
        n_cpu = cpu_count()
    except NotImplementedError:
        n_cpu = 1
    # Optionally, add memory checks here
    return max(1, n_cpu)


class ExperimentsSetup:
    """
    Base class to configure experiment parameters and validate inputs.

    Attributes:
        numberOfFrames (int): Number of video frames to process.
        imageShape (tuple): Shape (height, width) of the images.
        initialSampling (str): Sampling method ('stratified' or 'uniform').
        interpolMethod (str): Interpolation method ('linear', 'nearest', or 'cubic').
        plots_dir (str): Directory to save generated plots.
    """

    SUPPORTED_SAMPLING_METHODS = ['stratified', 'uniform']
    SUPPORTED_INTERPOL_METHODS = ['linear', 'nearest', 'cubic']

    def __init__(self, numberOfFrames, imageShape=None,
                 initialSampling='stratified', interpolMethod='linear'):
        self.numberOfFrames = numberOfFrames
        self.imageShape = imageShape or REFERENCE_VIDEO_SEQUENCE[0].shape
        self.initialSampling = initialSampling
        self.interpolMethod = interpolMethod

        self.plots_dir = 'plots'
        os.makedirs(self.plots_dir, exist_ok=True)

    def validate_inputs(self):
        """
        Validate inputs to ensure parameters are consistent and correct.

        Raises:
            ValueError: If any input is invalid.
        """
        if not isinstance(self.numberOfFrames, int) or self.numberOfFrames <= 0:
            raise ValueError("numberOfFrames must be a positive integer.")

        max_frames = len(REFERENCE_VIDEO_SEQUENCE)
        if self.numberOfFrames > max_frames:
            raise ValueError(f"numberOfFrames cannot exceed the number of frames in "
                             f"REFERENCE_VIDEO_SEQUENCE ({max_frames}).")

        if not isinstance(self.imageShape, (tuple, list)) or len(self.imageShape) != 2:
            raise ValueError("imageShape must be a tuple or list of two positive integers.")

        if not all(isinstance(x, int) and x > 0 for x in self.imageShape):
            raise ValueError("imageShape must contain two positive integers.")

        if self.initialSampling not in self.SUPPORTED_SAMPLING_METHODS:
            raise ValueError(f"initialSampling must be one of {self.SUPPORTED_SAMPLING_METHODS}.")

        if self.interpolMethod not in self.SUPPORTED_INTERPOL_METHODS:
            raise ValueError(f"interpolMethod must be one of {self.SUPPORTED_INTERPOL_METHODS}.")


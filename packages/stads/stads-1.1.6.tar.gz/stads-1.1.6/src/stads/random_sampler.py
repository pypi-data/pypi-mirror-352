from .image_processing import generate_random_pixel_locations
from .utility_functions import compute_sample_size


class RandomSampler:
    def __init__(self, imageShape, sparsityPercent):
        self.imageShape = imageShape
        self.sparsityPercent = sparsityPercent
        self.numberOfSamples = compute_sample_size(imageShape, sparsityPercent)
        self.validate_inputs()

    def validate_inputs(self):
        if not isinstance(self.imageShape, (tuple, list)) or len(self.imageShape) != 2:
            raise ValueError("Image shape must be a tuple or list of two integers.")
        if not all(isinstance(x, int) and x > 0 for x in self.imageShape):
            raise ValueError("Image dimensions must be positive integers.")
        if not (0 <= self.sparsityPercent <= 100):
            raise ValueError("Sparsity percent must be between 0 and 100.")


    def get_coordinates(self):
        return generate_random_pixel_locations(self.imageShape, self.sparsityPercent)



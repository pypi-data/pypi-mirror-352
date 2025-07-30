import numpy as np
from scipy.interpolate import griddata, LinearNDInterpolator


class ImageInterpolator:
    def __init__(self, imageShape, knownPoints, pixelIntensities, interpolMethod):
        self.imageShape = imageShape
        self.knownPoints = knownPoints
        self.pixelIntensities = pixelIntensities
        self.interpolMethod = interpolMethod
        self.validate_inputs()

    def validate_inputs(self):

        if not isinstance(self.imageShape, tuple) or len(self.imageShape) != 2:
            raise ValueError("imageShape must be a tuple of two integers (height, width)")
        if self.interpolMethod not in ['linear', 'cubic', 'nearest']:
            raise ValueError(f"Unknown interpolation method: {self.interpolMethod}")
        if len(self.knownPoints) != len(self.pixelIntensities):
            raise ValueError("Number of knownPoints must match number of pixelIntensities")
        if self.knownPoints.ndim != 2 or self.knownPoints.shape[1] != 2:
            raise ValueError("knownPoints must be a 2D array with shape (N, 2) for [y, x] coordinates")
        if not np.all(np.isfinite(self.knownPoints)):
            raise ValueError("knownPoints contains NaN or infinite values")
        if not np.all(np.isfinite(self.pixelIntensities)):
            raise ValueError("pixelIntensities contains NaN or infinite values")

        height, width = self.imageShape

        if (np.any(self.knownPoints[:, 0] < 0) or np.any(self.knownPoints[:, 0] >= height) or
            np.any(self.knownPoints[:, 1] < 0) or np.any(self.knownPoints[:, 1] >= width)):
            raise ValueError("Some knownPoints are outside the image bounds")

    def interpolate_image(self):
        gridX, gridY = np.mgrid[0:self.imageShape[1], 0:self.imageShape[0]]
        if self.interpolMethod in ['cubic', 'nearest']:
            interpolatedImage = griddata(self.knownPoints, self.pixelIntensities, (gridX, gridY), method=self.interpolMethod)
        elif self.interpolMethod == 'linear':
            interpolator = LinearNDInterpolator(self.knownPoints, self.pixelIntensities)
            interpolatedImage = interpolator(gridX, gridY)
        else:
            raise RuntimeError("Interpolation method validation failed to catch an invalid method")

        return np.nan_to_num(interpolatedImage, nan=0.0)

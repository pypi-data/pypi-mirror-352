import unittest
import numpy as np
import numpy.testing as npt

from src.stads.stratified_sampler import StratifiedSampler


class TestStratifiedSampler(unittest.TestCase):

    def test_basic_sampling_shape_serial(self):
        sampler = StratifiedSampler((20, 20), 45)
        sampledPoints = sampler.get_coordinates()
        self.assertEqual(len(sampledPoints[0]), 180)

    def test_basic_sampling_shape_parallel(self):
        sampler = StratifiedSampler((20, 20), 45)
        sampledPoints = sampler.get_coordinates()
        self.assertEqual(len(sampledPoints[0]), 180)

    def test_zero_samples(self):
        sampler = StratifiedSampler((100, 100), 0)
        sampledPoints = sampler.get_coordinates()
        npt.assert_array_equal(sampledPoints, np.empty((2, 0), dtype=np.uint8))

    def test_maximum_samples_equal_to_pixels(self):
        height, width = 16, 16
        sampler = StratifiedSampler((height, width), 100)
        sampledPoints = sampler.get_coordinates()
        self.assertEqual(len(sampledPoints[0]), height * width)

    def test_invalid_negative_sample_count(self):
        with self.assertRaises(ValueError):
            StratifiedSampler((128, 128), -5)

    def test_invalid_zero_shape(self):
        with self.assertRaises(ValueError):
            StratifiedSampler((0, 128), 10)
        with self.assertRaises(ValueError):
            StratifiedSampler((128, 0), 10)

    def test_invalid_over_sample(self):
        with self.assertRaises(ValueError):
            StratifiedSampler((10, 10), 101)

    def test_consistency_of_shape_parameter(self):
        for shape in [(1, 1), (5, 10), (40, 15), (1024, 1024)]:
            sampler = StratifiedSampler(shape, 10)
            sampledPoints = sampler.get_coordinates()
            for y, x in zip(sampledPoints[0], sampledPoints[1]):
                self.assertTrue(0 <= y < shape[0])
                self.assertTrue(0 <= x < shape[1])

    def test_sample_return_type(self):
        sampler = StratifiedSampler((100, 100), 5)
        sampledPoints = sampler.get_coordinates()
        self.assertIsInstance(sampledPoints, tuple)
        self.assertEqual(len(sampledPoints), 2)
        self.assertTrue(all(isinstance(arr, np.ndarray) for arr in sampledPoints))
        self.assertEqual(len(sampledPoints[0]), len(sampledPoints[1]))

    def test_duplicate_sampled_points_not_allowed(self):
        sampler = StratifiedSampler((10, 10), 50)
        yCoords, xCoords = sampler.get_coordinates()
        coords = list(zip(yCoords, xCoords))
        self.assertEqual(len(coords), len(set(coords)))
if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import os
from stads.experiments import SamplingExperiments


class TestLaboratoryInstrument(unittest.TestCase):
    def setUp(self):
        self.instrument = SamplingExperiments(
            image_shape=(100, 100),
            number_of_frames=3,
            interpolation_method='linear',
            initial_sampling='stratified',
            output_dir='test_output'
        )

    def test_validate_inputs_bad_image_shape(self):
        self.instrument.image_shape = (100, -1)
        with self.assertRaises(TypeError):
            self.instrument.validate_inputs()

    def test_validate_inputs_bad_number_of_frames(self):
        self.instrument.number_of_frames = 0
        with self.assertRaises(TypeError):
            self.instrument.validate_inputs()

    @patch.object(SamplingExperiments, '_run_adaptive_sampler', return_value=([30], [0.9]))
    @patch.object(SamplingExperiments, '_run_random_sampler', return_value=([25], [0.85]))
    @patch.object(SamplingExperiments, '_run_stratified_sampler', return_value=([20], [0.8]))
    def test_run_experiment1_aggregates_results(self, mock_strat, mock_rand, mock_adapt):
        self.instrument.number_of_frames = 1
        self.instrument.validate_inputs = MagicMock()
        self.instrument.save_comparison_plots = MagicMock()

        self.instrument.run_experiment1()

        self.instrument.save_comparison_plots.assert_called_once()
        args = self.instrument.save_comparison_plots.call_args[0]
        sparsities, psnr_means, psnr_stds, ssim_means, ssim_stds = args
        self.assertIn('AdaptiveSampler', psnr_means)
        self.assertAlmostEqual(psnr_means['AdaptiveSampler'][0], 30)
        self.assertAlmostEqual(ssim_means['AdaptiveSampler'][0], 0.9)


if __name__ == '__main__':
    unittest.main()

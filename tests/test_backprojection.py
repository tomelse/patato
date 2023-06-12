#  Copyright (c) Thomas Else 2023.
#  License: MIT

import unittest

import numpy as np

from patato.data import get_msot_time_series_example
from patato.processing.jax_preprocessing_algorithm import PreProcessor
from patato.recon import OpenCLBackprojection, ReferenceBackprojection, SlowBackprojection


class BackprojectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pa = get_msot_time_series_example("so2")[0:2, 0:2]

        self.preproc = PreProcessor(time_factor=1, detector_factor=2)
        self.filtered_time_series, self.new_settings, _ = self.preproc.run(self.pa.get_time_series(), self.pa)

    def _test_backprojector(self, reconstructor_class):
        reconstructor = reconstructor_class([333, 334, 1], [0.025, 0.025, 1.])
        r, _, _ = reconstructor.run(self.filtered_time_series, self.pa, **self.new_settings)
        self.assertEqual(r.shape, (2, 2, 1, 334, 333))
        self.assertAlmostEqual(np.mean(r[0, 0].values), 316.15831026634015, 2)

        reconstructor = reconstructor_class([1, 333, 334], [1., 0.025, 0.025])
        r, _, _ = reconstructor.run(self.filtered_time_series, self.pa, **self.new_settings)
        self.assertEqual(r.shape, (2, 2, 334, 333, 1))

        reconstructor = reconstructor_class([334, 1, 333], [0.025, 1., 0.025])
        r, _, _ = reconstructor.run(self.filtered_time_series, self.pa, **self.new_settings)
        self.assertEqual(r.shape, (2, 2, 333, 1, 334))

    def test_reference_reconstruction(self):
        self._test_backprojector(ReferenceBackprojection)

    def test_slow_backprojection(self):
        self._test_backprojector(SlowBackprojection)

    def test_opencl_reconstruction(self):
        try:
            import pyopencl
        except ImportError:
            return  # Skip test if pyopencl is not installed

        self._test_backprojector(OpenCLBackprojection)

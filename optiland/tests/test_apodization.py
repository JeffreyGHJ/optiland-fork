import math
import unittest

from optiland.optic.optic import Optic
from optiland.apodization import UniformApodization, GaussianApodization
from optiland.rays.ray_generator import RayGenerator

# Create some dummy replacements for required attributes/methods on Optic
class DummyAperture:
    def __init__(self, ap_type="default", value=1.0):
        self.ap_type = ap_type
        self.value = value

class DummyFieldGroup:
    def get_vig_factor(self, Hx, Hy):
        # Return zero vignetting
        return (0, 0)
    max_field = 1

class DummySurfaceGroup:
    positions = [0, 1, 2]
    uses_polarization = False

class DummyParaxial:
    def EPL(self):
        return 1
    def EPD(self):
        return 1

class TestApodization(unittest.TestCase):
    def setUp(self):
        # Create an Optic with dummy attributes necessary for ray generation.
        self.optic = Optic("test optic")
        self.optic.aperture = DummyAperture()
        self.optic.fields = DummyFieldGroup()
        self.optic.surface_group = DummySurfaceGroup()
        self.optic.paraxial = DummyParaxial()
        self.optic.obj_space_telecentric = False
        self.ray_gen = RayGenerator(self.optic)

    def test_no_apodization(self):
        self.optic.apodization = None
        rays = self.ray_gen.generate_rays(0, 0, 0, 0, 0.5)
        # Expect intensity to be unchanged (ones)
        if hasattr(rays.intensity, '__iter__'):
            for intensity in rays.intensity:
                self.assertEqual(intensity, 1)
        else:
            self.assertEqual(rays.intensity, 1)

    def test_uniform_apodization(self):
        self.optic.apodization = UniformApodization()
        rays = self.ray_gen.generate_rays(0, 0, 0, 0, 0.5)
        # Uniform apodization returns a factor of 1, so intensities remain ones.
        if hasattr(rays.intensity, '__iter__'):
            for intensity in rays.intensity:
                self.assertEqual(intensity, 1)
        else:
            self.assertEqual(rays.intensity, 1)

    def test_gaussian_apodization(self):
        # Set up Gaussian apodization with sigma=0.5
        self.optic.apodization = GaussianApodization(sigma=0.5)
        # Test at pupil center (0, 0): expect exp(0) == 1.
        rays_center = self.ray_gen.generate_rays(0, 0, 0.0, 0.0, 0.5)
        if hasattr(rays_center.intensity, '__iter__'):
            for intensity in rays_center.intensity:
                self.assertAlmostEqual(intensity, 1.0)
        else:
            self.assertAlmostEqual(rays_center.intensity, 1.0)
        # Test at a nonzero pupil coordinate, e.g., (0.5, 0.5)
        rays_offcenter = self.ray_gen.generate_rays(0, 0, 0.5, 0.5, 0.5)
        # Expected scaling: r = sqrt(0.5^2+0.5^2) ~ 0.7071, divided by sigma = 0.5 gives ~1.4142, square = 2
        # scaling = exp(-2) ~ 0.1353
        expected = math.exp(-2)
        if hasattr(rays_offcenter.intensity, '__iter__'):
            for intensity in rays_offcenter.intensity:
                self.assertAlmostEqual(intensity, expected, places=4)
        else:
            self.assertAlmostEqual(rays_offcenter.intensity, expected, places=4)

if __name__ == '__main__':
    unittest.main()
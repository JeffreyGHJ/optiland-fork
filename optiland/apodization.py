from math import exp, sqrt

class Apodization:
    """Base class for apodization patterns applied to ray intensities.
    
    Subclasses should implement the apply method which returns a scaling
    factor based on the pupil coordinates.
    """
    def apply(self, Px, Py):
        """Apply the apodization to the given pupil coordinates.
        
        Args:
            Px: x-coordinate(s) of the pupil point(s).
            Py: y-coordinate(s) of the pupil point(s).
            
        Returns:
            The scaling factor(s) for the intensity.
        """
        raise NotImplementedError("Subclasses must implement the apply method.")

class UniformApodization(Apodization):
    """Uniform apodization leaves the ray intensity unchanged."""
    def apply(self, Px, Py):
        # If Px is iterable, return a list of ones; otherwise, return 1.
        try:
            iter(Px)
            return [1 for _ in Px]
        except TypeError:
            return 1

class GaussianApodization(Apodization):
    """Gaussian apodization scales the ray intensity with a Gaussian profile.
    
    The scaling factor is computed as:
        scaling = exp( - (r / sigma)^2 )
    where r is the radial distance in the pupil.
    """
    def __init__(self, sigma=1.0):
        self.sigma = sigma

    def apply(self, Px, Py):
        # Compute the radial distance and apply the Gaussian function.
        try:
            # If Px is iterable (e.g. list or numpy array), process element-wise.
            iter(Px)
            result = []
            for x, y in zip(Px, Py):
                r = sqrt(x*x + y*y)
                result.append(exp(- (r/self.sigma)**2))
            return result
        except TypeError:
            # Assume numeric values
            r = sqrt(Px*Px + Py*Py)
            return exp(- (r/self.sigma)**2)
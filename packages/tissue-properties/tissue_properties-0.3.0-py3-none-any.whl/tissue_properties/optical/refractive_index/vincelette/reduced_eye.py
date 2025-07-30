import numpy

from ....units import Q_
from .reference import VinceletteModel


class ReducedEye(VinceletteModel):
    def __init__(self):
        self.B1 = Q_(7.516e-1, "")
        self.B2 = Q_(-4.484e-3, "")
        self.B3 = Q_(-1.503e1, "")
        self.C1 = Q_(1.641e-2, "um**2")
        self.C2 = Q_(8.596e-2, "um**2")
        self.C3 = Q_(-1.028e3, "um**2")

    def __call__(self, wavelength: str | Q_):

        wavelength = Q_(wavelength).to("um")
        wavelength2 = wavelength * wavelength

        val = (
            1
            + self.B1 * wavelength2 / (wavelength2 - self.C1)
            + self.B2 * wavelength2 / (wavelength2 - self.C2)
            + self.B3 * wavelength2 / (wavelength2 - self.C3)
        ).to("") ** 0.5

        return val

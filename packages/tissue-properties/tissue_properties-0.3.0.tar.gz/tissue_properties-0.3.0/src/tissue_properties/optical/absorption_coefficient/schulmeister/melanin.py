import numpy

from ....units import Q_
from .reference import SchulmeisterModel


class Melanin(SchulmeisterModel):
    def __init__(self):
        self.argument_units = "nm"
        self.value_units = "1/cm"
        pass

    def __call__(self, wavelength: str | Q_):
        wavelength = Q_(wavelength)
        wavelength.ito("nm")
        wavelength = wavelength.magnitude
        val = 3.85e14 * wavelength ** (-4.2)

        return Q_(val, "1/cm")

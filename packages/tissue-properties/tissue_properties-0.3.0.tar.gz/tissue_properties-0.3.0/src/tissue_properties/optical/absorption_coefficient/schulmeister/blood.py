import numpy

from ....units import Q_
from .reference import SchulmeisterModel


class Blood(SchulmeisterModel):
    def __init__(self):
        self.argument_units = "nm"
        self.value_units = "1/cm"
        pass

    def __call__(self, wavelength: str | Q_):
        wavelength = Q_(wavelength)
        wavelength.ito("nm")
        wavelength = wavelength.magnitude
        val = 1.404e7 * numpy.exp(-0.024 * wavelength)
        val += 2160 * numpy.exp(-0.0055 * (417 - wavelength) ** 2)
        val += 244 * numpy.exp(-0.0022 * (543 - wavelength) ** 2)
        val += 253 * numpy.exp(-0.0065 * (577 - wavelength) ** 2)
        val += 7 * numpy.exp(-0.00004 * (920 - wavelength) ** 2)

        return Q_(val, "1/cm")

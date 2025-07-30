import numpy

from ....units import Q_
from .blood import Blood
from .melanin import Melanin
from .reference import SchulmeisterModel


class Choroid(SchulmeisterModel):
    def __init__(self):
        super().__init__()
        self.blood = Blood()
        self.melanin = Melanin()

    def __call__(self, wavelength: str | Q_):
        wavelength = Q_(wavelength)
        wavelength.ito("nm")
        val = 0.114 * self.melanin(wavelength) + 0.3 * self.blood(wavelength)

        return Q_(val, "1/cm")

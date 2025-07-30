import numpy

from ....units import Q_
from ..cie203.total_transmission import TotalTransmission
from .reference import SchulmeisterModel


class EffectiveTransmission(SchulmeisterModel):
    def __init__(self):
        self.total_transmission = TotalTransmission()

    def g(self, wavelength: str | Q_):
        wavelength = Q_(wavelength)
        wavelength.ito("nm")
        A = 0.5
        B = Q_(883, "nm")
        return A * numpy.exp(-wavelength / B)

    def h(self, spot_size: str | Q_):
        spot_size = Q_(spot_size)
        spot_size.ito("um")
        C = Q_(600, "um")
        return numpy.exp(-spot_size / C)

    def __call__(self, wavelength: str | Q_, spot_size: str | Q_):
        """
        Note: spot size is 1/e retinal spot size
        """
        return self.total_transmission(wavelength) * (
            1 - self.g(wavelength) * self.h(spot_size)
        )

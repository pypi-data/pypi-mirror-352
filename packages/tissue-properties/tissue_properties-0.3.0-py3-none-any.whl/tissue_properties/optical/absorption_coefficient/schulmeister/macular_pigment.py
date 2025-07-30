from .reference import SchulmeisterModel
from ....units import Q_
import numpy


class MacularPigment(SchulmeisterModel):
    def __init__(self):
        self.argument_units = "nm"
        self.value_units = "1/cm"
        pass
    

    def __call__(self,wavelength: str|Q_):
        wavelength = Q_(wavelength)
        wavelength.ito("nm")
        wavelength = wavelength.magnitude
        val = 0
        val += 0.32*numpy.exp(-0.0012*(436-wavelength)**2)
        val += 0.32*numpy.exp(-0.0012*(480-wavelength)**2)
        val -= 0.123*numpy.exp(-0.0012*(458-wavelength)**2)
        val += 0.12042*numpy.exp(-0.006*(457-wavelength)**2)
        val *= 143/0.35

        return Q_(val,'1/cm')


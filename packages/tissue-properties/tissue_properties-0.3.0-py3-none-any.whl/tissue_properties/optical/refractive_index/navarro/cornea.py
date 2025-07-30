import numpy

from ....units import Q_
from .reference import NavarroModel
from .utils import n


class Cornea(NavarroModel):
    def __init__(self):
        pass

    def __call__(self, wavelength: str | Q_):
        n_double_star = Q_(1.3975,'')
        n_F = Q_(1.3807,'')
        n_c = Q_(1.37405,'')
        n_star = Q_(1.3668,'')

        wavelength = Q_(wavelength)

        val = n(n_double_star,n_F,n_c,n_star,wavelength)

        return val

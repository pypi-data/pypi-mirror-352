import numpy
from ....units import Q_
from .reference import NavarroModel
from .utils import n



class Aqueous(NavarroModel):
    def __init__(self):
        pass

    def __call__(self, wavelength: str | Q_):
        n_double_star = Q_(1.3593,'')
        n_F = Q_(1.3422,'')
        n_c = Q_(1.3354,'')
        n_star = Q_(1.3278,'')

        wavelength = Q_(wavelength)

        val = n(n_double_star,n_F,n_c,n_star,wavelength)

        return val

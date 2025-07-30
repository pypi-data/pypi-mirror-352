import pytest

from tissue_properties.base_classes import *
from tissue_properties.exceptions import UndefinedProperty
from tissue_properties.optical.absorption_coefficient import (mainster,
                                                              schulmeister)
from tissue_properties.units import *


def test_mainster_data():
    rpe = mainster.RPE()
    choroid = mainster.Choroid()

    assert rpe("429 nm").magnitude == pytest.approx(1.032218944384028646e03)
    assert choroid("429 nm").magnitude == pytest.approx(1.516453712129046778e02)

    assert rpe("0.429 um").magnitude == pytest.approx(1.032218944384028646e03)
    assert choroid("0.429 um").magnitude == pytest.approx(1.516453712129046778e02)


def test_schulmeister_equations():
    rpe = schulmeister.RPE()
    assert rpe("532 nm").magnitude == pytest.approx(1369.72)
    assert rpe("0.532 um").magnitude == pytest.approx(1369.72)

    henles_fiber_layer = schulmeister.HenlesFiberLayer()
    assert henles_fiber_layer("532 nm").magnitude == pytest.approx(5.02758)
    assert henles_fiber_layer("0.532 um").magnitude == pytest.approx(5.02758)

    choroid = schulmeister.Choroid()
    assert choroid("532 nm").magnitude == pytest.approx(
        0.3 * 235.806 + 0.114 * 1369.72, rel=0.02
    )
    assert choroid("0.532 um").magnitude == pytest.approx(
        0.3 * 235.806 + 0.114 * 1369.72, rel=0.02
    )


def test_function_call_does_not_modify_arg():
    rpe = mainster.RPE()
    wavelength = Q_("429 nm")

    assert rpe(wavelength).magnitude == pytest.approx(1.032218944384028646e03)
    assert wavelength.magnitude == pytest.approx(429)

    wavelength = Q_("0.429 um")

    assert rpe(wavelength).magnitude == pytest.approx(1.032218944384028646e03)
    assert wavelength.magnitude == pytest.approx(0.429)


def test_outof_range_errors():
    rpe = mainster.RPE()
    choroid = mainster.Choroid()

    with pytest.raises(UndefinedProperty):
        rpe("1400 nm")

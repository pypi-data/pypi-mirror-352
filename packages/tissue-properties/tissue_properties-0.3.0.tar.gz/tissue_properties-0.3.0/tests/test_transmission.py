import pytest

from tissue_properties.optical.ocular_transmission import (cie203, mainster,
                                                           schulmeister)
from tissue_properties.units import *


def test_cie_data():
    T_t = cie203.TotalTransmission()
    T_d = cie203.DirectTransmission()

    assert T_t(Q_(530, "nm")).magnitude == pytest.approx(0.7867)
    assert T_d(Q_(530, "nm")).magnitude == pytest.approx(0.543)
    assert T_t(Q_(0.530, "um")).magnitude == pytest.approx(0.7867)
    assert T_d(Q_(0.530, "um")).magnitude == pytest.approx(0.543)
    assert T_t(Q_(530, "nm")).to("percent").magnitude == pytest.approx(78.67)
    assert T_d(Q_(530, "nm")).to("percent").magnitude == pytest.approx(54.3)


def test_schulmeister_effective_transmission():
    T_eff = schulmeister.EffectiveTransmission()
    T_t = cie203.TotalTransmission()
    T_d = cie203.DirectTransmission()

    assert T_eff("530 nm", "10000 um") == pytest.approx(0.7867)
    assert T_eff("530 nm", "0 um") == pytest.approx(0.543, rel=0.055)


def test_mainster_transmission():
    T = mainster.Transmission()

    assert T("530 nm") == pytest.approx(5.421831732026283213e-01)
    assert T("0.530 um") == pytest.approx(5.421831732026283213e-01)

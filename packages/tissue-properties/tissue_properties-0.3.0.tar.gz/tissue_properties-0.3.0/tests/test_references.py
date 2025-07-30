from tissue_properties.base_classes import *
from tissue_properties.optical.absorption_coefficient.mainster import RPE


def test_getting_references():
    model = ReferencedDataModel()
    assert model.get_reference() is None

    model = RPE()
    assert model.get_reference() is not None
    assert model.get_reference().replace("\n", "").startswith("@Article")

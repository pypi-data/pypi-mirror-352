from ....base_classes import ReferencedDataModel


class SchulmeisterModel(ReferencedDataModel):
    reference = """
@Article{schulmeister-2017,
  author  = {Mathieu Jean and Karl Schulmeister},
  title   = {Validation of a computer model to predict laser induced retinal injury thresholds},
  journal = {Journal of Laser Applications},
  year    = {2017},
  url     = {https://lia.scitation.org/doi/10.2351/1.4997831},
}
"""

    def __init__(self):
        pass

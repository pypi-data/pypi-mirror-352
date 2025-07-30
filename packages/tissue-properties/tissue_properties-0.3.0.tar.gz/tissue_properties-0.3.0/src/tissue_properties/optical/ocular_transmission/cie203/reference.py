from ....base_classes import ReferencedDataModel


class CIEModel203(ReferencedDataModel):
    reference = """
@TechReport{lund-2012,
author      = {D. Lund and J. Marshall and J. Mellerio and T. Okuno and K. Schulmeister and D. Sliney and P. S\"{o}derberg and B. Stuck and D. {van Norren} and J. Zuclich},
title       = {A computerized approach to transmission and absorption characteristics of the human eye},
institution = {International Commission on Illumination},
year        = {2012},
url         = {http://cie.co.at/publications/computerized-approach-transmission-and-absorption-characteristics-human-eye},
}
"""

    def __init__(self):
        pass

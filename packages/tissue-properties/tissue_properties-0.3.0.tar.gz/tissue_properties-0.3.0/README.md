# A python library for calculating/looking up various tissue properties for laser bioeffect calculations

To simulate the exposure of tissue (skin or retina) to laser radiation, several properties characterizing the thermo-optical response of the tissue are needed.
These include absorption coefficients, transmission coefficients, conductivity, density, specific heat, etc. This library is a collection of tissue property data
sets that have been reported in the literature.

# Installing

Install with pip (or your favorite virtual environment manager)

```bash
pip install tissue-properties
```

# Usage

```
# Print out the absorption coefficients as a function of wavelength used in the 
# paper "Retinal-Temperature Increases Produced by Intense Light Sources" by
# Mainster in 1970. These values were extracted from Figure 3.
from tissue_properties.optical.absorption_coefficient import mainster
from tissue_properties.units import Q_

RPE = mainster.RPE()
choroid = minster.Choroid()

print("# wavelength retina choroid")
for wavelength in range(400,1405,5):
    l = Q_(wavelength,'nm')
    mu_r = RPE(l)
    mu_c = RPE(l)
    print(l,mu_r,mu_c)

# We can also get information about data set. Currently only the reference is
# provided, in BibTex format.
bibtex_text = RPE.get_reference()
print(bibtex_text)
```

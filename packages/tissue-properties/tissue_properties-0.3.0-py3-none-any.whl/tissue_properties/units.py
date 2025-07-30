import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

ureg.define("percent = 0.01*radian")

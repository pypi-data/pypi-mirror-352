import setuptools
from pathlib import Path

setuptools.setup(
    name="jakepdf-bloom",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
# pypi-AgEIcHlwaS5vcmcCJGE0NDZiM2Y1LTBiMzQtNGY1NS04ZDljLWY5M2VkNTRiN2Q0OQACKlszLCI2ZTBlNzFiMS1iODhkLTRmZjAtYTEwMy0wNDhkMDUzMjFkYzEiXQAABiAsoLvgFfchMKt21IgC1aQ1F4Z96fsRO1rfVAfERWDW_Q

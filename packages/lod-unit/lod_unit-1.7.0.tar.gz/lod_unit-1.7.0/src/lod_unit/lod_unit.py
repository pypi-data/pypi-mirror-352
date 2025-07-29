"""Defines a unit for λ/D, :py:data:`lod`, that can be imported and an equivalency, :py:func:`lod_eq`, to convert to angular units."""

import functools

from astropy.units import Quantity, IrreducibleUnit
from astropy.units.equivalencies import Equivalency
import astropy.units as u

lod: IrreducibleUnit = u.def_unit("λ/D", doc="A unit for λ/D")  # type: ignore
"""
An astropy IrreducibleUnit representing the ratio of wavelength to diameter (λ/D).
"""


@functools.cache
def lod_eq(lam: Quantity, D: Quantity) -> Equivalency:
    """Convert between λ/D and angular units.

    Function to allow conversion between λ/D and angular units natively
    with the astropy units package.

    Args:
        lam (Astropy Quantity):
            Wavelength
        D (Astropy Quantity):
            Diameter

    Returns:
        An astropy Equivalency object to allow conversion between λ/D and
        angular units.

    Usage:
        >>> diam = 10*u.m
        >>> lam = 500*u.nm
        >>> angseparation = 3 * lod
        >>> angseparation.to(u.arcsec, lod_eq(lam, diam))
            <Quantity 0.03093972 arcsec>
    """
    _lam = lam.to(u.m).value
    _D = D.to(u.m).value

    # Conversion functions
    def lod_to_rad(lod_val: float) -> float:
        return lod_val * (_lam / _D)

    def rad_to_lod(rad_val: float) -> float:
        return rad_val * (_D / _lam)

    base_equivalence = [(lod, u.rad, lod_to_rad, rad_to_lod)]

    return Equivalency(base_equivalence)

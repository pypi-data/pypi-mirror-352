__all__ = ["Comet"]

import numpy as np

try:
    import astropy.units as u
except ImportError:
    u = None

from .phase import phase_HalleyMarcus

# TODO: Change this to use the Astropy definition
AU_IN_CM = 14959787070000


class Comet:
    """LSST comet model.

    The goal of this model is to make a template comet based on ``H``
    magnitude, which is the main brightness parameter in the LSST
    Metrics Analysis Framework.  Using this value enables easy object
    cloning.


    Parameters
    ----------
    afrho1 or afrho_q: float
        Comet coma quantity Afρ at 1 au (``afrho1``) or at perihelion
        (``afrho_q``), in units of cm.  The latter requires ``q``.

    k : float
        Activity power-law slope with heliocentric distance: ``rh^k``.

    q : float, required if ``afrho_q`` is provided
        Perihelion distance for Afρ normalization.

    Phi_c : function, optional
        One-parameter function that takes phase angle in degrees and
        returns the phase function for comae.  It is assumed that
        Phi(0) = 1.0.  Default is to use the Halley-Marcus phase
        function of Schleicher & Bair 2011.
    """

    # Willmer 2018, ApJS 236, 47
    mv_sun = -26.76  # Vega mag
    m_sun = {"u": -25.30, "g": -26.52, "r": -26.93, "i": -27.05, "z": -27.07, "y": -27.07}  # AB mag

    def __init__(self, k=-2, afrho1=1500, **kwargs):
        self.k = k
        self.afrho1 = afrho1

        self.Phi_c = kwargs.get("Phi_c", phase_HalleyMarcus)

    def _get_value(self, d, keys, unit):
        v = None
        for k in keys[::-1]:
            try:
                # this works with sbpy Ephem objects
                v = d[k]
                break
            except KeyError:
                pass

        if v is None:
            raise IndexError
        if u:
            v = u.Quantity(v, unit).value
        return v

    def _normalize_geom(self, geom):
        # allows for sbpy Ephem objects, LSST MAF ssObs, and plain
        # dictionaries
        return {
            "rh": self._get_value(geom, ("rh", "helio_dist"), "au"),
            "delta": self._get_value(geom, ("delta", "geo_dist"), "au"),
            "phase": self._get_value(geom, ("phase", "alpha"), "deg"),
        }

    def afrho(self, geom):
        """Afρ quanitity given geometrical circumstances.

        Parameters
        ----------
        geom: dictionary-like
            'rh' or 'helio_dist', and 'phase' or 'alpha' angle in au
            and deg.

        Returns
        -------
        afrho: float
            Afρ parameter in cm.

        """
        g = self._normalize_geom(geom)
        afrho = self.afrho1 * g["rh"] ** self.k * self.Phi_c(g["phase"])
        return afrho

    def mag(self, geom, bandpass, rap=1):
        """Apparent magnitude within aperture.

        Parameters
        ----------
        geom : dictionary-like
            'rh' or 'helio_dist', 'delta' or 'geo_dist', and 'phase'
            angle in au and deg.

        bandpass : string
            LSST bandpass.  One of u, g, r, i, z, y.

        rap : float, optional
            Aperture radius in arcsec.
        """
        g = self._normalize_geom(geom)
        delta = AU_IN_CM * g["delta"]  # au to cm

        afrho = self.afrho(g)
        rho = 725e5 * g["delta"] * rap  # arcsec to projected cm
        dm = -2.5 * np.log10(afrho * rho / (2 * g["rh"] * delta) ** 2)

        if bandpass in self.m_sun:
            coma = self.m_sun[bandpass] + dm
        else:
            raise KeyError(
                f"Unexpected bandpass provided. Expected one of ['u','g','r','i','z','y'], but was provided: {bandpass}"
            )

        return coma

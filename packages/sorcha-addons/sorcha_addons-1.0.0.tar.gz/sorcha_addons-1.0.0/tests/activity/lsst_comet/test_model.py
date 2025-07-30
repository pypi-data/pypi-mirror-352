import pytest
import os
from pathlib import Path
import numpy as np
import astropy.units as u
from sbpy.activity import Afrho
import synphot
from sorcha_addons.activity.lsst_comet.model import Comet


class TestComet:
    def test_afrho(self):
        comet = Comet(afrho1=100, k=-2)
        g = {"rh": 2.0, "delta": 1.0, "phase": 0}
        assert np.isclose(comet.afrho(g), 100 * 2**-2)

    def test_mag(self):
        # compare to sbpy
        g = {"rh": 2.0 * u.au, "delta": 1.0 * u.au, "phase": 0 * u.deg}
        afrho = Afrho(100 * 2**-2, "cm")

        THIS_DIR = Path(__file__).parent
        file_path = os.path.join(THIS_DIR, "lsst-total-r.dat")
        tab = np.loadtxt(file_path).T
        r = synphot.SpectralElement(synphot.Empirical1D, points=tab[0] * u.nm, lookup_table=tab[1])
        rap = 1 * u.arcsec
        m0 = afrho.to_fluxd(r, rap, g, unit=u.ABmag).value

        comet = Comet(afrho1=100, k=-2)
        m = comet.mag(g, "r", rap=rap.value)

        assert np.isclose(m, m0, atol=0.05)

    def test_mag_raises(self):
        comet = Comet(afrho1=100, k=-2)
        g = {"rh": 2.0 * u.au, "delta": 1.0 * u.au, "phase": 0 * u.deg}
        with pytest.raises(KeyError) as excinfo:
            _ = comet.mag(geom=g, bandpass="t", rap=1)

        assert "but was provided: t" in str(excinfo.value)

from sorcha_addons.lightcurve.sinusoidal.sinusoidal_lightcurve import SinusoidalLightCurve
import pandas as pd
import numpy as np


def test_sinusoidal_lightcurve_name():
    assert "sinusoidal" == SinusoidalLightCurve.name_id()


def test_compute_simple():
    data_dict = {
        "fieldMJD_TAI": [1.0 / 4],
        "LCA": [1],
        "Period": [1],
        "Time0": [0],
    }

    df = pd.DataFrame.from_dict(data_dict)

    model = SinusoidalLightCurve()
    output = model.compute(df)

    assert np.isclose(output.values[0], 1)

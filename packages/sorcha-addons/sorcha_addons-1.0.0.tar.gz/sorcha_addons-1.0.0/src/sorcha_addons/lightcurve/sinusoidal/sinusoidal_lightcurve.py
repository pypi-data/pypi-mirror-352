from sorcha.lightcurves.base_lightcurve import AbstractLightCurve

from typing import List
import pandas as pd
import numpy as np


class SinusoidalLightCurve(AbstractLightCurve):
    """
    Assumes a sinusoidal lightcurve in magnitude space with a given period and lightcurve amplitude.
    The observation dataframe provided to the ``compute``
    method should have the following columns:

    * ``FieldMJD_TAI`` - time of observation.
    * ``LCA`` - lightcurve amplitude [magnitudes].
    * ``Period`` - period of the sinusoidal oscillation [days]. Should be a positive value.
    * ``Time0`` - phase for the light curve [days].
    """

    def __init__(self, required_column_names: List[str] = ["fieldMJD_TAI", "LCA", "Period", "Time0"]) -> None:
        super().__init__(required_column_names)

    def compute(self, df: pd.DataFrame) -> np.array:
        """
        Computes a sinusoidal light curve given the input dataframe

        Parameters
        ----------
        df : pd.DataFrame
            The ``observations`` dataframe provided by ``Sorcha``.

        Returns
        -------
        np.array
            Numpy array of with shape equal to the input dataframe "FieldMJD"
            column. Values are changes to the magnitude.
        """

        # Verify that the input data frame contains each of the required columns.
        self._validate_column_names(df)

        time = 2 * np.pi * (df["fieldMJD_TAI"] - df["Time0"]) / df["Period"]
        return df["LCA"] * np.sin(time)

    @staticmethod
    def name_id() -> str:
        """Returns the string identifier for this light curve method. It must be
        unique within all the subclasses of ``AbstractLightCurve``.

        Returns
        -------
        str
            Unique identifier for this light curve calculator
        """
        return "sinusoidal"

    def maxBrightness(self, df: pd.DataFrame) -> float:
        return -df["LCA"]  # note this - because magnitudes are weird

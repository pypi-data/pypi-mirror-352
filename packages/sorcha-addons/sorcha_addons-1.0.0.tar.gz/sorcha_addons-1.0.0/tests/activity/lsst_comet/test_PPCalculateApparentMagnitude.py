import pytest
from numpy.testing import assert_almost_equal
import pandas as pd

from sorcha.modules.PPCalculateSimpleCometaryMagnitude import PPCalculateSimpleCometaryMagnitude

# imported so that it can be registered by `update_activity_subclasses`
from sorcha_addons.activity.lsst_comet.lsst_comet_activity import LSSTCometActivity
from sorcha.activity.activity_registration import update_activity_subclasses


# TODO Remove this `skip` decorator once the config variable for which cometary activity class to use is passed through
@pytest.mark.skip
def test_PPCalculateApparentMagnitude_with_comet():
    from sorcha.modules.PPCalculateApparentMagnitude import PPCalculateApparentMagnitude

    update_activity_subclasses()

    cometary_obs = pd.DataFrame(
        {
            "AstRange(km)": [7.35908481e08],
            "Ast-Sun(J2000x)(km)": [-5.61871308e08],
            "Ast-Sun(J2000y)(km)": [-5.47551402e08],
            "Ast-Sun(J2000z)(km)": [-2.48566276e08],
            "Sun-Ast-Obs(deg)": [8.899486],
            "optFilter": ["i"],
            "H_r": [15.9],
            "GS": [0.19],
            "afrho1": [1552],
            "k": [-3.35],
            "i-r": [-0.12],
            "seeingFwhmEff": [1.0],
        }
    )

    # TODO Check this method signature once the cometary activity class config is available.
    comet_out = PPCalculateApparentMagnitude(
        cometary_obs, "HG", "r", ["i-r"], ["r", "i"], "comet", "lsst_comet"
    )

    assert_almost_equal(comet_out["H_filter"].values[0], 15.78, decimal=6)
    assert_almost_equal(comet_out["TrailedSourceMag"].values[0], 23.210883, decimal=6)


def test_PPCalculateSimpleCometaryMagnitude():
    # Updates the dictionary of available subclasses of `AbstractCometaryActivity`
    update_activity_subclasses()

    cometary_obs = pd.DataFrame(
        {
            "optFilter": ["r", "r"],
            "trailedSourceMagTrue": [19.676259, 22.748274],
            "H_r": [15.35, 15.35],
            "afrho1": [1552, 1552],
            "k": [-3.35, -3.35],
        }
    )

    rho = [1.260000, 4.889116]
    delta = [1.709000, 4.298050]
    alpha = [35.100000, 10.339021]

    df_comet = PPCalculateSimpleCometaryMagnitude(cometary_obs, ["r"], rho, delta, alpha, "lsst_comet")

    assert_almost_equal(df_comet["trailedSourceMagTrue"], [15.757, 22.461], decimal=3)

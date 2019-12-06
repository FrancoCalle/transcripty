import numpy as np
import scipy.optimize as opt

from hyperopt import fmin, tpe, Trials
from hyperopt import hp
from functools import partial

from .targets import CalibrationTargets, CT, CPMParams, HPMParams, HL_OPT_PARAMS
from ..probabilitymodels import (
    CommonProbabilityModel, HeterogeneousProbabilityModel
)


def HPMobjective(params, target):
    """
    Used as objective function in calibrateHPM

    Parameters
    ----------
    params : np.array((4,), float64)
        An array of the parameters ordered according to HPMParams
    target : CalibrationTargets
        The calibration targets

    Returns
    -------
    score : float64
        The score associated with a particular parameter set
    """
    # Create and simulate the model to get samples of gpa and credits
    model = HeterogeneousProbabilityModel(*params, 6, 12, 3, 125)
    a_i, gpa_i, credits = model.simulate(5000)

    # Compute score
    score = target.compare_results(gpa_i, credits, corrmult=0.7, normalize=True)

    return score


def calibrateHPM(target=CT, nevals=500):
    """
    Searches the parameter space to find the set of parameters that
    provide the best fit to our calibration targets

    Parameters
    ----------
    target : CalibrationTargets
        The calibration targets

    Returns
    -------
    parameters : (CPMParams/HPMParams)
        The parameters found by the optimization algorithm
    """
    # Set up the arguments to the optimization
    f = partial(HPMobjective, target=CT)
    space = [
        hp.uniform("gamma_min", 0.05, 0.60),
        hp.uniform("gamma_1", 0.20, 2.5),
        hp.uniform("gamma_2", 0.20, 2.5),
        hp.uniform("sigma", 1e-4, 1.0)
    ]
    tpe_trials = Trials()

    # Optimize
    out = fmin(
        fn=f, space=space, algo=tpe.suggest, trials=tpe_trials, max_evals=nevals
    )

    return out, tpe_trials


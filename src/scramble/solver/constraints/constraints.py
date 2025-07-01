from ortools.sat.python.cp_model import CpModel
from scramble.solver.constraints.constraint_functions import CONSTRAINT_FUNCTIONS
from scramble.solver.constraints.symmetries_functions import SYMMETRY_FUNCTIONS
from scramble.solver.model_variables import ModelVariables


def add_constraints(mdl: CpModel, mv: ModelVariables):
    """
    Adds all constraints to the model based on the provided model variables.

    Parameters
    ----------
    mdl : CpModel
        The CP model to which the constraints are added.
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.
    """
    for constraint_fn in CONSTRAINT_FUNCTIONS:
        constraint_fn(mdl, mv)


def add_symmetry_breaking(mdl: CpModel, mv: ModelVariables):
    """
    Adds symmetry-breaking constraints to the model based on the provided model variables.

    Parameters
    ----------
    mdl : CpModel
        The CP model to which the symmetry-breaking constraints are added.
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.
    """
    for symmetry_fn in SYMMETRY_FUNCTIONS:
        symmetry_fn(mdl, mv)

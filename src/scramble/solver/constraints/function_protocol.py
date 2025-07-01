from typing import Protocol
from ortools.sat.python.cp_model import CpModel
from scramble.solver.model_variables import ModelVariables


class ConstraintFunction(Protocol):
    def __call__(self, mdl: CpModel, mv: ModelVariables):
        """
        Adds a constraint expression for the given model and variables.

        Parameters
        ----------
        mdl : CpModel
            The CP model to which the constraint is applied.
        mv : ModelVariables
            The model variables containing decision variables and other relevant data.
        """
        ...

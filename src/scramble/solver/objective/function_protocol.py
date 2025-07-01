from typing import Protocol
from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.solver.model_variables import ModelVariables


class ScoringFunction(Protocol):
    def __call__(self, mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
        """
        A scoring function computes a penalty (higher is worse) for a round.

        Parameters
        ----------
        mdl : CpModel
            The CP model to which the scoring function is applied.
        mv : ModelVariables
            The model variables containing decision variables and other relevant data.

        Returns
        -------
        LinearExpr | IntVar
            A linear expression or integer variable representing the penalty score.
        """
        ...
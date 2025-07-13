from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.solver.objective.scoring_functions import SCORING_FUNCTIONS
from scramble.solver.model_variables import ModelVariables


def score_round(mdl: CpModel, mv: ModelVariables) -> dict:
    """
    Computes individual symbolic penalty expressions for enabled goals.

    Returns
    -------
    dict[Goal, LinearExpr | IntVar]
        A dictionary mapping goals to their symbolic penalty expression.
    """
    expressions = {}

    for goal, cfg in mv.settings.goal_configs.items():
        if cfg.enabled and goal in SCORING_FUNCTIONS:
            expressions[goal] = SCORING_FUNCTIONS[goal](mdl, mv)

    return expressions

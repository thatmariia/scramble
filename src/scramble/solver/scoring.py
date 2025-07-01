from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.solver.scoring_functions import SCORING_FUNCTIONS, ModelVariables


def score_round(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Computes the total weighted penalty score for a round based on active goals.
    Lower scores are better.

    Parameters
    ----------
    mdl : CpModel
        The CP model to which the scoring function is applied.
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.

    Returns
    -------
    float
        The total penalty score for the round.
    """
    terms = []

    for goal, cfg in mv.settings.goal_configs.items():
        if not cfg.enabled or goal not in SCORING_FUNCTIONS:
            continue

        # symbolic penalty expression for this goal
        expr = SCORING_FUNCTIONS[goal](mdl, mv)

        terms.append(cfg.weight * expr)

    if not terms:
        # Return a constant zero IntVar if no goals enabled
        zero = mdl.NewIntVar(0, 0, "zero_obj")
        return zero

    return sum(terms)

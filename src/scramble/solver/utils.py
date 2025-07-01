from ortools.sat.python.cp_model import CpModel


def define_and_var(mdl: CpModel, name: str, vars: list):
    """
    Creates a BoolVar `out` such that:
        out <=> (vars[0] AND vars[1] AND ... AND vars[n])
    """
    out = mdl.NewBoolVar(name)
    mdl.AddBoolAnd(vars).OnlyEnforceIf(out)
    mdl.AddBoolOr([v.Not() for v in vars]).OnlyEnforceIf(out.Not())
    return out


def define_or_var(mdl: CpModel, name: str, vars: list):
    """
    Creates a BoolVar `out` such that:
        out <=> (vars[0] OR vars[1] OR ... OR vars[n])
    """
    out = mdl.NewBoolVar(name)
    mdl.AddBoolOr(vars).OnlyEnforceIf(out)
    mdl.AddBoolAnd([v.Not() for v in vars]).OnlyEnforceIf(out.Not())
    return out

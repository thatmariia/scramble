from ortools.sat.python.cp_model import CpModel, IntVar


def absolute_slack(mdl: CpModel, x: IntVar, name: str, ub: int) -> IntVar:
    s = mdl.NewIntVar(0, ub, name)
    mdl.Add(s >=  x)
    mdl.Add(s >= -x)
    return s


def define_and_var_bool(mdl: CpModel, a, b, name: str):
    """
    Return c = a ∧ b using only *linear* constraints.
    Much lighter than AddBoolAnd/Or when you don't need the clauses.
    """
    c = mdl.new_bool_var(name)
    # c ⇒ a     and     c ⇒ b
    mdl.add(a >= c)
    mdl.add(b >= c)
    # a + b – 1 ≥ c   (⇐ direction)
    mdl.add(a + b - 1 <= c)   # same as c ≤ a + b - 1
    return c


def define_and_var_imp(mdl, a, b, name):
    v = mdl.NewBoolVar(name)

    # v => a  and  v => b
    mdl.AddImplication(v, a)
    mdl.AddImplication(v, b)

    # a and b => v
    mdl.Add(a + b - v >= 1)

    return v


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

from ortools.sat.python.cp_model import CpModel, IntVar
from ortools.sat.python import cp_model as cp
import operator
from typing import Union, Callable

IntLike = Union[int, cp.IntVar]


def multiply_vars(mdl: cp.CpModel, vars: list[cp.IntVar], name: str) -> cp.IntVar:
    """
    Returns a new IntVar representing the product of the input IntVars.
    The output variable is bounded between 0 and the product of the upper bounds of the input variables.
    """
    if not vars:
        raise ValueError("At least one variable is required for multiplication.")

    # Calculate the bounds for the product
    lb = 1
    ub = 1
    for var in vars:
        lb *= var.Proto().domain[0]
        ub *= var.Proto().domain[-1]

    out = mdl.new_int_var(lb, ub, name)
    mdl.add_multiplication_equality(out, vars)
    return out


def reify_existing_with_inequality(mdl: cp.CpModel, out: cp.IntVar, target: IntLike, cond: cp.IntVar) -> cp.IntVar:
    dom = out.Proto().domain
    big_m = dom[-1] - dom[0]

    mdl.add(out == target).only_enforce_if(cond)
    mdl.add(out != target).only_enforce_if(cond.Not())

    mdl.add(out - target >= -big_m * (1 - cond))
    mdl.add(out - target <= big_m * (1 - cond))

    return out


def reify_with_inequality(mdl: cp.CpModel, target: IntLike, cond: cp.IntVar, lo_hi: tuple[int, int], name: str) -> cp.IntVar:
    lo, hi = lo_hi
    out = mdl.new_int_var(lo, hi, name)
    reify_existing_with_inequality(mdl, out, target, cond)
    return out


def reify_existing_with_fallback(mdl: cp.CpModel, out: cp.IntVar, target: IntLike, fallback: IntLike, cond: cp.IntVar, op: Callable = operator.eq) -> cp.IntVar:
    dom = out.Proto().domain
    big_m = dom[-1] - dom[0]

    def _is_non_negative(x) -> bool:
        """Return True iff we *can prove* that x ≥ 0 from its domain."""
        if isinstance(x, int):
            return x >= 0
        if isinstance(x, IntVar):
            dom = x.Proto().domain  # lowest value is the first element
            return dom[0] >= 0
        # Anything else (LinearExpr, SumArray, etc.) – we don’t know its bounds
        return False

    if op is operator.eq:
        if fallback == 0 and _is_non_negative(target) and _is_non_negative(out):
            # 100 % safe: product will also be non-negative
            mdl.add_multiplication_equality(out, [cond, target])
        else:
            # generic – two half-reified equalities, no Big-M needed
            mdl.add(out == target).only_enforce_if(cond)
            mdl.add(out == fallback).only_enforce_if(cond.Not())

    elif op is operator.ge:
        mdl.add(out >= target).only_enforce_if(cond)
        mdl.add(out == fallback).only_enforce_if(cond.Not())

    elif op is operator.le:
        mdl.add(out <= target).only_enforce_if(cond)
        mdl.add(out == fallback).only_enforce_if(cond.Not())

    else:
        raise ValueError(f"Unsupported operator: {op}")

    # if op is operator.eq:
    #     mdl.add(out == target).only_enforce_if(cond)
    #     mdl.add(out == fallback).only_enforce_if(cond.Not())
    #
    #     mdl.add(out - target >= -big_m * (1 - cond))
    #     mdl.add(out - target <= big_m * (1 - cond))
    #     mdl.add(out - fallback >= -big_m * cond)
    #     mdl.add(out - fallback <= big_m * cond)
    #
    # elif op is operator.ge:
    #     mdl.add(out >= target).only_enforce_if(cond)
    #     mdl.add(out == fallback).only_enforce_if(cond.Not())
    #     mdl.add(out - target >= -big_m * (1 - cond))
    #     mdl.add(out - fallback >= -big_m * cond)
    #
    # elif op is operator.le:
    #     mdl.add(out <= target).only_enforce_if(cond)
    #     mdl.add(out == fallback).only_enforce_if(cond.Not())
    #     mdl.add(out - target <= big_m * (1 - cond))
    #     mdl.add(out - fallback <= big_m * cond)
    #
    # else:
    #     raise ValueError(f"Unsupported operator: {op}")

    return out


def reify_with_fallback(mdl: cp.CpModel, target: IntLike,  fallback: IntLike, cond: cp.IntVar, lo_hi: tuple[int, int], name: str, op: Callable = operator.eq) -> cp.IntVar:
    lo, hi = lo_hi
    out = mdl.new_int_var(lo, hi, name)
    reify_existing_with_fallback(mdl, out, target, fallback, cond, op)
    return out


def absolute_value(mdl: CpModel, x: IntVar, name: str, ub: int) -> IntVar:
    """
    Returns a new IntVar representing the absolute value of x.
    The output variable is bounded between 0 and ub.
    """
    abs_x = mdl.new_int_var(0, ub, name)
    mdl.add_abs_equality(abs_x, x)
    return abs_x


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

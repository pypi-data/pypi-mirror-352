import numpy as np
import sympy as s
from .symbols import x
from .domain import find_domain
from ..utils.numerics import sample_points, fallback_points

def find_range(expr_str):
    expr = s.sympify(expr_str)
    domain = find_domain(expr)
    points_to_check = []

    if isinstance(domain, s.Interval):
        if domain.start.is_finite and domain.end.is_finite:
            points_to_check += sample_points(domain.start, domain.end)
        elif domain == s.Interval(-s.oo, s.oo):
            points_to_check += fallback_points()
        else:
            points_to_check += fallback_points()
    elif isinstance(domain, s.Union):
        for interval in domain.args:
            if isinstance(interval, s.Interval):
                if interval.start.is_finite and interval.end.is_finite:
                    points_to_check += sample_points(interval.start, interval.end, count=3)
    else:
        points_to_check += fallback_points()

    f_np = s.lambdify(x, expr, modules=['numpy'])
    y_vals = []
    for pt in points_to_check:
        try:
            val = f_np(pt)
            if np.isfinite(val):
                y_vals.append(val)
        except:
            continue

    if y_vals:
        return [min(y_vals), max(y_vals)]
    return "Range could not be determined."


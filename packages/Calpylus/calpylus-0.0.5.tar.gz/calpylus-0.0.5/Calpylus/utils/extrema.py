import sympy as s
from .checks import is_finite
from ..core.symbols import x

def find_extrema(expr_str):
    expr = s.sympify(expr_str)
    deriv = s.diff(expr, x)
    critical_points = s.solve(deriv, x)
    finite_points = [pt for pt in critical_points if is_finite(pt)]
    return finite_points


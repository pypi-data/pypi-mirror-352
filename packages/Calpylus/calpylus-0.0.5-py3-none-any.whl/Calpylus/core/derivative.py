import sympy as s
from .symbols import x, c

def derivative(expr_str, wrt='x'):
    sym = s.Symbol(wrt)
    expr = s.sympify(expr_str, locals={wrt: sym, 'c': c})
    deriv = s.diff(expr, sym).doit()
    comp = len(deriv.atoms()) + s.count_ops(deriv)
    return s.simplify(deriv) if comp < 100 else deriv


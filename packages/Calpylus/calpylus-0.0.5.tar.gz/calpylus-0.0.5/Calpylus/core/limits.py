import sympy as s

def compute_limit(expr_str, var='x', to=0, dir='+'):
    sym = s.Symbol(var)
    expr = s.sympify(expr_str)
    return s.limit(expr, sym, to, dir)


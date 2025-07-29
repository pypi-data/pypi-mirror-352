import sympy as s

def taylor_series(expr_str, var='x', about=0, n=6):
    sym = s.Symbol(var)
    expr = s.sympify(expr_str)
    return s.series(expr, sym, about, n).removeO()


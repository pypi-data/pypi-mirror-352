import sympy as s

def indefinite_integral(expr_str, wrt='x'):
    sym = s.Symbol(wrt)
    expr = s.sympify(expr_str)
    return s.integrate(expr, sym)

def definite_integral(expr_str, lower, upper, wrt='x'):
    sym = s.Symbol(wrt)
    expr = s.sympify(expr_str)
    return s.integrate(expr, (sym, lower, upper))


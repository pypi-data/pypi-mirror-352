import sympy as s

def partial_derivative(expr_str, var='x'):
    sym = s.Symbol(var)
    expr = s.sympify(expr_str)
    return s.diff(expr, sym)

def gradient(expr_str, vars_str='x y'):
    vars = [s.Symbol(v) for v in vars_str.split()]
    expr = s.sympify(expr_str)
    return [s.diff(expr, v) for v in vars]


import sympy as s

def simplify_expr(expr_str, locals=None):
    return s.simplify(s.sympify(expr_str, locals=locals))


import sympy as s
from sympy import S
from sympy.calculus.util import continuous_domain
from .symbols import x

def find_domain(expr):
    return continuous_domain(s.sympify(expr), x, S.Reals)


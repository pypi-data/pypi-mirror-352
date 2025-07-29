import sympy as s

def is_finite(value):
    if isinstance(value, (int, float)): return True
    if not isinstance(value, s.Basic): return False
    return value.is_real and not value.has(s.zoo, s.nan)


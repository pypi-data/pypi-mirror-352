# Expose essential components of CalPylus
from .core.symbols import x, y, z, pi, E, c
from .core.simplifier import simplify_expr
from .core.domain import find_domain
from .core.derivative import derivative
from .core.graphing import plot_2D, plot_3D
from .core.range_finder import find_range
from .core.integrals import definite_integral, indefinite_integral
from .core.limits import compute_limit
from .core.series import taylor_series
from .core.multivariable import gradient, partial_derivative
from .utils.checks import is_finite
from .utils.numerics import sample_points, fallback_points
from .utils.extrema import find_extrema

__all__ = [
    'x', 'y', 'z', 'pi', 'E', 'c',
    'simplify_expr', 'find_domain', 'derivative', 'plot_2D','plot_3D', 'find_range',
    'definite_integral', 'indefinite_integral', 'compute_limit', 'taylor_series',
    'gradient', 'partial_derivative',
    'is_finite', 'sample_points', 'fallback_points', 'find_extrema'
]


import numpy as np

def sample_points(start, end, count=5):
    try:
        return np.linspace(float(start), float(end), count).tolist()
    except Exception:
        return []

def fallback_points():
    return [-10, -1, 0, 1, 10]


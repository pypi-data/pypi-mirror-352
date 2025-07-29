import matplotlib.pyplot as plt
import numpy as np
import sympy as s
from .symbols import x

def plot_2D(expr_str):
    try:
        expr = s.sympify(expr_str)
        f_np = s.lambdify(x, expr, modules=['numpy'])
        x_vals = np.linspace(-10, 10, 300)
        y_vals = f_np(x_vals)
        y_vals = np.clip(y_vals, -10, 10)

        plt.figure()
        plt.plot(x_vals, y_vals, label=str(expr))
        plt.axhline(0, color='black', lw=0.5)
        plt.axvline(0, color='black', lw=0.5)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title(f"Graph of {expr}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.show(block=False)
    except Exception as e:
        print("Graph error:", e)

def plot_3D(function_str):
    x, y = s.symbols('x y')
    try:
        expr = s.sympify(function_str)
        func = s.lambdify((x, y), expr, modules=["numpy"])
        X_vals = np.linspace(-5, 5, 100)
        Y_vals = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(X_vals, Y_vals)
        Z = func(X, Y)

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_title(f"3D Plot of: {function_str}")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.set_zlabel("f(x, y)")
        plt.show(block=False)  # <- show without blocking
    except Exception as e:
        print("Failed to plot 3D graph:", e)

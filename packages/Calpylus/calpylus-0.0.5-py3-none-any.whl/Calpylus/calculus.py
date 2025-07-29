import matplotlib.pyplot as plt
import numpy as np
import sympy as s
from sympy import S, sin, cos, tan, cot, pi, E
from sympy.calculus.util import continuous_domain 
from mpl_toolkits.mplot3d import Axes3D

class Calculus:
    x = s.symbols('x')
    y = s.symbols('y')
    z = s.symbols('z')
    pi = pi
    e = E

    @staticmethod
    def symplify(function):
        return s.sympify(function)

    @staticmethod
    def domain(function):
        function = s.sympify(function)
        return continuous_domain(function, Calculus.x, S.Reals)
    @staticmethod
    def range(function):
        try:
            f = s.sympify(function)
            x = Calculus.x
            domain = Calculus.domain(f)

            # Collect candidate points: critical points + endpoints if finite
            criticals = Calculus.critical_points(f)
            points_to_check = []

            # Add endpoints of domain if they are finite
            if hasattr(domain, 'start') and hasattr(domain, 'end'):
                if domain.start.is_real:
                    points_to_check.append(domain.start)
                if domain.end.is_real:
                    points_to_check.append(domain.end)

            # Add critical points within domain
            for pt in criticals:
                if isinstance(pt, (int, float, s.Basic)) and Calculus.is_finite(pt):
                    if pt in domain:
                        points_to_check.append(pt)

            # Add some numerical points for estimation
            if isinstance(domain, s.Interval):
                if domain.start.is_finite and domain.end.is_finite:
                    pts = np.linspace(float(domain.start), float(domain.end), 5)
                    points_to_check += list(pts)
                elif domain == s.Interval(-s.oo, s.oo):
                    points_to_check += [-10, -1, 0, 1, 10]
                else:
                    # Fallback for other types of domains like Union, etc.
                    points_to_check += [-10, -1, 0, 1, 10]




            # Remove duplicates and evaluate
            points_to_check = list(set(points_to_check))
            values = []
            for pt in points_to_check:
                try:
                    val = f.subs(x, pt).evalf()
                    if Calculus.is_finite(val):
                        values.append(val)
                except:
                    continue

            if not values:
                return "Range could not be determined"

            min_val = min(values)
            max_val = max(values)
            return f"[{min_val}, {max_val}] (estimated)"

        except Exception as e:
            return f"Error determining range: {e}"


    @staticmethod
    def derivative(function, wrt='x'):
        sym = s.Symbol(wrt)
        c = s.Symbol('c')
        f = s.Function('f')
        expr = s.sympify(function, locals={wrt: sym, 'c': c, 'f': f})
        derivative = s.diff(expr, sym).doit()
        comp = len(derivative.atoms()) + s.count_ops(derivative)
        return s.simplify(derivative) if comp < 100 else derivative

    @staticmethod
    def critical_points(function):
        function = s.sympify(function)
        df = Calculus.derivative(function)
        df = df.rewrite(s.Piecewise).replace(s.Abs(Calculus.x), s.Piecewise((-Calculus.x, Calculus.x < 0), (Calculus.x, Calculus.x >= 0)))
        try:
            cp = s.solve(s.Eq(df, 0), Calculus.x)
        except NotImplementedError:
            cp = []
            for guess in [-5, -2, 0, 2, 5, 10]:
                try:
                    root = s.nsolve(df, Calculus.x, guess)
                    if root not in cp:
                        cp.append(root)
                except:
                    continue
        return cp if cp else "No extreme points"

    @staticmethod
    def _table_code(function):
        yf = s.sympify(function)
        D = Calculus.domain(function)
        f = Calculus.derivative(function)
        ex = Calculus.critical_points(function)
        ea = len(ex)
        tc = 2 * ea + 1
        t = np.empty((3, tc + 1), dtype=object)
        t[0, 0] = 'X'
        t[1, 0] = 'Y'
        t[2, 0] = "Y'"
        for i in range(1, ea + 1):
            t[0, 2 * i] = ex[i - 1]
            if i > 1:
                t[0, 2 * i - 1] = (ex[i - 2] + ex[i - 1]) / 2
        t[0, tc] = ex[-1] + 1
        t[0, 1] = ex[0] - 1
        ey = [yf.subs(Calculus.x, xi) for xi in ex]
        for i in range(1, len(ey) + 1):
            t[1, 2 * i] = ey[i - 1]
        yf1 = s.simplify(s.sympify(f))
        for i in range(1, tc + 1):
            t[2, i] = yf1.subs(Calculus.x, t[0, i])
            t[1, i] = "U" if t[2, i] > 0 else "D" if t[2, i] < 0 else None
        u = d = ""
        if t[1, 1] == "U": u += "x<" + str(t[0, 2])
        if t[1, 1] == "D": d += "x<" + str(t[0, 2])
        if t[1, -1] == "U": u += ", x>" + str(t[0, -2])
        if t[1, -1] == "D": d += ", x>" + str(t[0, -2])
        for i in range(3, tc - 1):
            if t[1, i] == "U": u += ", {}<x<{}".format(t[0, i - 1], t[0, i + 1])
            if t[1, i] == "D": d += ", {}<x<{}".format(t[0, i - 1], t[0, i + 1])
        if not d: d = "No decreasing intervals"
        if not u: u = "No increasing intervals"
        exy = ["({}, {})".format(ex[i], ey[i]) for i in range(len(ex))]
        ep = []
        for i in range(1, ea + 1):
            if t[1, 2 * i - 1] == "U" and t[1, 2 * i + 1] == "D": ep.append(exy[i - 1] + " max")
            if t[1, 2 * i - 1] == "D" and t[1, 2 * i + 1] == "U": ep.append(exy[i - 1] + " min")
        return t, d, u, ep

    @staticmethod
    def table(function): return Calculus._table_code(function)[0]
    @staticmethod
    def extreme(function): return Calculus._table_code(function)[3]
    @staticmethod
    def decreasing(function): return Calculus._table_code(function)[1]
    @staticmethod
    def increasing(function): return Calculus._table_code(function)[2]

    @staticmethod
    def is_finite(value):
        if isinstance(value, (int, float)): return True
        if not isinstance(value, s.Basic): return False
        return value.is_real and not value.has(s.zoo, s.nan)

    @staticmethod
    def graph(function_str, wrt='x'):
        x = s.Symbol(wrt)
        c = s.Symbol('c')
        f = s.Function('f')
        try:
            function = s.sympify(function_str, locals={wrt: x, 'c': c, 'f': f})
            if function.has(f):
                print("Can't plot undefined functions like f(x). Skipping graph.")
                return
            f_np = s.lambdify(x, function, modules=["numpy"])
            x_vals = np.linspace(-10, 10, 300)
            y_vals = np.array(f_np(x_vals), dtype=np.float64).flatten()
            y_vals = np.clip(y_vals, -10, 10)
            
            plt.figure()  # <- create a new figure
            plt.plot(x_vals, y_vals, label=str(function), color='b')
            plt.axhline(0, color='black', lw=0.5)
            plt.axvline(0, color='black', lw=0.5)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.title(f"Graph of {function}")
            plt.xlabel(wrt)
            plt.ylabel("f(" + wrt + ")")
            plt.legend()
            plt.show(block=False)  # <- show without blocking
        except Exception as e:
            print("Graph error:", e)

    @staticmethod
    def graph3D(function_str):
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

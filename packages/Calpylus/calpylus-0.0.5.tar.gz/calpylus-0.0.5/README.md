# 📐 Calpylus

Calpylus is a powerful and beginner-friendly Python library built for symbolic and visual calculus. Whether you're a student studying calculus, an educator building tools, or a developer creating math-powered apps — Calpylus has your back with expressive syntax, beautiful plotting, and a growing feature set.

> Developed with ❤️ by [Mohammad Mahfuz Rahman](https://github.com/mahfuz0712)

---

## ✨ Features

- ✅ Symbolic Differentiation and Integration
- ✅ 2D Function Plotting (Matplotlib-based)
- ✅ 3D Surface Plotting (`graph3D`)
- ✅ Simple, intuitive API
- ✅ Built using `SymPy` and `Matplotlib`

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install calpylus
```

Or install from GitHub (for development):

```bash
pip install git+https://github.com/mahfuz0712/Calpylus.git
```

---

## 🧪 Quick Start

```python
import matplotlib.pyplot as plt
from calpylus.calculus import Calculus as cl

# Define a function
f = "sin(x)"
g = "cos(x)"

# Plot 2D graphs
cl.graph(f)
cl.graph(g)

# Plot a 3D surface
cl.graph3D("sin(x)*cos(y)")

# Final blocking call to keep all windows open until closed manually
plt.show()
```

---

## Differential & Integral Calculus

Symbolically differentiate an expression with respect to a variable.

```python
cl.differentiate("x**2 + sin(x)")
# Output: 2*x + cos(x)

cl.differentiate(expr: str, variable='x')
```

---


Symbolically integrate an expression with respect to a variable.

```python
cl.integrate("x**2")
# Output: x**3/3

cl.integrate(expr: str, variable='x')
```

---

### Graphical View
Plots a 2D graph of a function of `x`.

```python

cl.graph(expr: str)

cl.graph("x**2 + 2*x + 1")
```

---

### 3D Graph
Plots a 3D surface plot of a function in terms of `x` and `y`.

```python
cl.graph3D(expr: str)
cl.graph3D("sin(x) * cos(y)")
```

---

## 🧠 Under the Hood

| Feature        | Library Used     |
|----------------|------------------|
| Symbolic Math  | `sympy`          |
| 2D/3D Plotting | `matplotlib`     |


---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or add.

To run locally:

```bash
git clone https://github.com/mahfuz0712/Calpylus.git
cd Calpylus
pip install -e .
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 FAQ

**Q: Can I use this library without knowing advanced calculus?**  
A: Yes! The library is designed to be intuitive and beginner-friendly.

**Q: Will you add support for limits, series expansion, etc.?**  
A: Absolutely. These features are planned in future releases.

---

## 🌐 Links

- 📦 [PyPI Project](https://pypi.org/project/calpylus/)
- 🧠 [Developer: @mahfuz0712](https://github.com/mahfuz0712)
- 📚 [SymPy Documentation](https://docs.sympy.org)

---

> “Mathematics is the music of reason.” — James Joseph Sylvester  
> Calpylus turns that music into code. 🎶

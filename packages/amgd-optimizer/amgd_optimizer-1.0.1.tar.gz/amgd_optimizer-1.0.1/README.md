# AMGD_Optimizer: Adaptive Momentum Gradient Descent for Regularized Poisson Regression

[![PyPI version](https://badge.fury.io/py/amgd_optimizer.svg)](https://badge.fury.io/py/amgd_optimizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://readthedocs.org/projects/amgd-python/badge/?version=latest)](https://amgd-python.readthedocs.io/)

A high-performance Python package implementing the **Adaptive Momentum Gradient Descent (AMGD)** algorithm for regularized Poisson regression. AMGD provides superior performance for sparse, high-dimensional count data modeling.

## 🚀 Key Features

- **56.6% reduction** in Mean Absolute Error compared to AdaGrad
- **2.7% improvement** over Adam optimizer
- **35.29% sparsity** achievement through effective feature selection
- **Novel adaptive soft-thresholding** for direct L1 penalty handling
- **Scikit-learn compatible** API for seamless integration
- **Comprehensive validation** with statistical significance testing

## 📊 Performance Highlights

| Metric | AMGD | Adam | AdaGrad | Improvement |
|--------|------|------|---------|-------------|
| MAE | 3.016 | 3.101 | 6.945 | **-56.6%** vs AdaGrad |
| RMSE | 3.885 | 4.001 | 7.653 | **-49.2%** vs AdaGrad |
| Sparsity | 35.29% | 11.76% | 0.00% | **+200%** vs Adam |

*Results from ecological dataset with 61,345 observations and 17 features*

## 🛠️ Installation

### From PyPI (recommended)
```bash
pip install amgd-python
```

### From Source
```bash
git clone https://github.com/yourusername/amgd-python.git
cd amgd-python
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/amgd-python.git
cd amgd-python
pip install -e ".[dev,docs,examples]"
```

## 🏃‍♂️ Quick Start

### Basic Usage

```python
import numpy as np
from amgd import AMGDPoissonRegressor

# Generate sample count data
np.random.seed(42)
X = np.random.randn(1000, 20)
y = np.random.poisson(np.exp(X @ np.random.randn(20) * 0.1))

# Fit AMGD model
model = AMGDPoissonRegressor(
    alpha=0.01,           # Regularization strength
    l1_ratio=0.7,         # 70% L1, 30% L2 penalty
    max_iter=1000
)

model.fit(X, y)
predictions = model.predict(X)

# Check results
print(f"Sparsity: {model.get_sparsity():.2%}")
print(f"Selected features: {np.sum(np.abs(model.coef_) > 1e-8)}")
print(f"Converged in: {model.n_iter_} iterations")
```

### Feature Selection Example

```python
from amgd import AMGDPoissonRegressor
import matplotlib.pyplot as plt

# Fit with different regularization strengths
alphas = [0.001, 0.01, 0.1, 1.0]
sparsities = []

for alpha in alphas:
    model = AMGDPoissonRegressor(alpha=alpha, l1_ratio=1.0)  # Pure L1
    model.fit(X, y)
    sparsities.append(model.get_sparsity())
    print(f"α={alpha}: {model.get_sparsity():.1%} sparsity, "
          f"{np.sum(np.abs(model.coef_) > 1e-8)} features selected")

# Plot sparsity vs regularization
plt.figure(figsize=(8, 5))
plt.semilogx(alphas, sparsities, 'o-')
plt.xlabel('Regularization Strength (α)')
plt.ylabel('Sparsity Ratio')
plt.title('Feature Selection with AMGD')
plt.grid(True, alpha=0.3)
plt.show()
```

### Comparison with Other Optimizers

```python
from amgd import compare_optimizers

# Compare AMGD against other methods
results = compare_optimizers(X, y, methods=['amgd'], alpha=0.01)

for method, metrics in results.items():
    print(f"{method.upper()}:")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  RMSE: {metrics['rmse']:.4f}")
    print(f"  Sparsity: {metrics['sparsity']:.2%}")
    print(f"  Iterations: {metrics['n_iter']}")
```

## 🔬 Advanced Usage

### Custom Optimization Parameters

```python
from amgd import AMGDOptimizer

# Low-level optimizer access for custom applications
optimizer = AMGDOptimizer(
    learning_rate=0.01,
    momentum_beta1=0.9,      # First moment decay
    momentum_beta2=0.999,    # Second moment decay
    lambda1=0.01,            # L1 regularization
    lambda2=0.001,           # L2 regularization
    penalty='elasticnet',
    decay_rate=1e-4,         # Learning rate decay
    gradient_clip=5.0,       # Gradient clipping threshold
    max_iter=1000,
    tol=1e-6
)

optimizer.fit(X, y)
coefficients = optimizer.coef_
```

### Cross-Validation and Model Selection

```python
from sklearn.model_selection import GridSearchCV
from amgd import AMGDPoissonRegressor

# Hyperparameter tuning
param_grid = {
    'alpha': [0.001, 0.01, 0.1, 1.0],
    'l1_ratio': [0.1, 0.5, 0.7, 0.9],
    'learning_rate': [0.001, 0.01, 0.1]
}

model = AMGDPoissonRegressor(max_iter=500)
grid_search = GridSearchCV(
    model, 
    param_grid, 
    cv=5, 
    scoring='neg_mean_absolute_error',
    n_jobs=-1
)

grid_search.fit(X, y)
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {-grid_search.best_score_:.4f}")
```

### Monitoring Convergence

```python
# Fit with verbose output
model = AMGDPoissonRegressor(alpha=0.01, verbose=True, max_iter=1000)
model.fit(X, y)

# Plot convergence history
model.plot_convergence()
plt.show()

# Get detailed convergence info
info = model.get_convergence_info()
print(f"Converged: {info['converged']}")
print(f"Final loss: {info['final_loss']:.6f}")
```

## 🧮 Algorithm Details

AMGD integrates three key innovations:

### 1. Adaptive Learning Rate Decay
```
αₜ = α / (1 + ηt)
```

### 2. Momentum Updates with Bias Correction
```
mₜ = ζ₁mₜ₋₁ + (1 - ζ₁)∇f(βₜ)
vₜ = ζ₂vₜ₋₁ + (1 - ζ₂)(∇f(βₜ))²
m̂ₜ = mₜ / (1 - ζ₁ᵗ)
v̂ₜ = vₜ / (1 - ζ₂ᵗ)
```

### 3. Adaptive Soft-Thresholding
```
βⱼ ← sign(βⱼ) · max(|βⱼ| - αₜλ/(|βⱼ| + ε), 0)
```

This adaptive thresholding is the key innovation, providing coefficient-dependent regularization that preserves large coefficients while aggressively shrinking small ones.

## 📈 Benchmarks

### Ecological Dataset (n=61,345, p=17)

| Algorithm | MAE | RMSE | MPD | Sparsity | Iterations |
|-----------|-----|------|-----|----------|------------|
| **AMGD** | **3.016** | **3.885** | **2.185** | **35.29%** | **~300** |
| Adam | 3.101 | 4.001 | 2.249 | 11.76% | ~1000 |
| AdaGrad | 6.945 | 7.653 | 11.507 | 0.00% | >1000 |
| GLMNet | 9.007 | 9.554 | 29.394 | 0.00% | ~500 |

### Statistical Significance
All improvements are statistically significant (p < 0.0001) with large effect sizes (Cohen's d: -9.46 to -713.03).

## 🎯 Use Cases

AMGD is particularly effective for:

- **High-dimensional count data** (genomics, network analysis)
- **Sparse modeling** requiring feature selection
- **Ecological modeling** (species counts, biodiversity indices)
- **Epidemiological studies** (disease incidence rates)
- **Marketing analytics** (customer behavior counts)
- **Quality control** (defect counts, failure rates)

## 📚 Documentation

- **Full Documentation**: [https://amgd-python.readthedocs.io/](https://amgd-python.readthedocs.io/)
- **API Reference**: [https://amgd-python.readthedocs.io/en/latest/api.html](https://amgd-python.readthedocs.io/en/latest/api.html)
- **Examples**: [https://github.com/yourusername/amgd-python/tree/main/examples](https://github.com/yourusername/amgd-python/tree/main/examples)
- **Paper**: "Adaptive Momentum Gradient Descent: A New Algorithm in Regularized Poisson Regression"

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/yourusername/amgd-python.git
cd amgd-python
pip install -e ".[dev]"
pre-commit install
```

### Running Tests
```bash
pytest tests/ -v --cov=amgd
```

## 📄 Citation

If you use AMGD in your research, please cite:

```bibtex
@article{bakari2024amgd,
  title={Adaptive Momentum Gradient Descent: A New Algorithm in Regularized Poisson Regression},
  author={Bakari, Ibrahim and Özkale, M. Revan},
  journal={Journal Name},
  year={2024},
  publisher={Publisher}
}

@software{amgd_python,
  title={AMGD-Python: Adaptive Momentum Gradient Descent for Regularized Poisson Regression},
  author={Bakari, Ibrahim},
  url={https://github.com/yourusername/amgd-python},
  version={0.1.0},
  year={2024}
}
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/amgd-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/amgd-python/discussions)
- **Email**: 2020913072@ogr.cu.edu.tr

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Çukurova University** - Department of Statistics
- **Research Community** - For valuable feedback and suggestions
- **Scikit-learn** - For the API design inspiration

---

<p align="center">
  <strong>AMGD-Python: Making sparse Poisson regression fast and effective</strong>
</p>

<p align="center">
  <a href="https://github.com/yourusername/amgd-python">⭐ Star us on GitHub</a> •
  <a href="https://amgd-python.readthedocs.io/">📖 Read the Docs</a> •
  <a href="https://pypi.org/project/amgd-python/">📦 PyPI Package</a>
</p>

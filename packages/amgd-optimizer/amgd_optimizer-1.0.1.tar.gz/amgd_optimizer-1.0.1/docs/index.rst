AMGD-Python Documentation
=========================

**Adaptive Momentum Gradient Descent for Regularized Poisson Regression**

AMGD-Python is a high-performance optimization package implementing the novel Adaptive Momentum Gradient Descent (AMGD) algorithm specifically designed for sparse, high-dimensional Poisson regression with L1, L2, and Elastic Net regularization.

.. image:: https://img.shields.io/pypi/v/amgd-python.svg
   :target: https://pypi.org/project/amgd-python/
   :alt: PyPI version

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

Key Features
------------

🚀 **Superior Performance**
   - **56.6% reduction** in Mean Absolute Error compared to AdaGrad
   - **2.7% improvement** over Adam optimizer  
   - **35.29% sparsity** achievement through effective feature selection

🧮 **Novel Algorithm**
   - **Adaptive soft-thresholding** for direct L1 penalty handling
   - **Coefficient-dependent regularization** strength
   - **Theoretical convergence guarantees** with O(1/√T) rate

🔧 **Easy Integration**
   - **Scikit-learn compatible** API for seamless workflow integration
   - **Comprehensive validation** with statistical significance testing
   - **Professional documentation** and extensive examples

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install amgd-python

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   import numpy as np
   from amgd import AMGDPoissonRegressor

   # Generate sample count data
   X = np.random.randn(1000, 20)
   y = np.random.poisson(np.exp(X @ np.random.randn(20) * 0.1))

   # Fit AMGD model
   model = AMGDPoissonRegressor(alpha=0.01, l1_ratio=0.7)
   model.fit(X, y)
   predictions = model.predict(X)

   # Check sparsity and performance
   print(f"Sparsity: {model.get_sparsity():.2%}")
   print(f"Selected features: {np.sum(np.abs(model.coef_) > 1e-8)}")

Performance Highlights
----------------------

.. list-table:: Benchmark Results (Ecological Dataset: n=61,345, p=17)
   :header-rows: 1
   :widths: 20 15 15 15 15 20

   * - Algorithm
     - MAE
     - RMSE
     - MPD
     - Sparsity
     - Improvement
   * - **AMGD**
     - **3.016**
     - **3.885**
     - **2.185**
     - **35.29%**
     - **Baseline**
   * - Adam
     - 3.101
     - 4.001
     - 2.249
     - 11.76%
     - -2.7% MAE
   * - AdaGrad  
     - 6.945
     - 7.653
     - 11.507
     - 0.00%
     - -56.6% MAE
   * - GLMNet
     - 9.007
     - 9.554
     - 29.394
     - 0.00%
     - -66.5% MAE

*All improvements are statistically significant (p < 0.0001)*

Algorithm Overview
------------------

AMGD integrates three key innovations:

**1. Adaptive Learning Rate Decay**

.. math::

   \alpha_t = \frac{\alpha}{1 + \eta t}

**2. Momentum Updates with Bias Correction**

.. math::

   m_t &= \zeta_1 m_{t-1} + (1 - \zeta_1) \nabla f(\beta_t) \\
   v_t &= \zeta_2 v_{t-1} + (1 - \zeta_2) (\nabla f(\beta_t))^2 \\
   \hat{m}_t &= \frac{m_t}{1 - \zeta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \zeta_2^t}

**3. Adaptive Soft-Thresholding** *(Key Innovation)*

.. math::

   \beta_j \leftarrow \text{sign}(\beta_j) \cdot \max\left(|\beta_j| - \frac{\alpha_t \lambda}{|\beta_j| + \varepsilon}, 0\right)

This adaptive thresholding provides **coefficient-dependent regularization** that preserves large coefficients while aggressively shrinking small ones.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   user_guide
   examples/index
   
.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/core
   api/regressors
   api/utils
   
.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics
   
   theory
   benchmarks
   contributing
   changelog

.. toctree::
   :maxdepth: 1
   :caption: External Links
   
   GitHub Repository <https://github.com/yourusername/amgd-python>
   PyPI Package <https://pypi.org/project/amgd-python/>
   Research Paper <https://arxiv.org/abs/your-paper-id>

Use Cases
---------

AMGD is particularly effective for:

🧬 **Genomics & Bioinformatics**
   High-dimensional gene expression analysis, SNP association studies

🌍 **Ecological Modeling**  
   Species abundance prediction, biodiversity index modeling

📊 **Marketing Analytics**
   Customer behavior modeling, click-through rate prediction

🏥 **Epidemiology**
   Disease incidence modeling, outbreak pattern analysis

🔧 **Quality Control**
   Defect count prediction, failure rate analysis

🌐 **Network Analysis**
   Node degree modeling, traffic flow prediction

Getting Help
------------

- **Documentation**: https://amgd-python.readthedocs.io/
- **Issues**: `GitHub Issues <https://github.com/yourusername/amgd-python/issues>`_
- **Discussions**: `GitHub Discussions <https://github.com/yourusername/amgd-python/discussions>`_
- **Email**: 2020913072@ogr.cu.edu.tr

Citation
--------

If you use AMGD in your research, please cite:

.. code-block:: bibtex

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

License
-------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/yourusername/amgd-python/blob/main/LICENSE>`_ file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

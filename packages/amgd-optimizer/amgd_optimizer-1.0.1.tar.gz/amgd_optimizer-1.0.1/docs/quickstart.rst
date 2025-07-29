Quick Start Guide
=================

Basic Example
-------------

.. code-block:: python

   import numpy as np
   from amgd import AMGDPoissonRegressor

   # Generate sample data
   X = np.random.randn(100, 10)
   y = np.random.poisson(np.exp(X @ np.random.randn(10)))

   # Fit model
   model = AMGDPoissonRegressor(alpha=0.01, l1_ratio=0.7)
   model.fit(X, y)

   # Make predictions
   predictions = model.predict(X)
   print(f"Sparsity: {model.get_sparsity():.2%}")

Feature Selection Example
-------------------------

.. code-block:: python

   from amgd import quick_fit

   # Quick fitting for different penalties
   model_l1 = quick_fit(X, y, penalty='l1', alpha=0.1)
   model_en = quick_fit(X, y, penalty='elasticnet', alpha=0.1)

   print(f"L1 sparsity: {model_l1.get_sparsity():.2%}")
   print(f"Elastic Net sparsity: {model_en.get_sparsity():.2%}")
Installation
============

Requirements
------------

- Python 3.8+
- NumPy >= 1.19.0
- Scikit-learn >= 1.0.0

Install from PyPI
-----------------

.. code-block:: bash

   pip install amgd-Optimizer

Install from Source
-------------------

.. code-block:: bash

   git clone https://github.com/elbakari01/amgd-optimizer.git
   cd amgd-python
   pip install -e .

Development Installation
------------------------

.. code-block:: bash

   git clone https://github.com/elbakari01/amgd-optimizer
   cd amgd-python
   pip install -e ".[dev,docs,examples]"

Verify Installation
-------------------

.. code-block:: python

   from amgd import validate_installation
   print(validate_installation())
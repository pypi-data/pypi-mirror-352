AMGD Documentation
==================

AMGD (Adaptive Momentum Gradient Descent) is a Python package for high-dimensional sparse Poisson regression with L1 and Elastic Net regularization.

.. toctree::
   :maxdepth: 2

   installation
   tutorial
   benchmarks
   theory
   api
   contributing

Features
--------

* **Efficient optimization** for Poisson regression with adaptive momentum
* **Automatic feature selection** through L1 and Elastic Net penalties  
* **Superior performance** compared to Adam, AdaGrad, and GLMnet
* **Built-in benchmarking** tools for algorithm comparison
* **Comprehensive visualization** for convergence and coefficient paths

Installation
------------

.. code-block:: bash

   pip install amgd

Quick Example
-------------

.. code-block:: python

   from amgd.models import PoissonRegressor
   
   # Create model
   model = PoissonRegressor(
       optimizer='amgd',
       penalty='l1',
       lambda1=0.1
   )
   
   # Fit model
   model.fit(X_train, y_train)
   
   # Make predictions
   y_pred = model.predict(X_test)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
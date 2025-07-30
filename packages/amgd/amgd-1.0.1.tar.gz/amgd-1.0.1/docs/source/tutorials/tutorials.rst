Tutorial
========

Basic Usage
-----------

Here’s how to use AMGD for Poisson regression:

.. code-block:: python

    from amgd.models import PoissonRegressor
    from sklearn.model_selection import train_test_split

    # Prepare your data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Create and train model
    model = PoissonRegressor(
        optimizer='amgd',
        penalty='l1',
        lambda1=0.1,
        max_iter=1000
    )
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate
    score = model.score(X_test, y_test)
    print(f"Test score: {score:.4f}")
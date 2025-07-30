"""
Reproduce the ecological health analysis from the paper.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from amgd.models import PoissonRegressor
from amgd.benchmarks import compare_optimizers
from amgd.visualization import plot_coefficient_path, plot_feature_importance


def main():
    # Note: This example assumes you have the ecological dataset
    # If not available, it will use synthetic data
    
    try:
        from amgd.benchmarks.datasets import load_ecological_dataset
        print("Loading ecological health dataset...")
        X, y, feature_names = load_ecological_dataset()
        print(f"Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features")
    except FileNotFoundError:
        print("Ecological dataset not found. Using synthetic data instead...")
        from amgd.benchmarks.datasets import generate_synthetic_poisson_data
        X, y, true_coef = generate_synthetic_poisson_data(
            n_samples=5000,
            n_features=50,
            n_informative=15,
            sparsity=0.7,
            random_state=42
        )
        feature_names = [f"Feature_{i}" for i in range(X.shape[1])]
    
    # Split data (70/15/15 as in the paper)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.1765, random_state=42  # 0.15/0.85
    )
    
    print(f"\nData splits:")
    print(f"Training: {X_train.shape[0]} samples")
    print(f"Validation: {X_val.shape[0]} samples")
    print(f"Test: {X_test.shape[0]} samples")
    
    # Hyperparameter tuning using validation set
    print("\nPerforming hyperparameter tuning...")
    lambda_values = np.logspace(-4, np.log10(20), 50)
    
    best_lambda = None
    best_score = float('inf')
    scores = []
    
    for lambda_val in lambda_values:
        model = PoissonRegressor(
            optimizer='amgd',
            penalty='l1',
            lambda1=lambda_val,
            max_iter=500,
            verbose=False
        )
        model.fit(X_train, y_train)
        
        # Evaluate on validation set
        val_score = -model.score(X_val, y_val)  # Negative because score returns negative deviance
        scores.append(val_score)
        
        if val_score < best_score:
            best_score = val_score
            best_lambda = lambda_val
    
    print(f"Best lambda: {best_lambda:.6f}")
    print(f"Best validation score: {best_score:.4f}")
    
    # Train final model with best parameters
    print("\nTraining final model...")
    final_model = PoissonRegressor(
        optimizer='amgd',
        penalty='l1',
        lambda1=best_lambda,
        max_iter=1000,
        verbose=True
    )
    
    # Use full training + validation for final model
    X_train_full = np.vstack([X_train, X_val])
    y_train_full = np.concatenate([y_train, y_val])
    
    final_model.fit(X_train_full, y_train_full)
    
    # Evaluate on test set
    test_score = final_model.score(X_test, y_test)
    print(f"\nTest score (negative deviance): {test_score:.4f}")
    
    # Feature analysis
    n_nonzero = np.sum(np.abs(final_model.coef_) > 1e-6)
    print(f"\nSelected features: {n_nonzero}/{len(final_model.coef_)}")
    
    # Plot coefficient path
    print("\nCreating coefficient path plot...")
    
    # Train models for different lambda values to show path
    coefficients = []
    for lambda_val in lambda_values:
        model = PoissonRegressor(
            optimizer='amgd',
            penalty='l1',
            lambda1=lambda_val,
            max_iter=200,
            verbose=False
        )
        model.fit(X_train, y_train)
        coefficients.append(model.coef_)
    
    coefficients = np.array(coefficients)
    
    fig = plot_coefficient_path(
        lambda_values,
        coefficients,
        feature_names=feature_names,
        top_k=15,
        title="Coefficient Path for Ecological Health Data"
    )
    plt.show()
    
    # Feature importance plot
    fig2 = plot_feature_importance(
        final_model.coef_,
        feature_names=feature_names,
        top_k=20,
        title="Top 20 Important Features for Biodiversity Prediction"
    )
    plt.show()
    
    # Compare with other methods
    print("\nComparing with other optimization methods...")
    comparison_results = compare_optimizers(
        X_train_full, y_train_full,
        optimizers=['amgd', 'adam', 'adagrad'],
        penalties=['l1', 'elasticnet'],
        lambda_values=lambda_values[::5],  # Use subset for speed
        cv_folds=5,
        test_size=0.2,
        verbose=False
    )
    
    print("\nOptimizer comparison on test set:")
    # Evaluate each best model on test set
    for opt_name, model in comparison_results['models'].items():
        test_score = model.score(X_test, y_test)
        sparsity = 1 - np.sum(np.abs(model.coef_) > 1e-6) / len(model.coef_)
        print(f"{opt_name}: score={test_score:.4f}, sparsity={sparsity:.2%}")


if __name__ == "__main__":
    main()
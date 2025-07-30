"""
Basic usage example for AMGD package.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from amgd.models import PoissonRegressor
from amgd.benchmarks.datasets import generate_synthetic_poisson_data
from amgd.visualization import plot_convergence, plot_feature_importance


def main():
    # Generate synthetic data
    print("Generating synthetic Poisson data...")
    X, y, true_coef = generate_synthetic_poisson_data(
        n_samples=1000,
        n_features=100,
        n_informative=20,
        sparsity=0.8,
        signal_strength=1.0,
        random_state=42
    )
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training samples: {X_train.shape[0]}")
    print(f"Test samples: {X_test.shape[0]}")
    print(f"Features: {X_train.shape[1]}")
    
    # Create and train model
    print("\nTraining Poisson regression with AMGD and L1 penalty...")
    model = PoissonRegressor(
        optimizer='amgd',
        penalty='l1',
        lambda1=0.1,
        max_iter=1000,
        verbose=True
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"\nTrain score (negative deviance): {train_score:.4f}")
    print(f"Test score (negative deviance): {test_score:.4f}")
    
    # Check sparsity
    n_nonzero = np.sum(np.abs(model.coef_) > 1e-6)
    sparsity = 1 - n_nonzero / len(model.coef_)
    print(f"\nSparsity: {sparsity:.2%}")
    print(f"Non-zero coefficients: {n_nonzero}/{len(model.coef_)}")
    
    # Visualizations
    print("\nCreating visualizations...")
    
    # Plot convergence
    fig1 = plot_convergence(
        model.loss_history_,
        title="AMGD Convergence",
        log_scale=True
    )
    plt.show()
    
    # Plot feature importance
    fig2 = plot_feature_importance(
        model.coef_,
        top_k=20,
        title="Top 20 Feature Importance"
    )
    plt.show()
    
    # Compare with true coefficients if available
    print("\nComparing with true coefficients...")
    
    # Find indices of true non-zero coefficients
    true_nonzero = np.where(np.abs(true_coef) > 1e-6)[0]
    pred_nonzero = np.where(np.abs(model.coef_) > 1e-6)[0]
    
    # Calculate selection accuracy
    true_positives = len(set(true_nonzero) & set(pred_nonzero))
    false_positives = len(set(pred_nonzero) - set(true_nonzero))
    false_negatives = len(set(true_nonzero) - set(pred_nonzero))
    
    precision = true_positives / (true_positives + false_positives) if pred_nonzero.size > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if true_nonzero.size > 0 else 0
    
    print(f"Feature selection precision: {precision:.2%}")
    print(f"Feature selection recall: {recall:.2%}")


if __name__ == "__main__":
    main()
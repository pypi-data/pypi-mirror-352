"""
Example usage of AMGD for Penalized Poisson Regression.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import PoissonRegressor

# Import AMGD implementation
from amgd import PenalizedPoissonRegression

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# matplotlib style
plt.style.use('ggplot')

def generate_synthetic_data(n_samples=1000, n_features=20, n_informative=5, 
                           sparsity=0.8, random_state=None):
    """
    Generate synthetic Poisson regression data with sparse coefficients.
    
    Parameters:
    -----------
    n_samples : int, default=1000
        Number of samples
    n_features : int, default=20
        Number of features
    n_informative : int, default=5
        Number of informative features
    sparsity : float, default=0.8
        Target sparsity level (proportion of zero coefficients)
    random_state : int, default=None
        Random seed
        
    Returns:
    --------
    X : ndarray, shape (n_samples, n_features)
        Feature matrix
    y : ndarray, shape (n_samples,)
        Target vector
    true_coef : ndarray, shape (n_features,)
        True coefficient vector
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate feature matrix
    X = np.random.randn(n_samples, n_features)
    
    # Generate sparse coefficient vector
    true_coef = np.zeros(n_features)
    informative_idx = np.random.choice(n_features, n_informative, replace=False)
    true_coef[informative_idx] = np.random.uniform(0.5, 2.0, n_informative) * np.random.choice([-1, 1], n_informative)
    
    # Generate linear predictor and count data
    linear_pred = X @ true_coef
    y = np.random.poisson(np.exp(linear_pred))
    
    return X, y, true_coef

def plot_results(amgd_model, sk_model, X_test, y_test, true_coef):
    """
    Plot comparison of AMGD and scikit-learn models.
    
    Parameters:
    -----------
    amgd_model : PenalizedPoissonRegression
        Fitted AMGD Poisson regression model
    sk_model : PoissonRegressor
        Fitted scikit-learn Poisson regression model
    X_test : ndarray
        Test feature matrix
    y_test : ndarray
        Test target vector
    true_coef : ndarray
        True coefficient vector
    """
    # Get predictions
    y_pred_amgd = amgd_model.predict(X_test)
    y_pred_sk = sk_model.predict(X_test)
    
    # Get coefficients
    amgd_coef = amgd_model.coef_
    sk_coef = sk_model.coef_
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Predictions comparison
    axes[0].scatter(y_test, y_pred_amgd, alpha=0.5, label='AMGD')
    axes[0].scatter(y_test, y_pred_sk, alpha=0.5, label='Scikit-learn')
    axes[0].plot([0, max(y_test)], [0, max(y_test)], 'k--', label='Perfect prediction')
    axes[0].set_xlabel('True counts')
    axes[0].set_ylabel('Predicted counts')
    axes[0].set_title('Model Predictions')
    axes[0].legend()
    
    # 2. Coefficient comparison
    axes[1].bar(np.arange(len(true_coef)) - 0.2, true_coef, width=0.2, label='True', alpha=0.7)
    axes[1].bar(np.arange(len(true_coef)), amgd_coef, width=0.2, label='AMGD', alpha=0.7)
    axes[1].bar(np.arange(len(true_coef)) + 0.2, sk_coef, width=0.2, label='Scikit-learn', alpha=0.7)
    axes[1].set_xlabel('Feature index')
    axes[1].set_ylabel('Coefficient value')
    axes[1].set_title('Coefficient Comparison')
    axes[1].legend()
    
    # 3. Optimization trajectory (loss history)
    stats = amgd_model.get_optimization_stats()
    axes[2].plot(stats['loss_history'])
    axes[2].set_xlabel('Iteration')
    axes[2].set_ylabel('Loss')
    axes[2].set_title('AMGD Optimization Trajectory')
    
    plt.tight_layout()
    plt.savefig('poisson_comparison.png')
    plt.show()

def main():
    """Run the example."""
    print("Generating synthetic data...")
    X, y, true_coef = generate_synthetic_data(n_samples=1000, n_features=20, 
                                             n_informative=5, random_state=RANDOM_SEED)
    
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Fit AMGD Poisson regression model
    print("\nFitting AMGD Poisson regression model...")
    amgd_start = time.time()
    amgd_model = PenalizedPoissonRegression(
        alpha=0.01,
        lambda1=0.1,
        penalty='l1',
        max_iter=1000,
        verbose=True,
        random_state=RANDOM_SEED
    )
    amgd_model.fit(X_train_scaled, y_train)
    amgd_time = time.time() - amgd_start
    
    # Fit scikit-learn Poisson regression model for comparison
    print("\nFitting scikit-learn Poisson regression model...")
    sk_start = time.time()
    sk_model = PoissonRegressor(
        alpha=0.1,
        max_iter=1000,
        tol=1e-6
    )
    sk_model.fit(X_train_scaled, y_train)
    sk_time = time.time() - sk_start
    
    # Evaluate models
    amgd_
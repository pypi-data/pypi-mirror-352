"""
Benchmark datasets for testing optimization algorithms.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, Any
from sklearn.preprocessing import StandardScaler
import os


def generate_synthetic_poisson_data(
    n_samples: int = 1000,
    n_features: int = 100,
    n_informative: int = 10,
    sparsity: float = 0.9,
    signal_strength: float = 1.0,
    noise_level: float = 0.1,
    random_state: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic data for Poisson regression.
    
    Parameters
    ----------
    n_samples : int
        Number of samples.
    n_features : int
        Total number of features.
    n_informative : int
        Number of informative features.
    sparsity : float
        Proportion of zero coefficients.
    signal_strength : float
        Strength of non-zero coefficients.
    noise_level : float
        Amount of noise to add.
    random_state : int or None
        Random seed.
        
    Returns
    -------
    X : ndarray of shape (n_samples, n_features)
        Feature matrix.
    y : ndarray of shape (n_samples,)
        Count outcomes.
    true_coef : ndarray of shape (n_features,)
        True coefficient values.
    """
    if random_state is not None:
        np.random.seed(random_state)
        
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Generate sparse coefficients
    true_coef = np.zeros(n_features)
    informative_indices = np.random.choice(n_features, n_informative, replace=False)
    true_coef[informative_indices] = np.random.randn(n_informative) * signal_strength
    
    # Apply additional sparsity
    n_zeros = int(n_informative * sparsity)
    if n_zeros > 0:
        zero_indices = np.random.choice(informative_indices, n_zeros, replace=False)
        true_coef[zero_indices] = 0
        
    # Generate Poisson response
    linear_pred = X @ true_coef
    
    # Add noise
    if noise_level > 0:
        linear_pred += np.random.randn(n_samples) * noise_level
        
    # Clip for numerical stability
    linear_pred = np.clip(linear_pred, -10, 10)
    
    # Generate counts from Poisson distribution
    mu = np.exp(linear_pred)
    y = np.random.poisson(mu)
    
    return X, y, true_coef





def load_ecological_dataset(filepath: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray, list]:
    """
    Load the ecological health dataset used in the paper.
    
    Parameters
    ----------
    filepath : str or None
        Path to the dataset. If None, uses default location.
        
    Returns
    -------
    X : ndarray of shape (n_samples, n_features)
        Feature matrix.
    y : ndarray of shape (n_samples,)
        Biodiversity index (count data).
    feature_names : list
        Names of features.
    """
    if filepath is None:
        # Try to find in package data directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(package_dir, '..', 'data', 'ecological_health_dataset.csv')
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. "
            "Please provide the correct path or use generate_synthetic_poisson_data()."
        )
        
    # Load data
    df = pd.read_csv(filepath)
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    # Separate features and target
    target_col = 'Biodiversity_Index'
    feature_cols = [col for col in df.columns if col != target_col and col != 'Timestamp']
    
    # Handle categorical variables if any
    categorical_cols = df[feature_cols].select_dtypes(include=['object']).columns
    
    if len(categorical_cols) > 0:
        # One-hot encode categorical variables
        df_encoded = pd.get_dummies(df[feature_cols], columns=categorical_cols, drop_first=True)
        feature_names = list(df_encoded.columns)
        X = df_encoded.values
    else:
        feature_names = feature_cols
        X = df[feature_cols].values
        
    y = df[target_col].values
    
    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    return X, y, feature_names


def get_benchmark_datasets() -> Dict[str, Dict[str, Any]]:
    """
    Get a collection of benchmark datasets for testing.
    
    Returns
    -------
    datasets : dict
        Dictionary of dataset names to dataset information.
    """
    datasets = {}
    
    # Synthetic datasets with varying properties
    synthetic_configs = [
        {
            'name': 'synthetic_small_dense',
            'n_samples': 500,
            'n_features': 50,
            'n_informative': 20,
            'sparsity': 0.3,
            'description': 'Small dataset with dense coefficients'
        },
        {
            'name': 'synthetic_large_sparse',
            'n_samples': 2000,
            'n_features': 500,
            'n_informative': 50,
            'sparsity': 0.9,
            'description': 'Large dataset with sparse coefficients'
        },
        {
            'name': 'synthetic_high_dim',
            'n_samples': 100,
            'n_features': 1000,
            'n_informative': 10,
            'sparsity': 0.95,
            'description': 'High-dimensional dataset (p >> n)'
        },
        {
            'name': 'synthetic_low_noise',
            'n_samples': 1000,
            'n_features': 100,
            'n_informative': 30,
            'sparsity': 0.7,
            'noise_level': 0.01,
            'description': 'Dataset with low noise level'
        },
        {
            'name': 'synthetic_high_noise',
            'n_samples': 1000,
            'n_features': 100,
            'n_informative': 30,
            'sparsity': 0.7,
            'noise_level': 0.5,
            'description': 'Dataset with high noise level'
        }
    ]
    
    # Generate synthetic datasets
    for config in synthetic_configs:
        name = config.pop('name')
        description = config.pop('description')
        
        X, y, true_coef = generate_synthetic_poisson_data(**config, random_state=42)
        
        datasets[name] = {
            'X': X,
            'y': y,
            'true_coef': true_coef,
            'description': description,
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'type': 'synthetic'
        }
        
    # Try to load real datasets
    try:
        X_eco, y_eco, feature_names = load_ecological_dataset()
        datasets['ecological_health'] = {
            'X': X_eco,
            'y': y_eco,
            'feature_names': feature_names,
            'description': 'Ecological health dataset from the paper',
            'n_samples': X_eco.shape[0],
            'n_features': X_eco.shape[1],
            'type': 'real'
        }
    except FileNotFoundError:
        pass
        
    return datasets
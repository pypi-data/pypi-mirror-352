"""
Data preprocessing utilities.
"""

import numpy as np
from typing import Optional


class StandardScaler:
    """
    Standardize features by removing mean and scaling to unit variance.
    
    Attributes
    ----------
    mean_ : ndarray of shape (n_features,)
        Per-feature mean.
    scale_ : ndarray of shape (n_features,)
        Per-feature standard deviation.
    """
    
    def __init__(self):
        self.mean_ = None
        self.scale_ = None
        
    def fit(self, X):
        """
        Compute mean and standard deviation.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data to compute mean and standard deviation.
            
        Returns
        -------
        self : object
            Fitted scaler.
        """
        X = np.asarray(X)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        # Avoid division by zero
        self.scale_[self.scale_ == 0] = 1.0
        return self
        
    def transform(self, X):
        """
        Standardize features.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data to standardize.
            
        Returns
        -------
        X_scaled : ndarray of shape (n_samples, n_features)
            Standardized data.
        """
        if self.mean_ is None or self.scale_ is None:
            raise ValueError("Scaler has not been fitted. Call fit() first.")
            
        X = np.asarray(X)
        return (X - self.mean_) / self.scale_
        
    def fit_transform(self, X):
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
        
    def inverse_transform(self, X):
        """
        Reverse standardization.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Standardized data.
            
        Returns
        -------
        X_original : ndarray of shape (n_samples, n_features)
            Original scale data.
        """
        if self.mean_ is None or self.scale_ is None:
            raise ValueError("Scaler has not been fitted. Call fit() first.")
            
        X = np.asarray(X)
        return X * self.scale_ + self.mean_


def add_intercept(X, prepend: bool = True):
    """
    Add intercept column to feature matrix.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Feature matrix.
    prepend : bool
        If True, add intercept as first column. Otherwise, append.
        
    Returns
    -------
    X_with_intercept : ndarray of shape (n_samples, n_features + 1)
        Feature matrix with intercept column.
    """
    X = np.asarray(X)
    n_samples = X.shape[0]
    intercept = np.ones((n_samples, 1))
    
    if prepend:
        return np.column_stack([intercept, X])
    else:
        return np.column_stack([X, intercept])
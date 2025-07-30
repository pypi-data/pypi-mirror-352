"""
Input validation utilities.
"""

import numpy as np
from typing import Optional, Union, List
import warnings


def check_array(
    array,
    accept_sparse: bool = False,
    dtype: Optional[Union[type, List[type]]] = None,
    ensure_2d: bool = True,
    allow_nd: bool = False,
    ensure_min_samples: int = 1,
    ensure_min_features: int = 1,
    copy: bool = False
):
    """
    Input validation on an array.
    
    Parameters
    ----------
    array : array-like
        Input array to check.
    accept_sparse : bool
        Whether to accept sparse matrices.
    dtype : type or list of types, optional
        Data type(s) that result should have.
    ensure_2d : bool
        Whether to ensure array is 2D.
    allow_nd : bool
        Whether to allow n-dimensional arrays.
    ensure_min_samples : int
        Ensure array has at least this many samples.
    ensure_min_features : int
        Ensure array has at least this many features.
    copy : bool
        Whether to force a copy of the array.
        
    Returns
    -------
    array_converted : ndarray
        The converted and validated array.
    """
    # Convert to numpy array
    array = np.asarray(array)
    
    # Force copy if requested
    if copy:
        array = array.copy()
        
    # Check dimensionality
    if ensure_2d and array.ndim != 2:
        if array.ndim == 1:
            array = array.reshape(-1, 1)
        else:
            raise ValueError(f"Expected 2D array, got {array.ndim}D array instead")
            
    if not allow_nd and array.ndim > 2:
        raise ValueError(f"Found array with dim {array.ndim}. Expected <= 2")
        
    # Check dtype
    if dtype is not None:
        if not isinstance(dtype, list):
            dtype = [dtype]
        if array.dtype not in dtype:
            array = array.astype(dtype[0])
            
    # Check minimum requirements
    if array.ndim >= 1 and ensure_min_samples > 0:
        n_samples = array.shape[0]
        if n_samples < ensure_min_samples:
            raise ValueError(f"Found array with {n_samples} sample(s) while a minimum "
                           f"of {ensure_min_samples} is required")
                           
    if array.ndim >= 2 and ensure_min_features > 0:
        n_features = array.shape[1]
        if n_features < ensure_min_features:
            raise ValueError(f"Found array with {n_features} feature(s) while a minimum "
                           f"of {ensure_min_features} is required")
                           
    return array


def check_consistent_length(*arrays):
    """Check that all arrays have consistent first dimensions."""
    lengths = []
    for X in arrays:
        if X is not None:
            X = np.asarray(X)
            if X.ndim > 0:
                lengths.append(X.shape[0])
                
    if len(set(lengths)) > 1:
        raise ValueError(f"Found input variables with inconsistent numbers of samples: {lengths}")


def check_is_fitted(estimator, attributes=None):
    """
    Check if estimator is fitted.
    
    Parameters
    ----------
    estimator : estimator instance
        Estimator to check.
    attributes : list of str, optional
        Attributes to check. If None, checks 'is_fitted_'.
    """
    if attributes is None:
        attributes = ['is_fitted_']
        
    if not hasattr(estimator, 'is_fitted_') or not estimator.is_fitted_:
        # Check for other common attributes
        fitted_attrs = ['coef_', 'intercept_', 'n_iter_']
        if not any(hasattr(estimator, attr) for attr in fitted_attrs):
            raise ValueError("This estimator is not fitted yet. Call 'fit' with "
                           "appropriate arguments before using this estimator.")


def validate_penalty_params(penalty: str, lambda1: float, lambda2: float):
    """
    Validate penalty parameters.
    
    Parameters
    ----------
    penalty : str
        Penalty type.
    lambda1 : float
        L1 regularization parameter.
    lambda2 : float
        L2 regularization parameter.
    """
    if lambda1 < 0:
        raise ValueError(f"lambda1 must be non-negative, got {lambda1}")
        
    if lambda2 < 0:
        raise ValueError(f"lambda2 must be non-negative, got {lambda2}")
        
    penalty_lower = penalty.lower()
    
    if penalty_lower == 'l1' and lambda2 > 0:
        warnings.warn("lambda2 > 0 but penalty='l1'. lambda2 will be ignored.")
        
    if penalty_lower == 'l2' and lambda1 > 0:
        warnings.warn("lambda1 > 0 but penalty='l2'. lambda1 will be ignored.")
        
    if penalty_lower == 'none' and (lambda1 > 0 or lambda2 > 0):
        warnings.warn("Regularization parameters specified but penalty='none'. "
                     "They will be ignored.")
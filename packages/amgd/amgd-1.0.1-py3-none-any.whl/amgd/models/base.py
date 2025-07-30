"""
Base classes for statistical models.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from sklearn.base import BaseEstimator as SKBaseEstimator

from amgd.core.optimizer import OptimizerBase, AMGDOptimizer
from amgd.core.penalties import PenaltyBase, create_penalty
from amgd.utils.validation import check_array, check_consistent_length, check_is_fitted


class BaseEstimator(SKBaseEstimator):
    """Base estimator class with scikit-learn compatibility."""
    
    def __init__(self):
        self.is_fitted_ = False
        
    def _check_is_fitted(self):
        """Check if estimator is fitted."""
        check_is_fitted(self)
        
    def _validate_data(self, X, y=None, reset=True):
        """Validate input data."""
        X = check_array(X, accept_sparse=True)
        
        if y is not None:
            y = check_array(y, ensure_2d=False)
            check_consistent_length(X, y)
            
        if reset:
            self._reset()
            
        return X, y if y is not None else X
        
    def _reset(self):
        """Reset internal state."""
        if hasattr(self, 'coef_'):
            del self.coef_
        if hasattr(self, 'intercept_'):
            del self.intercept_
        self.is_fitted_ = False


class BaseGLM(BaseEstimator, ABC):
    """
    Base class for Generalized Linear Models.
    
    Parameters
    ----------
    optimizer : str or OptimizerBase, default='amgd'
        Optimization algorithm. Can be 'amgd', 'adam', 'adagrad', or custom optimizer.
    penalty : str, default='none'
        Regularization penalty: 'l1', 'l2', 'elasticnet', or 'none'.
    lambda1 : float, default=0.0
        L1 regularization strength.
    lambda2 : float, default=0.0
        L2 regularization strength.
    fit_intercept : bool, default=True
        Whether to fit an intercept term.
    max_iter : int, default=1000
        Maximum number of optimization iterations.
    tol : float, default=1e-6
        Tolerance for convergence.
    warm_start : bool, default=False
        Whether to reuse previous solution as initialization.
    verbose : bool, default=False
        Whether to print progress.
    random_state : int or None, default=None
        Random seed for reproducibility.
    """
    
    def __init__(
        self,
        optimizer: Union[str, OptimizerBase] = 'amgd',
        penalty: str = 'none',
        lambda1: float = 0.0,
        lambda2: float = 0.0,
        fit_intercept: bool = True,
        max_iter: int = 1000,
        tol: float = 1e-6,
        warm_start: bool = False,
        verbose: bool = False,
        random_state: Optional[int] = None,
        **optimizer_params
    ):
        super().__init__()
        self.optimizer = optimizer
        self.penalty = penalty
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.fit_intercept = fit_intercept
        self.max_iter = max_iter
        self.tol = tol
        self.warm_start = warm_start
        self.verbose = verbose
        self.random_state = random_state
        self.optimizer_params = optimizer_params
        
    def _create_optimizer(self) -> OptimizerBase:
        """Create optimizer instance."""
        if isinstance(self.optimizer, OptimizerBase):
            return self.optimizer
            
        optimizer_name = self.optimizer.lower()
        
        # Default optimizer parameters
        params = {
            'max_iter': self.max_iter,
            'tol': self.tol,
            'verbose': self.verbose,
            'random_state': self.random_state,
        }
        params.update(self.optimizer_params)
        
        if optimizer_name == 'amgd':
            return AMGDOptimizer(**params)
        elif optimizer_name == 'adam':
            from amgd.core.optimizer import AdamOptimizer
            return AdamOptimizer(**params)
        elif optimizer_name == 'adagrad':
            from amgd.core.optimizer import AdaGradOptimizer
            return AdaGradOptimizer(**params)
        else:
            raise ValueError(f"Unknown optimizer: {self.optimizer}")
            
    def _create_penalty(self) -> PenaltyBase:
        """Create penalty object."""
        return create_penalty(self.penalty, self.lambda1, self.lambda2)
        
    @abstractmethod
    def _compute_loss(self, X: np.ndarray, y: np.ndarray, coef: np.ndarray) -> float:
        """Compute loss function value."""
        pass
        
    @abstractmethod
    def _compute_gradient(self, X: np.ndarray, y: np.ndarray, coef: np.ndarray) -> np.ndarray:
        """Compute loss gradient."""
        pass
        
    def fit(self, X, y):
        """
        Fit the model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
            
        Returns
        -------
        self : object
            Fitted estimator.
        """
        X, y = self._validate_data(X, y, reset=not self.warm_start)
        n_samples, n_features = X.shape
        
        # Add intercept column if needed
        if self.fit_intercept:
            X = np.column_stack([np.ones(n_samples), X])
            n_features += 1
            
        # Initialize coefficients
        if self.warm_start and hasattr(self, 'coef_'):
            if self.fit_intercept:
                coef_init = np.concatenate([[self.intercept_], self.coef_])
            else:
                coef_init = self.coef_.copy()
        else:
            coef_init = np.random.normal(0, 0.1, n_features)
            
        # Create optimizer and penalty
        optimizer = self._create_optimizer()
        penalty = self._create_penalty()
        
        # Define objective and gradient functions
        def objective(coef):
            return self._compute_loss(X, y, coef)
            
        def gradient(coef):
            return self._compute_gradient(X, y, coef)
            
        # Optimize
        coef_opt, info = optimizer.minimize(
            objective,
            gradient,
            coef_init,
            penalty=penalty
        )
        
        # Store results
        if self.fit_intercept:
            self.intercept_ = coef_opt[0]
            self.coef_ = coef_opt[1:]
        else:
            self.intercept_ = 0.0
            self.coef_ = coef_opt
            
        # Store optimization info
        self.n_iter_ = info['n_iter']
        self.loss_history_ = info['loss_history']
        self.optimization_info_ = info
        self.is_fitted_ = True
        
        return self
        
    @abstractmethod
    def predict(self, X):
        """Make predictions."""
        pass
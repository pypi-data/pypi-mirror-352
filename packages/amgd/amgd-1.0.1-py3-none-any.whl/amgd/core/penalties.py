"""
Regularization penalties for sparse optimization.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional


class PenaltyBase(ABC):
    """Base class for regularization penalties."""
    
    @abstractmethod
    def __call__(self, x: np.ndarray) -> float:
        """Compute penalty value."""
        pass
        
    @abstractmethod
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute penalty gradient."""
        pass
        
    @abstractmethod
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Apply proximal operator for the penalty."""
        pass


class L1Penalty(PenaltyBase):
    """L1 (Lasso) penalty."""
    
    def __init__(self, lambda1: float = 1.0):
        """
        Parameters
        ----------
        lambda1 : float
            L1 regularization strength.
        """
        self.lambda1 = lambda1
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute L1 penalty value."""
        return self.lambda1 * np.sum(np.abs(x))
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute L1 penalty subgradient."""
        return self.lambda1 * np.sign(x)
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Soft-thresholding operator."""
        threshold = self.lambda1 * step_size
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)


class L2Penalty(PenaltyBase):
    """L2 (Ridge) penalty."""
    
    def __init__(self, lambda2: float = 1.0):
        """
        Parameters
        ----------
        lambda2 : float
            L2 regularization strength.
        """
        self.lambda2 = lambda2
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute L2 penalty value."""
        return 0.5 * self.lambda2 * np.sum(x ** 2)
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute L2 penalty gradient."""
        return self.lambda2 * x
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """L2 proximal operator."""
        return x / (1 + self.lambda2 * step_size)


class ElasticNetPenalty(PenaltyBase):
    """Elastic Net penalty (combination of L1 and L2)."""
    
    def __init__(self, lambda1: float = 1.0, lambda2: float = 1.0):
        """
        Parameters
        ----------
        lambda1 : float
            L1 regularization strength.
        lambda2 : float
            L2 regularization strength.
        """
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.l1_penalty = L1Penalty(lambda1)
        self.l2_penalty = L2Penalty(lambda2)
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute Elastic Net penalty value."""
        return self.l1_penalty(x) + self.l2_penalty(x)
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute Elastic Net penalty gradient."""
        return self.l1_penalty.gradient(x) + self.l2_penalty.gradient(x)
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Elastic Net proximal operator."""
        # First apply L2 proximal operator
        x_l2 = self.l2_penalty.proximal_operator(x, step_size)
        # Then apply L1 proximal operator
        return self.l1_penalty.proximal_operator(x_l2, step_size)


class NonePenalty(PenaltyBase):
    """No penalty (unregularized)."""
    
    def __call__(self, x: np.ndarray) -> float:
        """No penalty."""
        return 0.0
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Zero gradient."""
        return np.zeros_like(x)
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Identity operator."""
        return x


def create_penalty(penalty_type: str, lambda1: float = 0.0, lambda2: float = 0.0) -> PenaltyBase:
    """
    Create penalty object from string specification.
    
    Parameters
    ----------
    penalty_type : str
        Type of penalty: 'l1', 'l2', 'elasticnet', or 'none'.
    lambda1 : float
        L1 regularization strength.
    lambda2 : float
        L2 regularization strength.
        
    Returns
    -------
    penalty : PenaltyBase
        Penalty object.
    """
    penalty_type = penalty_type.lower()
    
    if penalty_type == 'l1':
        return L1Penalty(lambda1)
    elif penalty_type == 'l2':
        return L2Penalty(lambda2)
    elif penalty_type == 'elasticnet':
        return ElasticNetPenalty(lambda1, lambda2)
    elif penalty_type == 'none':
        return NonePenalty()
    else:
        raise ValueError(f"Unknown penalty type: {penalty_type}")
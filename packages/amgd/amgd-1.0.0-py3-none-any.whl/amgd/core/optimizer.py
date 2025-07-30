"""
Core optimization algorithms including AMGD, Adam, and AdaGrad.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, Callable
from abc import ABC, abstractmethod
import time

from amgd.core.penalties import PenaltyBase, L1Penalty, ElasticNetPenalty
from amgd.core.convergence import ConvergenceCriterion, RelativeChangeCriterion
from amgd.utils.validation import check_array, check_consistent_length


class OptimizerBase(ABC):
    """Base class for all optimizers."""
    
    def __init__(
        self,
        alpha: float = 0.01,
        max_iter: int = 1000,
        tol: float = 1e-6,
        verbose: bool = False,
        random_state: Optional[int] = None
    ):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.verbose = verbose
        self.random_state = random_state
        
        # Track optimization history
        self.loss_history_ = []
        self.gradient_norm_history_ = []
        self.n_iter_ = 0
        self.converged_ = False
        
    @abstractmethod
    def minimize(
        self,
        objective_fn: Callable,
        gradient_fn: Callable,
        x0: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Minimize the objective function."""
        pass
        
    def _initialize_state(self, n_features: int) -> None:
        """Initialize optimizer state variables."""
        if self.random_state is not None:
            np.random.seed(self.random_state)
            

class AMGDOptimizer(OptimizerBase):
    """
    Adaptive Momentum Gradient Descent optimizer.
    
    This optimizer combines adaptive learning rates with momentum and
    specialized soft-thresholding for sparse regularization.
    
    Parameters
    ----------
    alpha : float, default=0.01
        Initial learning rate.
    beta1 : float, default=0.9
        Exponential decay rate for first moment estimates.
    beta2 : float, default=0.999
        Exponential decay rate for second moment estimates.
    T : float, default=20.0
        Gradient clipping threshold.
    eta : float, default=0.0001
        Learning rate decay parameter.
    epsilon : float, default=1e-8
        Small constant for numerical stability.
    max_iter : int, default=1000
        Maximum number of iterations.
    tol : float, default=1e-6
        Tolerance for convergence.
    verbose : bool, default=False
        Whether to print progress messages.
    random_state : int or None, default=None
        Random seed for reproducibility.
    """
    
    def __init__(
        self,
        alpha: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        T: float = 20.0,
        eta: float = 0.0001,
        epsilon: float = 1e-8,
        max_iter: int = 1000,
        tol: float = 1e-6,
        verbose: bool = False,
        random_state: Optional[int] = None
    ):
        super().__init__(alpha, max_iter, tol, verbose, random_state)
        self.beta1 = beta1
        self.beta2 = beta2
        self.T = T
        self.eta = eta
        self.epsilon = epsilon
        
    def minimize(
        self,
        objective_fn: Callable,
        gradient_fn: Callable,
        x0: np.ndarray,
        penalty: Optional[PenaltyBase] = None,
        convergence_criterion: Optional[ConvergenceCriterion] = None,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Minimize objective function using AMGD.
        
        Parameters
        ----------
        objective_fn : callable
            Objective function to minimize.
        gradient_fn : callable
            Function that computes gradient of objective.
        x0 : ndarray
            Initial parameter values.
        penalty : PenaltyBase or None
            Regularization penalty.
        convergence_criterion : ConvergenceCriterion or None
            Custom convergence criterion.
        callback : callable or None
            Function called after each iteration.
            
        Returns
        -------
        x : ndarray
            Optimized parameters.
        info : dict
            Optimization information including history.
        """
        # Initialize
        n_features = len(x0)
        x = x0.copy()
        
        # Initialize momentum variables
        m = np.zeros(n_features)
        v = np.zeros(n_features)
        
        # Initialize convergence criterion
        if convergence_criterion is None:
            convergence_criterion = RelativeChangeCriterion(tol=self.tol)
            
        # Tracking
        self.loss_history_ = []
        self.gradient_norm_history_ = []
        nonzero_history = []
        start_time = time.time()
        
        # Optimization loop
        for t in range(1, self.max_iter + 1):
            # Adaptive learning rate
            alpha_t = self.alpha / (1 + self.eta * t)
            
            # Compute gradient
            grad = gradient_fn(x)
            
            # Gradient clipping
            grad = np.clip(grad, -self.T, self.T)
            
            # Update momentum
            m = self.beta1 * m + (1 - self.beta1) * grad
            v = self.beta2 * v + (1 - self.beta2) * (grad ** 2)
            
            # Bias correction
            m_hat = m / (1 - self.beta1 ** t)
            v_hat = v / (1 - self.beta2 ** t)
            
            # Parameter update
            x = x - alpha_t * m_hat / (np.sqrt(v_hat) + self.epsilon)
            
            # Apply penalty (soft-thresholding for L1/ElasticNet)
            if penalty is not None:
                if isinstance(penalty, (L1Penalty, ElasticNetPenalty)):
                    # Adaptive soft-thresholding
                    denom = np.abs(x) + 0.1
                    threshold = alpha_t * penalty.lambda1 / denom
                    x = np.sign(x) * np.maximum(np.abs(x) - threshold, 0)
                    
            # Compute loss
            loss = objective_fn(x)
            if penalty is not None:
                loss += penalty(x)
                
            # Track progress
            self.loss_history_.append(loss)
            self.gradient_norm_history_.append(np.linalg.norm(grad))
            nonzero_history.append(np.sum(np.abs(x) > 1e-6))
            
            # Callback
            if callback is not None:
                callback(x, t, loss)
                
            # Verbose output
            if self.verbose and t % 100 == 0:
                print(f"Iteration {t}: Loss = {loss:.6f}, "
                      f"||grad|| = {np.linalg.norm(grad):.6f}, "
                      f"Non-zero = {nonzero_history[-1]}")
                      
            # Check convergence
            if convergence_criterion.check(self.loss_history_, x):
                self.converged_ = True
                self.n_iter_ = t
                if self.verbose:
                    print(f"Converged at iteration {t}")
                break
                
        # Final info
        runtime = time.time() - start_time
        info = {
            'converged': self.converged_,
            'n_iter': self.n_iter_ if self.converged_ else self.max_iter,
            'loss_history': np.array(self.loss_history_),
            'gradient_norm_history': np.array(self.gradient_norm_history_),
            'nonzero_history': np.array(nonzero_history),
            'runtime': runtime,
            'final_loss': self.loss_history_[-1],
        }
        
        return x, info


class AdamOptimizer(OptimizerBase):
    """Adam optimizer implementation."""
    
    def __init__(
        self,
        alpha: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
        max_iter: int = 1000,
        tol: float = 1e-6,
        verbose: bool = False,
        random_state: Optional[int] = None
    ):
        super().__init__(alpha, max_iter, tol, verbose, random_state)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        
    def minimize(
        self,
        objective_fn: Callable,
        gradient_fn: Callable,
        x0: np.ndarray,
        penalty: Optional[PenaltyBase] = None,
        convergence_criterion: Optional[ConvergenceCriterion] = None,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Minimize using Adam optimizer."""
        # Initialize
        n_features = len(x0)
        x = x0.copy()
        
        # Initialize moment estimates
        m = np.zeros(n_features)
        v = np.zeros(n_features)
        
        # Initialize convergence criterion
        if convergence_criterion is None:
            convergence_criterion = RelativeChangeCriterion(tol=self.tol)
            
        # Tracking
        self.loss_history_ = []
        self.gradient_norm_history_ = []
        nonzero_history = []
        start_time = time.time()
        
        # Optimization loop
        for t in range(1, self.max_iter + 1):
            # Compute gradient
            grad = gradient_fn(x)
            
            # Update biased moment estimates
            m = self.beta1 * m + (1 - self.beta1) * grad
            v = self.beta2 * v + (1 - self.beta2) * (grad ** 2)
            
            # Compute bias-corrected moment estimates
            m_hat = m / (1 - self.beta1 ** t)
            v_hat = v / (1 - self.beta2 ** t)
            
            # Update parameters
            x = x - self.alpha * m_hat / (np.sqrt(v_hat) + self.epsilon)
            
            # Apply penalty if needed
            if penalty is not None and isinstance(penalty, (L1Penalty, ElasticNetPenalty)):
                # Soft thresholding for L1 component
                x = np.sign(x) * np.maximum(np.abs(x) - penalty.lambda1 * self.alpha, 0)
                
            # Compute loss
            loss = objective_fn(x)
            if penalty is not None:
                loss += penalty(x)
                
            # Track progress
            self.loss_history_.append(loss)
            self.gradient_norm_history_.append(np.linalg.norm(grad))
            nonzero_history.append(np.sum(np.abs(x) > 1e-6))
            
            # Callback
            if callback is not None:
                callback(x, t, loss)
                
            # Verbose output
            if self.verbose and t % 100 == 0:
                print(f"Iteration {t}: Loss = {loss:.6f}, "
                      f"||grad|| = {np.linalg.norm(grad):.6f}")
                      
            # Check convergence
            if convergence_criterion.check(self.loss_history_, x):
                self.converged_ = True
                self.n_iter_ = t
                if self.verbose:
                    print(f"Converged at iteration {t}")
                break
                
        # Final info
        runtime = time.time() - start_time
        info = {
            'converged': self.converged_,
            'n_iter': self.n_iter_ if self.converged_ else self.max_iter,
            'loss_history': np.array(self.loss_history_),
            'gradient_norm_history': np.array(self.gradient_norm_history_),
            'nonzero_history': np.array(nonzero_history),
            'runtime': runtime,
            'final_loss': self.loss_history_[-1],
        }
        
        return x, info


class AdaGradOptimizer(OptimizerBase):
    """AdaGrad optimizer implementation."""
    
    def __init__(
        self,
        alpha: float = 0.01,
        epsilon: float = 1e-8,
        max_iter: int = 1000,
        tol: float = 1e-6,
        verbose: bool = False,
        random_state: Optional[int] = None
    ):
        super().__init__(alpha, max_iter, tol, verbose, random_state)
        self.epsilon = epsilon
        
    def minimize(
        self,
        objective_fn: Callable,
        gradient_fn: Callable,
        x0: np.ndarray,
        penalty: Optional[PenaltyBase] = None,
        convergence_criterion: Optional[ConvergenceCriterion] = None,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Minimize using AdaGrad optimizer."""
        # Initialize
        n_features = len(x0)
        x = x0.copy()
        
        # Initialize gradient accumulator
        G = np.zeros(n_features)
        
        # Initialize convergence criterion
        if convergence_criterion is None:
            convergence_criterion = RelativeChangeCriterion(tol=self.tol)
            
        # Tracking
        self.loss_history_ = []
        self.gradient_norm_history_ = []
        nonzero_history = []
        start_time = time.time()
        
        # Optimization loop
        for t in range(1, self.max_iter + 1):
            # Compute gradient
            grad = gradient_fn(x)
            
            # Update accumulator
            G += grad ** 2
            
            # Parameter update with AdaGrad scaling
            x = x - self.alpha * grad / (np.sqrt(G) + self.epsilon)
            
            # Apply penalty if needed
            if penalty is not None and isinstance(penalty, (L1Penalty, ElasticNetPenalty)):
                # Proximal operator for L1 regularization
                x = np.sign(x) * np.maximum(
                    np.abs(x) - penalty.lambda1 * self.alpha / (np.sqrt(G) + self.epsilon), 
                    0
                )
                
            # Compute loss
            loss = objective_fn(x)
            if penalty is not None:
                loss += penalty(x)
                
            # Track progress
            self.loss_history_.append(loss)
            self.gradient_norm_history_.append(np.linalg.norm(grad))
            nonzero_history.append(np.sum(np.abs(x) > 1e-6))
            
            # Callback
            if callback is not None:
                callback(x, t, loss)
                
            # Verbose output
            if self.verbose and t % 100 == 0:
                print(f"Iteration {t}: Loss = {loss:.6f}, "
                      f"||grad|| = {np.linalg.norm(grad):.6f}")
                      
            # Check convergence
            if convergence_criterion.check(self.loss_history_, x):
                self.converged_ = True
                self.n_iter_ = t
                if self.verbose:
                    print(f"Converged at iteration {t}")
                break
                
        # Final info
        runtime = time.time() - start_time
        info = {
            'converged': self.converged_,
            'n_iter': self.n_iter_ if self.converged_ else self.max_iter,
            'loss_history': np.array(self.loss_history_),
            'gradient_norm_history': np.array(self.gradient_norm_history_),
            'nonzero_history': np.array(nonzero_history),
            'runtime': runtime,
            'final_loss': self.loss_history_[-1],
        }
        
        return x, info
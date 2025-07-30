"""
Unit tests for AMGD optimizer.
"""

import unittest
import numpy as np
from amgd.core.optimizer import AMGD
from amgd.core.utils import poisson_log_likelihood

class TestAMGD(unittest.TestCase):
    """Tests for the AMGD optimizer."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_samples = 100
        self.n_features = 5
        
        # Generate synthetic data
        self.X = np.random.randn(self.n_samples, self.n_features)
        true_coef = np.array([0.5, -0.2, 0.3, 0.0, 0.1])
        linear_pred = self.X @ true_coef
        self.y = np.random.poisson(np.exp(linear_pred))
        
        # Initialize optimizer with test parameters
        self.optimizer = AMGD(
            alpha=0.01,
            beta1=0.8,
            beta2=0.999,
            lambda1=0.1,
            penalty='l1',
            max_iter=100,
            verbose=False
        )
    
    def test_initialization(self):
        """Test initialization of AMGD optimizer."""
        self.assertEqual(self.optimizer.alpha, 0.01)
        self.assertEqual(self.optimizer.beta1, 0.8)
        self.assertEqual(self.optimizer.beta2, 0.999)
        self.assertEqual(self.optimizer.lambda1, 0.1)
        self.assertEqual(self.optimizer.penalty, 'l1')
        self.assertEqual(self.optimizer.max_iter, 100)
    
    def test_fit_converges(self):
        """Test that the optimizer converges."""
        self.optimizer.fit(self.X, self.y, objective_fn=poisson_log_likelihood)
        
        # Check that parameters have been updated
        self.assertIsNotNone(self.optimizer.beta)
        
        # Check that loss history is decreasing
        losses = self.optimizer.loss_history
        self.assertGreater(len(losses), 1)  # At least a few iterations
        self.assertLess(losses[-1], losses[0])  # Loss decreased
    
    def test_l1_regularization(self):
        """Test that L1 regularization produces sparse coefficients."""
        # Fit with strong L1 regularization
        strong_l1_optimizer = AMGD(
            alpha=0.01,
            beta1=0.8,
            beta2=0.999,
            lambda1=1.0,  # Strong L1 penalty
            penalty='l1',
            max_iter=100,
            verbose=False
        )
        strong_l1_optimizer.fit(self.X, self.y)
        
        # Fit with weak L1 regularization
        weak_l1_optimizer = AMGD(
            alpha=0.01,
            beta1=0.8,
            beta2=0.999,
            lambda1=0.01,  # Weak L1 penalty
            penalty='l1',
            max_iter=100,
            verbose=False
        )
        weak_l1_optimizer.fit(self.X, self.y)
        
        # Count non-zero coefficients
        strong_non_zeros = np.sum(np.abs(strong_l1_optimizer.beta) > 1e-6)
        weak_non_zeros = np.sum(np.abs(weak_l1_optimizer.beta) > 1e-6)
        
        # Strong penalty should give more sparse solution
        self.assertLessEqual(strong_non_zeros, weak_non_zeros)
    
    def test_elasticnet_regularization(self):
        """Test that elastic net regularization works."""
        # Fit with elastic net regularization
        elasticnet_optimizer = AMGD(
            alpha=0.01,
            beta1=0.8,
            beta2=0.999,
            lambda1=0.1,
            lambda2=0.1,
            penalty='elasticnet',
            max_iter=100,
            verbose=False
        )
        elasticnet_optimizer.fit(self.X, self.y)
        
        # Check that parameters have been updated
        self.assertIsNotNone(elasticnet_optimizer.beta)
        
        # Check that loss history is decreasing
        losses = elasticnet_optimizer.loss_history
        self.assertGreater(len(losses), 1)
        self.assertLess(losses[-1], losses[0])

if __name__ == "__main__":
    unittest.main()
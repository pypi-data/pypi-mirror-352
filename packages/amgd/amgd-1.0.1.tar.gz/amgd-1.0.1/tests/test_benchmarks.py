"""
Tests for benchmarking utilities.
"""

import pytest
import numpy as np

from amgd.benchmarks.comparison import (
    compare_optimizers, 
    run_cross_validation,
    statistical_significance_test
)
from amgd.benchmarks.datasets import (
    generate_synthetic_poisson_data,
    get_benchmark_datasets
)


class TestBenchmarks:
    """Test benchmarking functionality."""
    
    @pytest.fixture
    def small_data(self):
        """Small dataset for quick tests."""
        X, y, true_coef = generate_synthetic_poisson_data(
            n_samples=100,
            n_features=20,
            n_informative=5,
            random_state=42
        )
        return X, y
        
    def test_compare_optimizers(self, small_data):
        """Test optimizer comparison."""
        X, y = small_data
        
        results = compare_optimizers(
            X, y,
            optimizers=['amgd', 'adam'],
            penalties=['l1'],
            lambda_values=np.array([0.01, 0.1]),
            cv_folds=3,
            verbose=False
        )
        
        assert 'cv_results' in results
        assert 'test_results' in results
        assert 'best_params' in results
        assert 'models' in results
        
        # Check that we have results for each optimizer
        assert 'amgd' in results['models']
        assert 'adam' in results['models']
        
    def test_cross_validation(self, small_data):
        """Test cross-validation functionality."""
        X, y = small_data
        
        scores = run_cross_validation(
            X, y,
            optimizer='amgd',
            penalty='l1',
            lambda_values=np.array([0.01, 0.1, 1.0]),
            cv_folds=3
        )
        
        assert 'mean_mae' in scores
        assert 'mean_rmse' in scores
        assert len(scores['mean_mae']) == 3  # One for each lambda
        
    def test_statistical_significance(self, small_data):
        """Test statistical significance testing."""
        X, y = small_data
        
        results = statistical_significance_test(
            X, y,
            optimizers=['amgd', 'adam'],
            n_bootstrap=100,
            n_runs=10,
            test_size=0.3
        )
        
        assert 'statistics' in results
        assert 'comparisons' in results
        assert 'amgd' in results['statistics']
        assert 'adam' in results['statistics']
        assert 'amgd_vs_adam' in results['comparisons']
        
    def test_benchmark_datasets(self):
        """Test benchmark dataset loading."""
        datasets = get_benchmark_datasets()
        
        # Should have at least synthetic datasets
        assert len(datasets) > 0
        
        # Check a synthetic dataset
        assert 'synthetic_small_dense' in datasets
        dataset = datasets['synthetic_small_dense']
        
        assert 'X' in dataset
        assert 'y' in dataset
        assert 'description' in dataset
        assert dataset['X'].shape[0] == 500
        assert dataset['X'].shape[1] == 50
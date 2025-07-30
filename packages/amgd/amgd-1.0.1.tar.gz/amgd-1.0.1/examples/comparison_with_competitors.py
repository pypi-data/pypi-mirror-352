"""
Compare AMGD with other optimization algorithms.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from amgd.benchmarks import compare_optimizers, get_benchmark_datasets
from amgd.visualization import plot_convergence_comparison


def main():
    # Load benchmark dataset
    print("Loading benchmark datasets...")
    datasets = get_benchmark_datasets()
    
    # Use a synthetic dataset for comparison
    dataset = datasets['synthetic_large_sparse']
    X = dataset['X']
    y = dataset['y']
    
    print(f"Dataset: {dataset['description']}")
    print(f"Samples: {dataset['n_samples']}, Features: {dataset['n_features']}")
    
    # Compare optimizers
    print("\nComparing optimizers...")
    results = compare_optimizers(
        X, y,
        optimizers=['amgd', 'adam', 'adagrad'],
        penalties=['l1', 'elasticnet'],
        lambda_values=np.logspace(-3, 0, 10),
        cv_folds=5,
        test_size=0.2,
        verbose=True
    )
    
    # Display results
    print("\n" + "="*60)
    print("SUMMARY OF RESULTS")
    print("="*60)
    
    # Best parameters for each optimizer
    print("\nBest parameters (based on CV):")
    for opt, params in results['best_params'].items():
        print(f"{opt}: penalty={params['penalty']}, "
              f"lambda={params['lambda']:.4f}, "
              f"CV MAE={params['cv_mae']:.4f}")
    
    # Test set performance
    print("\nTest set performance:")
    test_df = results['test_results']
    print(test_df[['optimizer', 'MAE', 'RMSE', 'Sparsity', 'train_time']].to_string(index=False))
    
    # Create convergence comparison plot
    print("\nPlotting convergence comparison...")
    
    # Extract loss histories from models
    plot_data = {}
    for opt_name, model in results['models'].items():
        plot_data[opt_name] = {
            'loss_history': model.loss_history_,
            'n_iter': model.n_iter_
        }
    
    fig = plot_convergence_comparison(
        plot_data,
        title="Optimizer Convergence Comparison",
        normalize_iterations=True
    )
    plt.show()
    
    # Statistical comparison
    print("\nPerforming statistical significance test...")
    from amgd.benchmarks import statistical_significance_test
    
    stat_results = statistical_significance_test(
        X, y,
        optimizers=['amgd', 'adam', 'adagrad'],
        n_bootstrap=500,
        n_runs=30
    )
    
    print("\nStatistical comparison (AMGD vs others):")
    for comparison, metrics in stat_results['comparisons'].items():
        print(f"\n{comparison}:")
        for metric, values in metrics.items():
            if values['significant']:
                print(f"  {metric}: p={values['p_value']:.4f} (significant), "
                      f"effect size={values['effect_size']:.3f}")
            else:
                print(f"  {metric}: p={values['p_value']:.4f} (not significant)")


if __name__ == "__main__":
    main()
"""
Example demonstrating custom regularization penalties with AMGD.

This example shows how to:
1. Create custom penalty functions
2. Use them with AMGD and other optimizers
3. Implement adaptive and group-based penalties
4. Compare different regularization strategies
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from typing import Optional, List, Dict, Any

from amgd.core.optimizer import AMGDOptimizer, AdamOptimizer
from amgd.core.penalties import PenaltyBase
from amgd.models import GLM
from amgd.benchmarks.datasets import generate_synthetic_poisson_data
from amgd.visualization import plot_convergence_comparison, plot_coefficient_heatmap


class AdaptiveLassoPenalty(PenaltyBase):
    """
    Adaptive Lasso penalty that uses weights based on initial estimates.
    
    The penalty is: sum_j (w_j * |beta_j|) where w_j = 1 / |beta_init_j|^gamma
    """
    
    def __init__(self, lambda1: float = 1.0, gamma: float = 1.0, 
                 initial_coef: Optional[np.ndarray] = None, epsilon: float = 1e-6):
        """
        Parameters
        ----------
        lambda1 : float
            Overall regularization strength.
        gamma : float
            Power for adaptive weights.
        initial_coef : array-like, optional
            Initial coefficient estimates for computing weights.
        epsilon : float
            Small constant to avoid division by zero.
        """
        self.lambda1 = lambda1
        self.gamma = gamma
        self.epsilon = epsilon
        self.weights = None
        
        if initial_coef is not None:
            self.set_weights(initial_coef)
            
    def set_weights(self, initial_coef: np.ndarray):
        """Set adaptive weights based on initial coefficients."""
        self.weights = 1.0 / (np.abs(initial_coef) ** self.gamma + self.epsilon)
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute adaptive lasso penalty value."""
        if self.weights is None:
            # If no weights set, use standard L1
            return self.lambda1 * np.sum(np.abs(x))
        return self.lambda1 * np.sum(self.weights * np.abs(x))
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute penalty gradient (subgradient for L1)."""
        if self.weights is None:
            return self.lambda1 * np.sign(x)
        return self.lambda1 * self.weights * np.sign(x)
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Adaptive soft-thresholding operator."""
        if self.weights is None:
            threshold = self.lambda1 * step_size
        else:
            threshold = self.lambda1 * self.weights * step_size
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)


class GroupLassoPenalty(PenaltyBase):
    """
    Group Lasso penalty for selecting groups of features together.
    
    The penalty is: sum_g sqrt(p_g) * ||beta_g||_2
    where g indexes groups and p_g is the size of group g.
    """
    
    def __init__(self, groups: List[List[int]], lambda1: float = 1.0):
        """
        Parameters
        ----------
        groups : list of lists
            Each inner list contains indices of features in that group.
        lambda1 : float
            Regularization strength.
        """
        self.groups = groups
        self.lambda1 = lambda1
        
        # Precompute group sizes and indices
        self.group_sizes = [len(g) for g in groups]
        self.n_features = max(max(g) for g in groups) + 1
        
        # Create mapping from feature to group
        self.feature_to_group = {}
        for g_idx, group in enumerate(groups):
            for feature in group:
                self.feature_to_group[feature] = g_idx
                
    def __call__(self, x: np.ndarray) -> float:
        """Compute group lasso penalty value."""
        penalty = 0.0
        for g_idx, group in enumerate(self.groups):
            group_coef = x[group]
            group_norm = np.linalg.norm(group_coef)
            penalty += np.sqrt(self.group_sizes[g_idx]) * group_norm
        return self.lambda1 * penalty
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute group lasso gradient."""
        grad = np.zeros_like(x)
        
        for g_idx, group in enumerate(self.groups):
            group_coef = x[group]
            group_norm = np.linalg.norm(group_coef)
            
            if group_norm > 1e-10:  # Avoid division by zero
                scale = np.sqrt(self.group_sizes[g_idx]) / group_norm
                grad[group] = self.lambda1 * scale * group_coef
                
        return grad
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """Group soft-thresholding operator."""
        x_prox = x.copy()
        
        for g_idx, group in enumerate(self.groups):
            group_coef = x[group]
            group_norm = np.linalg.norm(group_coef)
            threshold = self.lambda1 * np.sqrt(self.group_sizes[g_idx]) * step_size
            
            if group_norm > threshold:
                scale = 1 - threshold / group_norm
                x_prox[group] = scale * group_coef
            else:
                x_prox[group] = 0
                
        return x_prox


class FusedLassoPenalty(PenaltyBase):
    """
    Fused Lasso penalty that encourages adjacent features to have similar values.
    
    The penalty is: lambda1 * sum_j |beta_j| + lambda2 * sum_j |beta_j - beta_{j-1}|
    """
    
    def __init__(self, lambda1: float = 1.0, lambda2: float = 1.0):
        """
        Parameters
        ----------
        lambda1 : float
            Standard L1 regularization strength.
        lambda2 : float
            Fusion penalty strength.
        """
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute fused lasso penalty value."""
        l1_penalty = self.lambda1 * np.sum(np.abs(x))
        fusion_penalty = self.lambda2 * np.sum(np.abs(np.diff(x)))
        return l1_penalty + fusion_penalty
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute fused lasso gradient (subgradient)."""
        n = len(x)
        grad = np.zeros(n)
        
        # L1 component
        grad += self.lambda1 * np.sign(x)
        
        # Fusion component
        for i in range(n):
            if i > 0:
                grad[i] += self.lambda2 * np.sign(x[i] - x[i-1])
            if i < n - 1:
                grad[i] -= self.lambda2 * np.sign(x[i+1] - x[i])
                
        return grad
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """
        Proximal operator for fused lasso.
        This is an approximation using alternating soft-thresholding.
        """
        # First apply L1 soft-thresholding
        x_prox = np.sign(x) * np.maximum(np.abs(x) - self.lambda1 * step_size, 0)
        
        # Then apply fusion penalty (simplified)
        # A proper implementation would use specialized algorithms
        return x_prox


class SCADPenalty(PenaltyBase):
    """
    Smoothly Clipped Absolute Deviation (SCAD) penalty.
    
    This penalty reduces bias for large coefficients while maintaining
    sparsity for small coefficients.
    """
    
    def __init__(self, lambda1: float = 1.0, a: float = 3.7):
        """
        Parameters
        ----------
        lambda1 : float
            Regularization parameter.
        a : float
            SCAD parameter (typically 3.7).
        """
        self.lambda1 = lambda1
        self.a = a
        
    def __call__(self, x: np.ndarray) -> float:
        """Compute SCAD penalty value."""
        penalty = np.zeros_like(x, dtype=float)
        abs_x = np.abs(x)
        
        # Three regions of SCAD
        mask1 = abs_x <= self.lambda1
        mask2 = (abs_x > self.lambda1) & (abs_x <= self.a * self.lambda1)
        mask3 = abs_x > self.a * self.lambda1
        
        penalty[mask1] = self.lambda1 * abs_x[mask1]
        penalty[mask2] = -(abs_x[mask2]**2 - 2*self.a*self.lambda1*abs_x[mask2] + 
                          self.lambda1**2) / (2*(self.a - 1))
        penalty[mask3] = (self.a + 1) * self.lambda1**2 / 2
        
        return np.sum(penalty)
        
    def gradient(self, x: np.ndarray) -> np.ndarray:
        """Compute SCAD gradient."""
        grad = np.zeros_like(x)
        abs_x = np.abs(x)
        
        # Three regions
        mask1 = abs_x <= self.lambda1
        mask2 = (abs_x > self.lambda1) & (abs_x <= self.a * self.lambda1)
        mask3 = abs_x > self.a * self.lambda1
        
        grad[mask1] = self.lambda1 * np.sign(x[mask1])
        grad[mask2] = (self.a * self.lambda1 * np.sign(x[mask2]) - x[mask2]) / (self.a - 1)
        grad[mask3] = 0  # No penalty for large coefficients
        
        return grad
        
    def proximal_operator(self, x: np.ndarray, step_size: float) -> np.ndarray:
        """SCAD proximal operator."""
        # Simplified version - full implementation would be more complex
        abs_x = np.abs(x)
        sign_x = np.sign(x)
        threshold = self.lambda1 * step_size
        
        # Apply different thresholding rules based on magnitude
        x_prox = np.zeros_like(x)
        
        # Small coefficients: soft thresholding
        mask1 = abs_x <= threshold * (1 + 1/self.a)
        x_prox[mask1] = sign_x[mask1] * np.maximum(abs_x[mask1] - threshold, 0)
        
        # Medium coefficients: adjusted thresholding
        mask2 = (abs_x > threshold * (1 + 1/self.a)) & (abs_x <= self.a * threshold)
        if np.any(mask2):
            x_prox[mask2] = ((self.a - 1) * x[mask2] - sign_x[mask2] * self.a * threshold) / (self.a - 2)
        
        # Large coefficients: no shrinkage
        mask3 = abs_x > self.a * threshold
        x_prox[mask3] = x[mask3]
        
        return x_prox


def create_custom_glm_model(penalty: PenaltyBase, **kwargs) -> GLM:
    """
    Create a GLM model with custom penalty.
    
    Parameters
    ----------
    penalty : PenaltyBase
        Custom penalty object.
    **kwargs
        Additional arguments for GLM.
        
    Returns
    -------
    model : GLM
        Configured GLM model.
    """
    class CustomGLM(GLM):
        def _create_penalty(self):
            return penalty
            
    return CustomGLM(**kwargs)


def demonstrate_adaptive_lasso():
    """Demonstrate adaptive lasso penalty."""
    print("=" * 60)
    print("ADAPTIVE LASSO DEMONSTRATION")
    print("=" * 60)
    
    # Generate data
    X, y, true_coef = generate_synthetic_poisson_data(
        n_samples=500,
        n_features=50,
        n_informative=10,
        sparsity=0.8,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Step 1: Get initial estimates using standard L1
    print("\nStep 1: Getting initial estimates with standard L1...")
    initial_model = GLM(
        family='poisson',
        link='log',
        optimizer='amgd',
        penalty='l1',
        lambda1=0.1
    )
    initial_model.fit(X_train, y_train)
    
    # Step 2: Create adaptive lasso penalty
    print("\nStep 2: Creating adaptive lasso penalty...")
    adaptive_penalty = AdaptiveLassoPenalty(
        lambda1=0.1,
        gamma=1.0,
        initial_coef=initial_model.coef_
    )
    
    # Step 3: Fit model with adaptive penalty
    print("\nStep 3: Fitting model with adaptive lasso...")
    adaptive_model = create_custom_glm_model(
        penalty=adaptive_penalty,
        family='poisson',
        link='log',
        optimizer='amgd',
        max_iter=1000,
        verbose=True
    )
    adaptive_model.fit(X_train, y_train)
    
    # Compare results
    print("\n" + "-" * 40)
    print("RESULTS COMPARISON")
    print("-" * 40)
    
    # Sparsity
    l1_sparsity = 1 - np.sum(np.abs(initial_model.coef_) > 1e-6) / len(initial_model.coef_)
    adaptive_sparsity = 1 - np.sum(np.abs(adaptive_model.coef_) > 1e-6) / len(adaptive_model.coef_)
    
    print(f"L1 sparsity: {l1_sparsity:.2%}")
    print(f"Adaptive Lasso sparsity: {adaptive_sparsity:.2%}")
    
    # Test performance
    l1_score = initial_model.score(X_test, y_test)
    adaptive_score = adaptive_model.score(X_test, y_test)
    
    print(f"\nL1 test score: {l1_score:.4f}")
    print(f"Adaptive Lasso test score: {adaptive_score:.4f}")
    
    # Feature selection accuracy
    true_nonzero = set(np.where(np.abs(true_coef) > 1e-6)[0])
    l1_selected = set(np.where(np.abs(initial_model.coef_) > 1e-6)[0])
    adaptive_selected = set(np.where(np.abs(adaptive_model.coef_) > 1e-6)[0])
    
    l1_precision = len(true_nonzero & l1_selected) / len(l1_selected) if l1_selected else 0
    adaptive_precision = len(true_nonzero & adaptive_selected) / len(adaptive_selected) if adaptive_selected else 0
    
    print(f"\nL1 feature selection precision: {l1_precision:.2%}")
    print(f"Adaptive Lasso feature selection precision: {adaptive_precision:.2%}")
    
    return initial_model, adaptive_model


def demonstrate_group_lasso():
    """Demonstrate group lasso penalty."""
    print("\n" + "=" * 60)
    print("GROUP LASSO DEMONSTRATION")
    print("=" * 60)
    
    # Generate data with grouped features
    n_samples = 500
    n_groups = 10
    group_size = 5
    n_features = n_groups * group_size
    
    # Create groups
    groups = [list(range(i*group_size, (i+1)*group_size)) for i in range(n_groups)]
    
    # Generate data where only some groups are relevant
    np.random.seed(42)
    X = np.random.randn(n_samples, n_features)
    
    # True coefficients: only 3 groups are active
    true_coef = np.zeros(n_features)
    active_groups = [1, 4, 7]
    for g in active_groups:
        true_coef[groups[g]] = np.random.randn(group_size) * 1.5
        
    # Generate Poisson response
    linear_pred = X @ true_coef
    mu = np.exp(np.clip(linear_pred, -10, 10))
    y = np.random.poisson(mu)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nData: {n_groups} groups of {group_size} features each")
    print(f"Active groups: {active_groups}")
    
    # Create group lasso penalty
    group_penalty = GroupLassoPenalty(groups=groups, lambda1=0.5)
    
    # Fit model
    print("\nFitting model with group lasso...")
    group_model = create_custom_glm_model(
        penalty=group_penalty,
        family='poisson',
        link='log',
        optimizer='amgd',
        max_iter=1000,
        verbose=True
    )
    group_model.fit(X_train, y_train)
    
    # Check which groups were selected
    selected_groups = []
    for g_idx, group in enumerate(groups):
        if np.any(np.abs(group_model.coef_[group]) > 1e-6):
            selected_groups.append(g_idx)
            
    print(f"\nSelected groups: {selected_groups}")
    print(f"Group selection accuracy: {len(set(active_groups) & set(selected_groups))}/{len(active_groups)}")
    
    # Visualize group structure
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    coef_matrix = true_coef.reshape(n_groups, group_size)
    plt.imshow(coef_matrix, aspect='auto', cmap='RdBu_r', vmin=-2, vmax=2)
    plt.colorbar(label='Coefficient Value')
    plt.xlabel('Feature within Group')
    plt.ylabel('Group')
    plt.title('True Coefficients')
    
    plt.subplot(1, 2, 2)
    estimated_matrix = group_model.coef_.reshape(n_groups, group_size)
    plt.imshow(estimated_matrix, aspect='auto', cmap='RdBu_r', vmin=-2, vmax=2)
    plt.colorbar(label='Coefficient Value')
    plt.xlabel('Feature within Group')
    plt.ylabel('Group')
    plt.title('Estimated Coefficients (Group Lasso)')
    
    plt.tight_layout()
    plt.show()
    
    return group_model


def compare_regularization_methods():
    """Compare different regularization methods."""
    print("\n" + "=" * 60)
    print("COMPARING REGULARIZATION METHODS")
    print("=" * 60)
    
    # Generate challenging dataset
    X, y, true_coef = generate_synthetic_poisson_data(
        n_samples=800,
        n_features=100,
        n_informative=20,
        sparsity=0.85,
        noise_level=0.2,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Different penalties to compare
    penalties = {
        'L1': L1Penalty(lambda1=0.1),
        'Adaptive Lasso': None,  # Will be created after initial fit
        'SCAD': SCADPenalty(lambda1=0.1, a=3.7),
        'Fused Lasso': FusedLassoPenalty(lambda1=0.05, lambda2=0.05)
    }
    
    results = {}
    convergence_histories = {}
    
    # Standard L1 for initial estimates
    print("\nFitting initial L1 model...")
    l1_model = GLM(
        family='poisson',
        link='log',
        optimizer='amgd',
        penalty='l1',
        lambda1=0.1,
        max_iter=1000
    )
    l1_model.fit(X_train, y_train)
    
    # Create adaptive lasso penalty
    penalties['Adaptive Lasso'] = AdaptiveLassoPenalty(
        lambda1=0.1,
        gamma=1.0,
        initial_coef=l1_model.coef_
    )
    
    # Fit models with different penalties
    for name, penalty in penalties.items():
        print(f"\nFitting model with {name}...")
        
        if name == 'L1':
            model = l1_model
        else:
            model = create_custom_glm_model(
                penalty=penalty,
                family='poisson',
                link='log',
                optimizer='amgd',
                max_iter=1000,
                verbose=False
            )
            model.fit(X_train, y_train)
            
        # Evaluate
        test_score = model.score(X_test, y_test)
        sparsity = 1 - np.sum(np.abs(model.coef_) > 1e-6) / len(model.coef_)
        
        # Feature selection accuracy
        true_nonzero = set(np.where(np.abs(true_coef) > 1e-6)[0])
        selected = set(np.where(np.abs(model.coef_) > 1e-6)[0])
        precision = len(true_nonzero & selected) / len(selected) if selected else 0
        recall = len(true_nonzero & selected) / len(true_nonzero) if true_nonzero else 0
        
        results[name] = {
            'test_score': test_score,
            'sparsity': sparsity,
            'precision': precision,
            'recall': recall,
            'n_selected': len(selected),
            'n_iter': model.n_iter_
        }
        
        convergence_histories[name] = {
            'loss_history': model.loss_history_
        }
        
    # Display results
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    print(f"\n{'Method':<20} {'Test Score':<12} {'Sparsity':<10} {'Precision':<10} {'Recall':<10} {'Selected':<10}")
    print("-" * 72)
    
    for name, res in results.items():
        print(f"{name:<20} {res['test_score']:<12.4f} {res['sparsity']:<10.2%} "
              f"{res['precision']:<10.2%} {res['recall']:<10.2%} {res['n_selected']:<10}")
        
    # Plot convergence comparison
    fig = plot_convergence_comparison(
        convergence_histories,
        title="Convergence Comparison of Regularization Methods",
        normalize_iterations=True
    )
    plt.show()
    
    # Plot coefficient comparison
    plt.figure(figsize=(15, 8))
    
    n_methods = len(penalties)
    for i, (name, _) in enumerate(penalties.items()):
        plt.subplot(2, (n_methods + 1) // 2, i + 1)
        
        if name == 'L1':
            coef = l1_model.coef_
        else:
            # Get the model's coefficients
            coef = results[name].get('coef', np.zeros(len(true_coef)))
            
        # Plot true vs estimated
        plt.scatter(true_coef, coef, alpha=0.5)
        plt.plot([-3, 3], [-3, 3], 'r--', alpha=0.5)
        plt.xlabel('True Coefficients')
        plt.ylabel('Estimated Coefficients')
        plt.title(name)
        plt.grid(True, alpha=0.3)
        
    plt.tight_layout()
    plt.show()
    
    return results


def main():
    """Run all demonstrations."""
    # 1. Adaptive Lasso
    adaptive_results = demonstrate_adaptive_lasso()
    
    # 2. Group Lasso
    group_results = demonstrate_group_lasso()
    
    # 3. Compare all methods
    comparison_results = compare_regularization_methods()
    
    print("\n" + "=" * 60)
    print("CUSTOM REGULARIZATION EXAMPLES COMPLETED")
    print("=" * 60)
    print("\nKey takeaways:")
    print("1. Adaptive Lasso can improve feature selection by using data-driven weights")
    print("2. Group Lasso is effective when features have natural grouping structure")
    print("3. SCAD reduces bias for large coefficients while maintaining sparsity")
    print("4. Different penalties are suitable for different data characteristics")
    print("\nThe AMGD optimizer works efficiently with all these custom penalties!")


if __name__ == "__main__":
    main()
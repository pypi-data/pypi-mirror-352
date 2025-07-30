"""
Visualization utilities for coefficient analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Union, Tuple
import seaborn as sns


def plot_coefficient_path(
    lambda_values: np.ndarray,
    coefficients: np.ndarray,
    feature_names: Optional[List[str]] = None,
    top_k: Optional[int] = 10,
    title: str = "Coefficient Path",
    xlabel: str = "Regularization Strength (λ)",
    ylabel: str = "Coefficient Value",
    log_scale_x: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot coefficient paths across different regularization strengths.
    
    Parameters
    ----------
    lambda_values : array-like
        Regularization parameter values.
    coefficients : array-like of shape (n_lambdas, n_features)
        Coefficient values for each lambda.
    feature_names : list or None
        Names of features.
    top_k : int or None
        Number of top features to highlight.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    log_scale_x : bool
        Whether to use log scale for x-axis.
    figsize : tuple
        Figure size.
    save_path : str or None
        Path to save figure.
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    n_features = coefficients.shape[1]
    
    # If top_k specified, find most important features
    if top_k is not None and top_k < n_features:
        # Find features with largest absolute coefficients
        max_abs_coef = np.max(np.abs(coefficients), axis=0)
        top_indices = np.argsort(max_abs_coef)[-top_k:]
        
        # Plot non-top features in gray
        for i in range(n_features):
            if i not in top_indices:
                ax.plot(lambda_values, coefficients[:, i], 
                       color='gray', alpha=0.3, linewidth=0.5)
                
        # Plot top features with colors
        colors = plt.cm.get_cmap('tab10')
        for idx, i in enumerate(top_indices):
            label = feature_names[i] if feature_names else f"Feature {i}"
            ax.plot(lambda_values, coefficients[:, i], 
                   label=label, color=colors(idx), linewidth=2)
    else:
        # Plot all features
        for i in range(n_features):
            label = feature_names[i] if feature_names else None
            ax.plot(lambda_values, coefficients[:, i], label=label, linewidth=1)
            
    if log_scale_x:
        ax.set_xscale('log')
        
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    if top_k is not None and top_k < n_features:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_coefficient_heatmap(
    coefficients: np.ndarray,
    feature_names: Optional[List[str]] = None,
    lambda_values: Optional[np.ndarray] = None,
    title: str = "Coefficient Heatmap",
    cmap: str = "RdBu_r",
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot heatmap of coefficients across features and lambda values.
    
    Parameters
    ----------
    coefficients : array-like of shape (n_lambdas, n_features)
        Coefficient values.
    feature_names : list or None
        Names of features.
    lambda_values : array-like or None
        Regularization values.
    title : str
        Plot title.
    cmap : str
        Colormap name.
    figsize : tuple
        Figure size.
    save_path : str or None
        Path to save figure.
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Prepare labels
    if feature_names is None:
        feature_names = [f"Feature {i}" for i in range(coefficients.shape[1])]
        
    if lambda_values is None:
        lambda_labels = [f"λ_{i}" for i in range(coefficients.shape[0])]
    else:
        lambda_labels = [f"{λ:.4f}" for λ in lambda_values]
        
    # Create heatmap
    sns.heatmap(coefficients.T, 
                xticklabels=lambda_labels,
                yticklabels=feature_names,
                cmap=cmap,
                center=0,
                cbar_kws={'label': 'Coefficient Value'},
                ax=ax)
                
    ax.set_xlabel("Regularization Strength (λ)", fontsize=12)
    ax.set_ylabel("Features", fontsize=12)
    ax.set_title(title, fontsize=14)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_feature_importance(
    coefficients: np.ndarray,
    feature_names: Optional[List[str]] = None,
    top_k: int = 20,
    title: str = "Feature Importance",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot feature importance based on coefficient magnitudes.
    
    Parameters
    ----------
    coefficients : array-like
        Model coefficients.
    feature_names : list or None
        Names of features.
    top_k : int
        Number of top features to show.
    title : str
        Plot title.
    figsize : tuple
        Figure size.
    save_path : str or None
        Path to save figure.
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Compute importance as absolute coefficient value
    importance = np.abs(coefficients)
    indices = np.argsort(importance)[::-1][:top_k]
    
    # Prepare labels
    if feature_names is None:
        labels = [f"Feature {i}" for i in indices]
    else:
        labels = [feature_names[i] for i in indices]
        
    # Create bar plot
    y_pos = np.arange(top_k)
    colors = ['red' if coefficients[i] < 0 else 'blue' for i in indices]
    
    bars = ax.barh(y_pos, importance[indices], color=colors, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Absolute Coefficient Value", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, idx) in enumerate(zip(bars, indices)):
        width = bar.get_width()
        ax.text(width + 0.001, bar.get_y() + bar.get_height()/2,
                f'{coefficients[idx]:.3f}', 
                ha='left', va='center', fontsize=9)
                
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig
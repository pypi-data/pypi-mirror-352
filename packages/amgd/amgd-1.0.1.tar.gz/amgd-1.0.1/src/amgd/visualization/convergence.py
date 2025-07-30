"""
Visualization utilities for optimization convergence.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union
import seaborn as sns


def plot_convergence(
    loss_history: Union[List[float], np.ndarray],
    title: str = "Convergence Plot",
    xlabel: str = "Iteration",
    ylabel: str = "Loss",
    log_scale: bool = True,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot convergence history of optimization.
    
    Parameters
    ----------
    loss_history : array-like
        History of loss values.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    log_scale : bool
        Whether to use log scale for y-axis.
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
    
    iterations = np.arange(1, len(loss_history) + 1)
    
    if log_scale:
        ax.semilogy(iterations, loss_history, linewidth=2)
    else:
        ax.plot(iterations, loss_history, linewidth=2)
        
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_convergence_comparison(
    results: Dict[str, Dict],
    metric: str = 'loss_history',
    title: str = "Convergence Comparison",
    xlabel: str = "Iteration",
    ylabel: str = "Loss",
    log_scale: bool = True,
    normalize_iterations: bool = True,
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Compare convergence of multiple optimizers.
    
    Parameters
    ----------
    results : dict
        Dictionary mapping optimizer names to their results.
    metric : str
        Which metric to plot from results.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    log_scale : bool
        Whether to use log scale for y-axis.
    normalize_iterations : bool
        Whether to normalize iteration counts to percentages.
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
    
    # Color palette
    colors = plt.cm.get_cmap('tab10')
    
    for i, (name, result) in enumerate(results.items()):
        if metric in result:
            history = result[metric]
            
            if normalize_iterations:
                # Normalize to percentage of iterations
                x = np.linspace(0, 100, len(history))
                xlabel = "Percentage of Iterations (%)"
            else:
                x = np.arange(1, len(history) + 1)
                
            if log_scale:
                ax.semilogy(x, history, label=name, linewidth=2, color=colors(i))
            else:
                ax.plot(x, history, label=name, linewidth=2, color=colors(i))
                
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_learning_curves(
    train_losses: Union[List[float], np.ndarray],
    val_losses: Optional[Union[List[float], np.ndarray]] = None,
    title: str = "Learning Curves",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot training and validation learning curves.
    
    Parameters
    ----------
    train_losses : array-like
        Training loss history.
    val_losses : array-like or None
        Validation loss history.
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
    
    iterations = np.arange(1, len(train_losses) + 1)
    
    ax.plot(iterations, train_losses, label='Training Loss', linewidth=2)
    
    if val_losses is not None:
        val_iterations = np.arange(1, len(val_losses) + 1)
        ax.plot(val_iterations, val_losses, label='Validation Loss', 
                linewidth=2, linestyle='--')
        
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Loss", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig
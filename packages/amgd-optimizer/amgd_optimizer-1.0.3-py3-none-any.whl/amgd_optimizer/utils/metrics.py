"""
Evaluation metrics for AMGD package.
"""

import numpy as np
from typing import Union, Optional
import warnings


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean absolute error regression loss.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    loss : float
        Non-negative floating point value (the best value is 0.0)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    
    return np.mean(np.abs(y_true - y_pred))


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean squared error regression loss.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    loss : float
        Non-negative floating point value (the best value is 0.0)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    
    return np.mean((y_true - y_pred) ** 2)


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Root mean squared error regression loss.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    loss : float
        Non-negative floating point value (the best value is 0.0)
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def poisson_deviance(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-8) -> float:
    """
    Compute the Poisson deviance for count data.
    
    The Poisson deviance is defined as:
    D = 2 * sum(y_true * log((y_true + eps) / (y_pred + eps)) - (y_true - y_pred))
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values (counts)
    y_pred : array-like of shape (n_samples,)
        Estimated target values (predicted rates)
    eps : float, default=1e-8
        Small constant to avoid log(0)
        
    Returns
    -------
    deviance : float
        Poisson deviance (lower is better, 0 is perfect)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    
    # Ensure predictions are positive
    y_pred = np.maximum(y_pred, eps)
    
    # Handle zero counts in y_true
    mask = y_true > 0
    deviance = np.zeros_like(y_true)
    
    # For non-zero counts
    if np.any(mask):
        deviance[mask] = y_true[mask] * np.log((y_true[mask] + eps) / y_pred[mask])
    
    # Add the second term for all observations
    deviance = deviance - (y_true - y_pred)
    
    return 2 * np.sum(deviance)


def mean_poisson_deviance(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-8) -> float:
    """
    Compute the mean Poisson deviance.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values (counts)
    y_pred : array-like of shape (n_samples,)
        Estimated target values (predicted rates)
    eps : float, default=1e-8
        Small constant to avoid log(0)
        
    Returns
    -------
    mean_deviance : float
        Mean Poisson deviance
    """
    return poisson_deviance(y_true, y_pred, eps) / len(y_true)


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    R² (coefficient of determination) regression score function.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    z : float
        R² score (1 is perfect prediction, can be negative)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    
    if ss_tot == 0:
        warnings.warn("R² is ill-defined when y_true has zero variance")
        return 0.0
    
    return 1 - (ss_res / ss_tot)


def explained_variance_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Explained variance regression score function.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    score : float
        Explained variance score (1 is perfect prediction)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    
    var_y = np.var(y_true)
    var_residual = np.var(y_true - y_pred)
    
    if var_y == 0:
        warnings.warn("Explained variance is ill-defined when y_true has zero variance")
        return 0.0
    
    return 1 - (var_residual / var_y)


def compute_metrics_summary(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Compute a comprehensive summary of regression metrics.
    
    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values
    y_pred : array-like of shape (n_samples,)
        Estimated target values
        
    Returns
    -------
    metrics : dict
        Dictionary containing various regression metrics
    """
    metrics = {
        'mae': mean_absolute_error(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': root_mean_squared_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'explained_variance': explained_variance_score(y_true, y_pred),
        'mean_poisson_deviance': mean_poisson_deviance(y_true, y_pred),
        'poisson_deviance': poisson_deviance(y_true, y_pred)
    }
    
    return metrics


def sparsity_metrics(coef: np.ndarray, threshold: float = 1e-8) -> dict:
    """
    Compute sparsity-related metrics for coefficient vectors.
    
    Parameters
    ----------
    coef : array-like of shape (n_features,)
        Coefficient vector
    threshold : float, default=1e-8
        Threshold below which coefficients are considered zero
        
    Returns
    -------
    metrics : dict
        Dictionary containing sparsity metrics
    """
    coef = np.asarray(coef)
    
    # Binary mask for non-zero coefficients
    non_zero_mask = np.abs(coef) > threshold
    
    metrics = {
        'n_features_total': len(coef),
        'n_features_selected': np.sum(non_zero_mask),
        'n_features_zero': np.sum(~non_zero_mask),
        'sparsity_ratio': np.mean(~non_zero_mask),
        'density_ratio': np.mean(non_zero_mask),
        'l0_norm': np.sum(non_zero_mask),  # Number of non-zero coefficients
        'l1_norm': np.sum(np.abs(coef)),
        'l2_norm': np.sqrt(np.sum(coef**2)),
        'max_coef': np.max(np.abs(coef)),
        'mean_coef_magnitude': np.mean(np.abs(coef[non_zero_mask])) if np.any(non_zero_mask) else 0.0
    }
    
    return metrics 
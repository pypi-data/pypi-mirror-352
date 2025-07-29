"""
Base classes and common utilities for AMGD package.

This module provides the foundational classes and interfaces that are shared
across different components of the AMGD package.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, Tuple, List
from sklearn.base import BaseEstimator
import warnings


class BaseAMGDOptimizer(ABC, BaseEstimizer):
    """
    Abstract base class for all AMGD-style optimizers.
    
    This class defines the common interface and shared functionality
    for all optimization algorithms in the AMGD family.
    
    Parameters
    ----------
    learning_rate : float, default=0.01
        Initial learning rate
    max_iter : int, default=1000
        Maximum number of iterations
    tol : float, default=1e-6
        Tolerance for convergence
    random_state : int, RandomState instance or None, default=None
        Random state for reproducibility
    verbose : bool, default=False
        Whether to print convergence information
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        max_iter: int = 1000,
        tol: float = 1e-6,
        random_state: Optional[int] = None,
        verbose: bool = False
    ):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.verbose = verbose
    
    @abstractmethod
    def _compute_loss(self, X: np.ndarray, y: np.ndarray, coef: np.ndarray) -> float:
        """
        Compute the objective function value.
        
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Input data
        y : ndarray of shape (n_samples,)
            Target values
        coef : ndarray of shape (n_features,)
            Current coefficients
            
        Returns
        -------
        loss : float
            Objective function value
        """
        pass
    
    @abstractmethod
    def _compute_gradient(self, X: np.ndarray, y: np.ndarray, coef: np.ndarray) -> np.ndarray:
        """
        Compute the gradient of the objective function.
        
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Input data
        y : ndarray of shape (n_samples,)
            Target values
        coef : ndarray of shape (n_features,)
            Current coefficients
            
        Returns
        -------
        gradient : ndarray of shape (n_features,)
            Gradient vector
        """
        pass
    
    @abstractmethod
    def _update_coefficients(
        self, 
        coef: np.ndarray, 
        gradient: np.ndarray, 
        iteration: int
    ) -> np.ndarray:
        """
        Update coefficients based on gradient and algorithm-specific rules.
        
        Parameters
        ----------
        coef : ndarray of shape (n_features,)
            Current coefficients
        gradient : ndarray of shape (n_features,)
            Current gradient
        iteration : int
            Current iteration number
            
        Returns
        -------
        new_coef : ndarray of shape (n_features,)
            Updated coefficients
        """
        pass
    
    def _check_convergence(
        self, 
        loss_history: List[float], 
        iteration: int
    ) -> bool:
        """
        Check if the optimization has converged.
        
        Parameters
        ----------
        loss_history : list of float
            History of loss values
        iteration : int
            Current iteration number
            
        Returns
        -------
        converged : bool
            Whether convergence criterion is met
        """
        if len(loss_history) < 2:
            return False
        
        # Check relative change in loss
        relative_change = abs(loss_history[-1] - loss_history[-2]) / (abs(loss_history[-2]) + 1e-10)
        
        if relative_change < self.tol:
            if self.verbose:
                print(f"Converged at iteration {iteration}: relative change = {relative_change:.2e}")
            return True
        
        return False
    
    def _initialize_state(self, n_features: int) -> Dict[str, Any]:
        """
        Initialize algorithm-specific state variables.
        
        Parameters
        ----------
        n_features : int
            Number of features
            
        Returns
        -------
        state : dict
            Initial state dictionary
        """
        return {
            'iteration': 0,
            'loss_history': [],
            'converged': False
        }
    
    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Get parameters for this estimator.
        
        Parameters
        ----------
        deep : bool, default=True
            If True, will return the parameters for this estimator and
            contained subobjects that are estimators.
            
        Returns
        -------
        params : dict
            Parameter names mapped to their values.
        """
        return {
            'learning_rate': self.learning_rate,
            'max_iter': self.max_iter,
            'tol': self.tol,
            'random_state': self.random_state,
            'verbose': self.verbose
        }
    
    def set_params(self, **params) -> 'BaseAMGDOptimizer':
        """
        Set the parameters of this estimator.
        
        Parameters
        ----------
        **params : dict
            Estimator parameters.
            
        Returns
        -------
        self : estimator instance
            Estimator instance.
        """
        valid_params = self.get_params()
        
        for key, value in params.items():
            if key not in valid_params:
                raise ValueError(f"Invalid parameter {key} for estimator {type(self).__name__}")
            setattr(self, key, value)
        
        return self


class RegularizationMixin:
    """
    Mixin class providing regularization functionality.
    
    This mixin provides common regularization operations that can be
    shared across different optimization algorithms.
    """
    
    @staticmethod
    def l1_penalty(coef: np.ndarray, lambda1: float) -> float:
        """
        Compute L1 (Lasso) penalty.
        
        Parameters
        ----------
        coef : ndarray
            Coefficient vector
        lambda1 : float
            L1 regularization parameter
            
        Returns
        -------
        penalty : float
            L1 penalty value
        """
        return lambda1 * np.sum(np.abs(coef))
    
    @staticmethod
    def l2_penalty(coef: np.ndarray, lambda2: float) -> float:
        """
        Compute L2 (Ridge) penalty.
        
        Parameters
        ----------
        coef : ndarray
            Coefficient vector
        lambda2 : float
            L2 regularization parameter
            
        Returns
        -------
        penalty : float
            L2 penalty value
        """
        return 0.5 * lambda2 * np.sum(coef**2)
    
    @staticmethod
    def elastic_net_penalty(coef: np.ndarray, lambda1: float, lambda2: float) -> float:
        """
        Compute Elastic Net penalty (combination of L1 and L2).
        
        Parameters
        ----------
        coef : ndarray
            Coefficient vector
        lambda1 : float
            L1 regularization parameter
        lambda2 : float
            L2 regularization parameter
            
        Returns
        -------
        penalty : float
            Elastic Net penalty value
        """
        return RegularizationMixin.l1_penalty(coef, lambda1) + RegularizationMixin.l2_penalty(coef, lambda2)
    
    @staticmethod
    def l1_gradient(coef: np.ndarray, lambda1: float) -> np.ndarray:
        """
        Compute L1 penalty gradient (subgradient).
        
        Parameters
        ----------
        coef : ndarray
            Coefficient vector
        lambda1 : float
            L1 regularization parameter
            
        Returns
        -------
        gradient : ndarray
            L1 penalty gradient
        """
        return lambda1 * np.sign(coef)
    
    @staticmethod
    def l2_gradient(coef: np.ndarray, lambda2: float) -> np.ndarray:
        """
        Compute L2 penalty gradient.
        
        Parameters
        ----------
        coef : ndarray
            Coefficient vector
        lambda2 : float
            L2 regularization parameter
            
        Returns
        -------
        gradient : ndarray
            L2 penalty gradient
        """
        return lambda2 * coef
    
    @staticmethod
    def soft_threshold(x: np.ndarray, threshold: float) -> np.ndarray:
        """
        Apply soft-thresholding operator.
        
        The soft-thresholding operator is defined as:
        soft_threshold(x, λ) = sign(x) * max(|x| - λ, 0)
        
        Parameters
        ----------
        x : ndarray
            Input array
        threshold : float
            Threshold value
            
        Returns
        -------
        result : ndarray
            Soft-thresholded array
        """
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)
    
    @staticmethod
    def adaptive_soft_threshold(
        x: np.ndarray, 
        threshold: float, 
        epsilon: float = 0.01
    ) -> np.ndarray:
        """
        Apply adaptive soft-thresholding operator (AMGD innovation).
        
        The adaptive soft-thresholding operator is defined as:
        adaptive_soft_threshold(x, λ, ε) = sign(x) * max(|x| - λ/(|x| + ε), 0)
        
        This is the key innovation of AMGD that provides coefficient-dependent
        regularization strength.
        
        Parameters
        ----------
        x : ndarray
            Input array
        threshold : float
            Base threshold value
        epsilon : float, default=0.01
            Small constant to avoid division by zero
            
        Returns
        -------
        result : ndarray
            Adaptive soft-thresholded array
        """
        denominator = np.abs(x) + epsilon
        adaptive_threshold = threshold / denominator
        return np.sign(x) * np.maximum(np.abs(x) - adaptive_threshold, 0)


class PoissonLossMixin:
    """
    Mixin class providing Poisson regression loss functions.
    
    This mixin provides Poisson-specific loss and gradient computations
    that can be shared across different estimators.
    """
    
    @staticmethod
    def poisson_log_likelihood(y: np.ndarray, mu: np.ndarray) -> float:
        """
        Compute Poisson log-likelihood.
        
        Parameters
        ----------
        y : ndarray of shape (n_samples,)
            Observed counts
        mu : ndarray of shape (n_samples,)
            Predicted rates
            
        Returns
        -------
        log_likelihood : float
            Poisson log-likelihood value
        """
        # Avoid log(0) and overflow in exp
        mu_safe = np.clip(mu, 1e-10, 1e10)
        
        # Compute log-likelihood: sum(y * log(mu) - mu - log(y!))
        # We ignore the log(y!) term as it doesn't depend on parameters
        return np.sum(y * np.log(mu_safe) - mu_safe)
    
    @staticmethod
    def poisson_deviance(y: np.ndarray, mu: np.ndarray) -> float:
        """
        Compute Poisson deviance.
        
        Parameters
        ----------
        y : ndarray of shape (n_samples,)
            Observed counts
        mu : ndarray of shape (n_samples,)
            Predicted rates
            
        Returns
        -------
        deviance : float
            Poisson deviance
        """
        mu_safe = np.clip(mu, 1e-10, 1e10)
        
        # Handle zero counts
        mask = y > 0
        deviance = np.zeros_like(y)
        
        if np.any(mask):
            deviance[mask] = y[mask] * np.log(y[mask] / mu_safe[mask])
        
        deviance = deviance - (y - mu_safe)
        return 2 * np.sum(deviance)
    
    @staticmethod
    def poisson_gradient(X: np.ndarray, y: np.ndarray, linear_pred: np.ndarray) -> np.ndarray:
        """
        Compute gradient of negative Poisson log-likelihood.
        
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Design matrix
        y : ndarray of shape (n_samples,)
            Observed counts
        linear_pred : ndarray of shape (n_samples,)
            Linear predictor (X @ coef)
            
        Returns
        -------
        gradient : ndarray of shape (n_features,)
            Gradient vector
        """
        # Clip to avoid overflow
        linear_pred_safe = np.clip(linear_pred, -20, 20)
        mu = np.exp(linear_pred_safe)
        return X.T @ (mu - y)


class ConvergenceMixin:
    """
    Mixin class providing convergence monitoring utilities.
    """
    
    @staticmethod
    def check_convergence_criteria(
        loss_history: List[float],
        coef_history: List[np.ndarray],
        tol: float,
        method: str = 'loss'
    ) -> bool:
        """
        Check various convergence criteria.
        
        Parameters
        ----------
        loss_history : list of float
            History of loss values
        coef_history : list of ndarray
            History of coefficient vectors
        tol : float
            Convergence tolerance
        method : str, default='loss'
            Convergence criterion method
            
        Returns
        -------
        converged : bool
            Whether convergence criterion is met
        """
        if len(loss_history) < 2:
            return False
        
        if method == 'loss':
            # Relative change in loss
            rel_change = abs(loss_history[-1] - loss_history[-2]) / (abs(loss_history[-2]) + 1e-10)
            return rel_change < tol
        
        elif method == 'gradient':
            # This would require gradient history (not implemented here)
            raise NotImplementedError("Gradient-based convergence not implemented")
        
        elif method == 'coefficients':
            if len(coef_history) < 2:
                return False
            # Relative change in coefficients
            coef_change = np.linalg.norm(coef_history[-1] - coef_history[-2])
            coef_norm = np.linalg.norm(coef_history[-2]) + 1e-10
            return (coef_change / coef_norm) < tol
        
        else:
            raise ValueError(f"Unknown convergence method: {method}")
    
    @staticmethod
    def detect_divergence(
        loss_history: List[float],
        window_size: int = 10,
        threshold: float = 1e6
    ) -> bool:
        """
        Detect if optimization is diverging.
        
        Parameters
        ----------
        loss_history : list of float
            History of loss values
        window_size : int, default=10
            Window size for trend analysis
        threshold : float, default=1e6
            Absolute threshold for divergence
            
        Returns
        -------
        diverged : bool
            Whether optimization appears to be diverging
        """
        if len(loss_history) < window_size:
            return False
        
        # Check for absolute divergence
        if loss_history[-1] > threshold:
            return True
        
        # Check for consistent increase over window
        recent_losses = loss_history[-window_size:]
        if len(recent_losses) > 1:
            trend = np.polyfit(range(len(recent_losses)), recent_losses, 1)[0]
            if trend > 0 and recent_losses[-1] > 2 * recent_losses[0]:
                return True
        
        return False


class ValidationMixin:
    """
    Mixin class providing common validation utilities.
    """
    
    @staticmethod
    def validate_positive_parameter(value: float, name: str) -> None:
        """Validate that a parameter is positive."""
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")
    
    @staticmethod
    def validate_non_negative_parameter(value: float, name: str) -> None:
        """Validate that a parameter is non-negative."""
        if value < 0:
            raise ValueError(f"{name} must be non-negative, got {value}")
    
    @staticmethod
    def validate_probability_parameter(value: float, name: str) -> None:
        """Validate that a parameter is a valid probability."""
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1, got {value}")
    
    @staticmethod
    def validate_integer_parameter(value: int, name: str, minimum: int = 1) -> None:
        """Validate that a parameter is a valid integer."""
        if not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}, got {value}")
    
    @staticmethod
    def warn_negative_targets(y: np.ndarray) -> None:
        """Issue warning for negative target values in Poisson regression."""
        if np.any(y < 0):
            warnings.warn(
                "Negative values detected in target. Poisson regression expects "
                "non-negative count data.",
                UserWarning
            )
    
    @staticmethod
    def warn_non_integer_targets(y: np.ndarray) -> None:
        """Issue warning for non-integer target values in Poisson regression."""
        if not np.allclose(y, np.round(y)):
            warnings.warn(
                "Non-integer values detected in target. Poisson regression typically "
                "expects count data (integers).",
                UserWarning
            )


# Type aliases for better code documentation
ArrayLike = Union[np.ndarray, List[float]]
OptimizationState = Dict[str, Any]
ConvergenceInfo = Dict[str, Union[bool, float, int]]


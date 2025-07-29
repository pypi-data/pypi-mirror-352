"""
Adaptive Momentum Gradient Descent (AMGD) Optimizer

This module implements the AMGD algorithm as described in:
"Adaptive Momentum Gradient Descent: A New Algorithm in Regularized Poisson Regression"
by Ibrahim Bakari and M. Revan Özkale
"""

import numpy as np
import warnings
from typing import Optional, Union, Literal, Tuple, Dict, Any
from sklearn.base import BaseEstimator
from ..utils.validation import check_array, check_X_y


class AMGDOptimizer(BaseEstimator):
    """
    Adaptive Momentum Gradient Descent optimizer for regularized regression.
    
    AMGD integrates adaptive learning rates, momentum updates, and adaptive 
    soft-thresholding specifically designed for regularized Poisson regression.
    
    Parameters
    ----------
    learning_rate : float, default=0.01
        Initial learning rate (α in the paper)
    momentum_beta1 : float, default=0.9
        Exponential decay rate for first moment estimates (ζ₁ in the paper)
    momentum_beta2 : float, default=0.999
        Exponential decay rate for second moment estimates (ζ₂ in the paper)
    lambda1 : float, default=0.01
        L1 regularization parameter for Lasso penalty
    lambda2 : float, default=0.01
        L2 regularization parameter for Ridge penalty
    penalty : {'l1', 'l2', 'elasticnet'}, default='l1'
        Regularization penalty type
    decay_rate : float, default=1e-4
        Learning rate decay factor (η in the paper)
    gradient_clip : float, default=5.0
        Maximum allowed gradient magnitude (T in the paper)
    max_iter : int, default=1000
        Maximum number of iterations
    tol : float, default=1e-6
        Tolerance for convergence
    epsilon : float, default=1e-8
        Small constant for numerical stability (ε in the paper)
    random_state : int, RandomState instance or None, default=None
        Random state for reproducibility
    verbose : bool, default=False
        Whether to print convergence information
        
    Attributes
    ----------
    coef_ : ndarray of shape (n_features,)
        Fitted coefficients
    intercept_ : float
        Fitted intercept term
    n_iter_ : int
        Number of iterations run by the optimizer
    loss_history_ : list
        Loss values during optimization
    convergence_info_ : dict
        Information about convergence
        
    Examples
    --------
    >>> import numpy as np
    >>> from amgd import AMGDOptimizer
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.poisson(np.exp(X @ np.random.randn(10)))
    >>> optimizer = AMGDOptimizer(penalty='l1', lambda1=0.01)
    >>> optimizer.fit(X, y)
    AMGDOptimizer(...)
    >>> predictions = optimizer.predict(X)
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        momentum_beta1: float = 0.9,
        momentum_beta2: float = 0.999,
        lambda1: float = 0.01,
        lambda2: float = 0.01,
        penalty: Literal['l1', 'l2', 'elasticnet'] = 'l1',
        decay_rate: float = 1e-4,
        gradient_clip: float = 5.0,
        max_iter: int = 1000,
        tol: float = 1e-6,
        epsilon: float = 1e-8,
        random_state: Optional[int] = None,
        verbose: bool = False
    ):
        self.learning_rate = learning_rate
        self.momentum_beta1 = momentum_beta1
        self.momentum_beta2 = momentum_beta2
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.penalty = penalty
        self.decay_rate = decay_rate
        self.gradient_clip = gradient_clip
        self.max_iter = max_iter
        self.tol = tol
        self.epsilon = epsilon
        self.random_state = random_state
        self.verbose = verbose
        
    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if not 0 <= self.momentum_beta1 < 1:
            raise ValueError("momentum_beta1 must be in [0, 1)")
        if not 0 <= self.momentum_beta2 < 1:
            raise ValueError("momentum_beta2 must be in [0, 1)")
        if self.lambda1 < 0 or self.lambda2 < 0:
            raise ValueError("Regularization parameters must be non-negative")
        if self.penalty not in ['l1', 'l2', 'elasticnet']:
            raise ValueError("penalty must be 'l1', 'l2', or 'elasticnet'")
            
    def _initialize_parameters(self, n_features: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Initialize optimization parameters."""
        np.random.seed(self.random_state)
        
        # Initialize coefficients
        beta = np.random.normal(0, 0.01, n_features)
        
        # Initialize momentum terms
        m = np.zeros(n_features)
        v = np.zeros(n_features)
        
        return beta, m, v
        
    def _clip_gradients(self, gradients: np.ndarray) -> np.ndarray:
        """Apply gradient clipping."""
        grad_norm = np.linalg.norm(gradients)
        if grad_norm > self.gradient_clip:
            gradients = gradients * (self.gradient_clip / grad_norm)
        return gradients
        
    def _compute_poisson_gradient(self, X: np.ndarray, y: np.ndarray, beta: np.ndarray) -> np.ndarray:
        """Compute gradient of negative Poisson log-likelihood."""
        linear_pred = X @ beta
        # Clip linear predictor to prevent overflow
        linear_pred = np.clip(linear_pred, -20, 20)
        mu = np.exp(linear_pred)
        gradient = X.T @ (mu - y)
        return gradient
        
    def _compute_regularization_gradient(self, beta: np.ndarray) -> np.ndarray:
        """Compute gradient of regularization term."""
        if self.penalty == 'l1':
            return np.zeros_like(beta)  # L1 handled in soft-thresholding
        elif self.penalty == 'l2':
            return self.lambda2 * beta
        elif self.penalty == 'elasticnet':
            return self.lambda2 * beta  # L1 part handled in soft-thresholding
        
    def _adaptive_soft_threshold(self, beta: np.ndarray, alpha_t: float) -> np.ndarray:
        """
        Apply adaptive soft-thresholding operation.
        
        This is the key innovation of AMGD, implementing Equation (6) from the paper:
        β_{t+1} = sign(β_t) · max(|β_t| - αₜλ/(|β_t| + ε), 0)
        """
        if self.penalty in ['l1', 'elasticnet']:
            denom = np.abs(beta) + 0.01  # Small constant to avoid division by zero
            threshold = alpha_t * self.lambda1 / denom
            beta = np.sign(beta) * np.maximum(np.abs(beta) - threshold, 0)
        return beta
        
    def _compute_loss(self, X: np.ndarray, y: np.ndarray, beta: np.ndarray) -> float:
        """Compute total loss (negative log-likelihood + regularization)."""
        linear_pred = X @ beta
        linear_pred = np.clip(linear_pred, -20, 20)
        mu = np.exp(linear_pred)
        
        # Negative log-likelihood
        log_likelihood = np.sum(y * linear_pred - mu)
        
        # Regularization terms
        reg_term = 0.0
        if self.penalty in ['l1', 'elasticnet']:
            reg_term += self.lambda1 * np.sum(np.abs(beta))
        if self.penalty in ['l2', 'elasticnet']:
            reg_term += 0.5 * self.lambda2 * np.sum(beta**2)
            
        return -log_likelihood + reg_term
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'AMGDOptimizer':
        """
        Fit the AMGD optimizer to training data.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data
        y : array-like of shape (n_samples,)
            Target values (counts for Poisson regression)
            
        Returns
        -------
        self : AMGDOptimizer
            Returns self for method chaining
        """
        self._validate_parameters()
        
        # Validate and convert input arrays
        X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)
        
        # Check that y contains non-negative integers (for Poisson)
        if np.any(y < 0):
            warnings.warn("Negative values in y detected. Poisson regression expects non-negative counts.")
            
        n_samples, n_features = X.shape
        
        # Initialize parameters
        beta, m, v = self._initialize_parameters(n_features)
        
        # Initialize tracking variables
        self.loss_history_ = []
        prev_loss = np.inf
        
        # Main optimization loop (Algorithm 1 from paper)
        for t in range(1, self.max_iter + 1):
            # Adaptive learning rate: αₜ = α/(1 + ηt)
            alpha_t = self.learning_rate / (1 + self.decay_rate * t)
            
            # Compute gradients
            grad_ll = self._compute_poisson_gradient(X, y, beta)
            grad_reg = self._compute_regularization_gradient(beta)
            grad = grad_ll + grad_reg
            
            # Apply gradient clipping
            grad = self._clip_gradients(grad)
            
            # Update momentum terms
            m = self.momentum_beta1 * m + (1 - self.momentum_beta1) * grad
            v = self.momentum_beta2 * v + (1 - self.momentum_beta2) * (grad**2)
            
            # Bias correction
            m_hat = m / (1 - self.momentum_beta1**t)
            v_hat = v / (1 - self.momentum_beta2**t)
            
            # Parameter update
            beta = beta - alpha_t * m_hat / (np.sqrt(v_hat) + self.epsilon)
            
            # Apply adaptive soft-thresholding
            beta = self._adaptive_soft_threshold(beta, alpha_t)
            
            # Compute and track loss
            current_loss = self._compute_loss(X, y, beta)
            self.loss_history_.append(current_loss)
            
            # Check convergence
            if abs(prev_loss - current_loss) < self.tol:
                if self.verbose:
                    print(f"Converged after {t} iterations")
                break
                
            prev_loss = current_loss
            
            if self.verbose and t % 100 == 0:
                print(f"Iteration {t}: Loss = {current_loss:.6f}")
        
        # Store results
        self.coef_ = beta
        self.intercept_ = 0.0  # No intercept for simplicity
        self.n_iter_ = t
        self.convergence_info_ = {
            'converged': abs(prev_loss - current_loss) < self.tol,
            'final_loss': current_loss,
            'n_iterations': t
        }
        
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the fitted model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data
            
        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Predicted values
        """
        if not hasattr(self, 'coef_'):
            raise ValueError("Model must be fitted before making predictions")
            
        X = check_array(X, accept_sparse=False)
        linear_pred = X @ self.coef_ + self.intercept_
        return np.exp(np.clip(linear_pred, -20, 20))
        
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return the coefficient of determination R² of the prediction.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples
        y : array-like of shape (n_samples,)
            True values
            
        Returns
        -------
        score : float
            R² score
        """
        y_pred = self.predict(X)
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean)**2)
        ss_res = np.sum((y - y_pred)**2)
        return 1 - (ss_res / ss_tot)
        
    def get_feature_importance(self) -> np.ndarray:
        """
        Get feature importance based on absolute coefficient values.
        
        Returns
        -------
        importance : ndarray of shape (n_features,)
            Feature importance scores
        """
        if not hasattr(self, 'coef_'):
            raise ValueError("Model must be fitted before getting feature importance")
        return np.abs(self.coef_)
        
    def get_sparsity(self) -> float:
        """
        Calculate the sparsity ratio (percentage of zero coefficients).
        
        Returns
        -------
        sparsity : float
            Sparsity ratio between 0 and 1
        """
        if not hasattr(self, 'coef_'):
            raise ValueError("Model must be fitted before calculating sparsity")
        return np.mean(np.abs(self.coef_) < 1e-8)
        
    def __repr__(self) -> str:
        """String representation of the optimizer."""
        params = [
            f"learning_rate={self.learning_rate}",
            f"penalty='{self.penalty}'",
            f"lambda1={self.lambda1}",
            f"lambda2={self.lambda2}"
        ]
        return f"AMGDOptimizer({', '.join(params)})"
        
"""
AMGD Poisson Regression implementation

This module provides a high-level interface for Poisson regression using AMGD optimization.
"""

import numpy as np
from typing import Optional, Literal, Union
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import StandardScaler

from ..core.amgd_optimizer import AMGDOptimizer
from ..utils.validation import check_X_y, check_array
from ..utils.metrics import mean_absolute_error, mean_squared_error, poisson_deviance


class AMGDPoissonRegressor(BaseEstimator, RegressorMixin):
    """
    Poisson regression using Adaptive Momentum Gradient Descent (AMGD).
    
    This estimator implements Poisson regression with L1, L2, or Elastic Net 
    regularization using the AMGD optimization algorithm. It's specifically 
    designed for count data and high-dimensional sparse datasets.
    
    Parameters
    ----------
    alpha : float, default=1.0
        Constant that multiplies the penalty terms
    l1_ratio : float, default=0.5
        The Elastic Net mixing parameter, with 0 <= l1_ratio <= 1.
        For l1_ratio = 0 the penalty is an L2 penalty.
        For l1_ratio = 1 it is an L1 penalty.
        For 0 < l1_ratio < 1, the penalty is a combination of L1 and L2.
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model
    normalize : bool, default=False
        Whether to normalize the features before fitting
    max_iter : int, default=1000
        Maximum number of iterations for the optimization algorithm
    tol : float, default=1e-6
        Tolerance for the optimization convergence
    learning_rate : float, default=0.01
        Learning rate for the AMGD optimizer
    random_state : int, RandomState instance or None, default=None
        Random state for reproducible results
    verbose : bool, default=False
        Whether to print convergence information
        
    Attributes
    ----------
    coef_ : ndarray of shape (n_features,)
        Estimated coefficients for the linear predictor
    intercept_ : float
        Estimated intercept (bias) term
    n_iter_ : int
        Number of iterations run by the optimizer
    optimizer_ : AMGDOptimizer
        The underlying AMGD optimizer instance
    scaler_ : StandardScaler or None
        Feature scaler (if normalize=True)
        
    Examples
    --------
    >>> import numpy as np
    >>> from amgd import AMGDPoissonRegressor
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.poisson(np.exp(X @ np.random.randn(10)))
    >>> model = AMGDPoissonRegressor(alpha=0.1, l1_ratio=0.7)
    >>> model.fit(X, y)
    AMGDPoissonRegressor(alpha=0.1, l1_ratio=0.7)
    >>> predictions = model.predict(X)
    >>> print(f"Sparsity: {model.get_sparsity():.2%}")
    """
    
    def __init__(
        self,
        alpha: float = 1.0,
        l1_ratio: float = 0.5,
        fit_intercept: bool = True,
        normalize: bool = False,
        max_iter: int = 1000,
        tol: float = 1e-6,
        learning_rate: float = 0.01,
        random_state: Optional[int] = None,
        verbose: bool = False
    ):
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.max_iter = max_iter
        self.tol = tol
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.verbose = verbose
        
    def _validate_params(self):
        """Validate input parameters."""
        if self.alpha < 0:
            raise ValueError("alpha must be non-negative")
        if not 0 <= self.l1_ratio <= 1:
            raise ValueError("l1_ratio must be between 0 and 1")
        if self.max_iter <= 0:
            raise ValueError("max_iter must be positive")
        if self.tol <= 0:
            raise ValueError("tol must be positive")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
            
    def _determine_penalty_type(self) -> str:
        """Determine penalty type based on l1_ratio."""
        if self.l1_ratio == 0:
            return 'l2'
        elif self.l1_ratio == 1:
            return 'l1'
        else:
            return 'elasticnet'
            
    def _prepare_data(self, X: np.ndarray, y: Optional[np.ndarray] = None, 
                     training: bool = True) -> Union[np.ndarray, tuple]:
        """Prepare data for training or prediction."""
        X = check_array(X, accept_sparse=False)
        
        if training and y is not None:
            X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)
            
            # Validate that y contains non-negative values
            if np.any(y < 0):
                raise ValueError("Poisson regression requires non-negative target values")
                
        # Handle intercept
        if self.fit_intercept:
            X = np.column_stack([np.ones(X.shape[0]), X])
            
        # Handle normalization
        if training and self.normalize:
            self.scaler_ = StandardScaler()
            if self.fit_intercept:
                # Don't scale the intercept column
                X[:, 1:] = self.scaler_.fit_transform(X[:, 1:])
            else:
                X = self.scaler_.fit_transform(X)
        elif not training and self.normalize and hasattr(self, 'scaler_'):
            if self.fit_intercept:
                X[:, 1:] = self.scaler_.transform(X[:, 1:])
            else:
                X = self.scaler_.transform(X)
                
        if training and y is not None:
            return X, y
        else:
            return X
            
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'AMGDPoissonRegressor':
        """
        Fit the Poisson regression model using AMGD optimization.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data
        y : array-like of shape (n_samples,)
            Target counts
            
        Returns
        -------
        self : AMGDPoissonRegressor
            Returns self for method chaining
        """
        self._validate_params()
        
        # Prepare data
        X, y = self._prepare_data(X, y, training=True)
        
        # Determine penalty type and regularization parameters
        penalty_type = self._determine_penalty_type()
        lambda1 = self.alpha * self.l1_ratio
        lambda2 = self.alpha * (1 - self.l1_ratio)
        
        # Create and configure optimizer
        self.optimizer_ = AMGDOptimizer(
            learning_rate=self.learning_rate,
            lambda1=lambda1,
            lambda2=lambda2,
            penalty=penalty_type,
            max_iter=self.max_iter,
            tol=self.tol,
            random_state=self.random_state,
            verbose=self.verbose
        )
        
        # Fit the optimizer
        self.optimizer_.fit(X, y)
        
        # Extract results
        if self.fit_intercept:
            self.intercept_ = self.optimizer_.coef_[0]
            self.coef_ = self.optimizer_.coef_[1:]
        else:
            self.intercept_ = 0.0
            self.coef_ = self.optimizer_.coef_
            
        self.n_iter_ = self.optimizer_.n_iter_
        
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict count values for samples in X.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input samples
            
        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Predicted count values
        """
        check_is_fitted(self)
        
        # Prepare data
        X = self._prepare_data(X, training=False)
        
        # Make predictions using the optimizer
        return self.optimizer_.predict(X)
        
    def predict_log_rate(self, X: np.ndarray) -> np.ndarray:
        """
        Predict log of the expected count (linear predictor).
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input samples
            
        Returns
        -------
        log_rate : ndarray of shape (n_samples,)
            Predicted log rates
        """
        check_is_fitted(self)
        
        X = check_array(X, accept_sparse=False)
        
        # Apply normalization if fitted
        if self.normalize and hasattr(self, 'scaler_'):
            X = self.scaler_.transform(X)
            
        return X @ self.coef_ + self.intercept_
        
    def score(self, X: np.ndarray, y: np.ndarray, 
              metric: Literal['deviance', 'mae', 'mse'] = 'deviance') -> float:
        """
        Return the score using the specified metric.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples
        y : array-like of shape (n_samples,)
            True values
        metric : {'deviance', 'mae', 'mse'}, default='deviance'
            Scoring metric to use
            
        Returns
        -------
        score : float
            Score value (lower is better for all metrics)
        """
        y_pred = self.predict(X)
        
        if metric == 'deviance':
            return poisson_deviance(y, y_pred)
        elif metric == 'mae':
            return mean_absolute_error(y, y_pred)
        elif metric == 'mse':
            return mean_squared_error(y, y_pred)
        else:
            raise ValueError(f"Unknown metric: {metric}")
            
    def get_feature_importance(self) -> np.ndarray:
        """
        Get feature importance based on absolute coefficient values.
        
        Returns
        -------
        importance : ndarray of shape (n_features,)
            Feature importance scores
        """
        check_is_fitted(self)
        return np.abs(self.coef_)
        
    def get_sparsity(self) -> float:
        """
        Calculate the sparsity ratio (percentage of zero coefficients).
        
        Returns
        -------
        sparsity : float
            Sparsity ratio between 0 and 1
        """
        check_is_fitted(self)
        return np.mean(np.abs(self.coef_) < 1e-8)
        
    def get_convergence_info(self) -> dict:
        """
        Get information about the optimization convergence.
        
        Returns
        -------
        info : dict
            Dictionary containing convergence information
        """
        check_is_fitted(self)
        return self.optimizer_.convergence_info_
        
    def plot_convergence(self, ax=None):
        """
        Plot the convergence history.
        
        Parameters
        ----------
        ax : matplotlib axes, optional
            Axes to plot on. If None, creates new figure.
            
        Returns
        -------
        ax : matplotlib axes
            The axes object with the plot
        """
        check_is_fitted(self)
        
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib is required for plotting")
            
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            
        ax.plot(self.optimizer_.loss_history_)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Loss')
        ax.set_title('AMGD Convergence History')
        ax.grid(True, alpha=0.3)
        
        return ax
        
    def __repr__(self) -> str:
        """String representation of the regressor."""
        params = []
        if self.alpha != 1.0:
            params.append(f"alpha={self.alpha}")
        if self.l1_ratio != 0.5:
            params.append(f"l1_ratio={self.l1_ratio}")
        if not self.fit_intercept:
            params.append("fit_intercept=False")
        if self.normalize:
            params.append("normalize=True")
            
        param_str = ", ".join(params) if params else ""
        return f"AMGDPoissonRegressor({param_str})"
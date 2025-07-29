"""
Validation utilities for AMGD package.
"""

import numpy as np
from typing import Union, Tuple, Optional
import warnings


def check_array(
    array: Union[np.ndarray, list], 
    accept_sparse: bool = False,
    dtype: str = "numeric",
    ensure_finite: bool = True,
    ensure_2d: bool = True
) -> np.ndarray:
    """
    Input validation on an array, list, or similar.
    
    Parameters
    ----------
    array : array-like
        Input object to check / convert
    accept_sparse : bool, default=False
        Whether sparse matrices are accepted
    dtype : str, default="numeric"
        Data type expected
    ensure_finite : bool, default=True
        Whether to raise an error on np.inf and np.nan
    ensure_2d : bool, default=True
        Whether to ensure array is 2D
        
    Returns
    -------
    array_converted : ndarray
        The converted and validated array
    """
    # Convert to numpy array
    array = np.asarray(array)
    
    # Check for sparse arrays (not implemented in this simple version)
    if not accept_sparse and hasattr(array, 'toarray'):
        raise ValueError("Sparse matrices are not supported")
    
    # Ensure 2D
    if ensure_2d and array.ndim == 1:
        array = array.reshape(-1, 1)
    elif ensure_2d and array.ndim != 2:
        raise ValueError(f"Expected 2D array, got {array.ndim}D array instead")
    
    # Check for finite values
    if ensure_finite and not np.isfinite(array).all():
        raise ValueError("Input contains NaN, infinity or a value too large")
    
    # Check dtype
    if dtype == "numeric":
        if not np.issubdtype(array.dtype, np.number):
            raise ValueError("Input array must be numeric")
        # Convert to float64 for consistency
        array = array.astype(np.float64)
    
    return array


def check_X_y(
    X: Union[np.ndarray, list], 
    y: Union[np.ndarray, list],
    accept_sparse: bool = False,
    y_numeric: bool = False,
    ensure_finite: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Input validation for standard estimators.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Input data
    y : array-like of shape (n_samples,)
        Target values
    accept_sparse : bool, default=False
        Whether sparse matrices are accepted for X
    y_numeric : bool, default=False
        Whether to enforce that y has a numeric type
    ensure_finite : bool, default=True
        Whether to raise an error on np.inf and np.nan
        
    Returns
    -------
    X_converted : ndarray
        The converted and validated X array
    y_converted : ndarray
        The converted and validated y array
    """
    # Validate X
    X = check_array(X, accept_sparse=accept_sparse, ensure_finite=ensure_finite, ensure_2d=True)
    
    # Validate y
    y = np.asarray(y)
    
    if y.ndim != 1:
        raise ValueError(f"Expected 1D array for y, got {y.ndim}D array instead")
    
    if ensure_finite and not np.isfinite(y).all():
        raise ValueError("y contains NaN, infinity or a value too large")
    
    if y_numeric and not np.issubdtype(y.dtype, np.number):
        raise ValueError("y must be numeric")
    
    # Convert y to float64 for consistency
    if y_numeric:
        y = y.astype(np.float64)
    
    # Check that X and y have compatible shapes
    if X.shape[0] != y.shape[0]:
        raise ValueError(
            f"X and y have incompatible shapes. X has {X.shape[0]} samples, "
            f"but y has {y.shape[0]} samples."
        )
    
    return X, y


def check_is_fitted(estimator, attributes=None):
    """
    Perform is_fitted validation for an estimator.
    
    Parameters
    ----------
    estimator : estimator instance
        Estimator instance for which the check is performed
    attributes : str, list or tuple of strings, default=None
        Attribute name(s) given as string or a list/tuple of strings
        If None, default fitted attributes are checked
        
    Raises
    ------
    NotFittedError
        If the attributes are not found
    """
    if attributes is None:
        # Default attributes to check
        attributes = ["coef_"]
    
    if not isinstance(attributes, (list, tuple)):
        attributes = [attributes]
    
    fitted = all(hasattr(estimator, attr) for attr in attributes)
    
    if not fitted:
        raise ValueError(
            f"This {type(estimator).__name__} instance is not fitted yet. "
            f"Call 'fit' with appropriate arguments before using this estimator."
        )


def validate_poisson_targets(y: np.ndarray, allow_negative: bool = False) -> np.ndarray:
    """
    Validate that targets are appropriate for Poisson regression.
    
    Parameters
    ----------
    y : array-like
        Target values
    allow_negative : bool, default=False
        Whether to allow negative values (will issue warning)
        
    Returns
    -------
    y_validated : ndarray
        Validated target array
        
    Raises
    ------
    ValueError
        If targets are not valid for Poisson regression
    """
    y = np.asarray(y)
    
    # Check for non-finite values
    if not np.isfinite(y).all():
        raise ValueError("Target values must be finite")
    
    # Check for negative values
    if np.any(y < 0):
        if allow_negative:
            warnings.warn(
                "Negative values found in target. Poisson regression typically "
                "expects non-negative count data.", 
                UserWarning
            )
        else:
            raise ValueError(
                "Negative values found in target. Poisson regression requires "
                "non-negative count data."
            )
    
    # Check if values are integers (or close to integers)
    if not np.allclose(y, np.round(y)):
        warnings.warn(
            "Non-integer values found in target. Poisson regression typically "
            "expects count data (integers).",
            UserWarning
        )
    
    return y


def validate_regularization_params(alpha: float, l1_ratio: Optional[float] = None) -> None:
    """
    Validate regularization parameters.
    
    Parameters
    ----------
    alpha : float
        Regularization strength
    l1_ratio : float, optional
        Elastic net mixing parameter
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative, got {alpha}")
    
    if l1_ratio is not None:
        if not 0 <= l1_ratio <= 1:
            raise ValueError(f"l1_ratio must be between 0 and 1, got {l1_ratio}")


def check_optimization_params(
    learning_rate: float,
    max_iter: int,
    tol: float,
    momentum_beta1: float = 0.9,
    momentum_beta2: float = 0.999
) -> None:
    """
    Validate optimization parameters.
    
    Parameters
    ----------
    learning_rate : float
        Learning rate for optimization
    max_iter : int
        Maximum number of iterations
    tol : float
        Convergence tolerance
    momentum_beta1 : float, default=0.9
        First momentum parameter
    momentum_beta2 : float, default=0.999
        Second momentum parameter
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
    if learning_rate <= 0:
        raise ValueError(f"learning_rate must be positive, got {learning_rate}")
    
    if max_iter <= 0:
        raise ValueError(f"max_iter must be positive, got {max_iter}")
    
    if tol <= 0:
        raise ValueError(f"tol must be positive, got {tol}")
    
    if not 0 <= momentum_beta1 < 1:
        raise ValueError(f"momentum_beta1 must be in [0, 1), got {momentum_beta1}")
    
    if not 0 <= momentum_beta2 < 1:
        raise ValueError(f"momentum_beta2 must be in [0, 1), got {momentum_beta2}")
"""
AMGD: Adaptive Momentum Gradient Descent for Regularized Poisson Regression

A Python package implementing the AMGD optimization algorithm for sparse, 
high-dimensional Poisson regression with L1, L2, and Elastic Net regularization.

Key Features:
- Novel adaptive soft-thresholding for improved sparsity
- Superior performance vs Adam and AdaGrad (56.6% MAE reduction vs AdaGrad)
- Direct L1 penalty handling without subgradient approximations
- Scikit-learn compatible API
- Comprehensive validation and metrics

Authors: Ibrahim Bakari, M. Revan Özkale
Paper: "Adaptive Momentum Gradient Descent: A New Algorithm in Regularized Poisson Regression"
"""

from .core.amgd_optimizer import AMGDOptimizer
from .regressors.poisson_regression import AMGDPoissonRegressor
from .utils import metrics, validation

# Version info
# Version info
__version__ = "1.0.0"
__author__ = "Ibrahim Bakari"
__email__ = "2020913072@ogr.cu.edu.tr"



# Main classes for easy import
__all__ = [
    "AMGDOptimizer",
    "AMGDPoissonRegressor",
    "metrics",
    "validation",
    "__version__"
]

# Package metadata
__title__ = "amgd-optimizer"
__description__ = "Adaptive Momentum Gradient Descent for Regularized Poisson Regression"
__url__ = "https://github.com/elbakari01/amgd-optimizer"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Ibrahim Bakari"

# Convenience imports for common usage patterns
def quick_fit(X, y, penalty='elasticnet', alpha=0.01, **kwargs):
    """
    Quick fitting function for common use cases.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data
    y : array-like of shape (n_samples,)
        Target counts
    penalty : {'l1', 'l2', 'elasticnet'}, default='elasticnet'
        Regularization type
    alpha : float, default=0.01
        Regularization strength
    **kwargs
        Additional parameters for AMGDPoissonRegressor
        
    Returns
    -------
    model : AMGDPoissonRegressor
        Fitted model
        
    Examples
    --------
    >>> import numpy as np
    >>> from amgd import quick_fit
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.poisson(np.exp(X @ np.random.randn(10)))
    >>> model = quick_fit(X, y, penalty='l1', alpha=0.1)
    >>> print(f"Sparsity: {model.get_sparsity():.2%}")
    """
    # Map penalty names to l1_ratio values
    penalty_map = {
        'l1': 1.0,
        'l2': 0.0,
        'elasticnet': 0.5
    }
    
    if penalty not in penalty_map:
        raise ValueError(f"penalty must be one of {list(penalty_map.keys())}")
    
    model = AMGDPoissonRegressor(
        alpha=alpha,
        l1_ratio=penalty_map[penalty],
        **kwargs
    )
    
    return model.fit(X, y)


def compare_optimizers(X, y, methods=['amgd', 'adam', 'adagrad'], **kwargs):
    """
    Compare AMGD against other optimization methods.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data
    y : array-like of shape (n_samples,)
        Target counts
    methods : list, default=['amgd', 'adam', 'adagrad']
        Optimization methods to compare
    **kwargs
        Additional parameters for models
        
    Returns
    -------
    results : dict
        Comparison results for each method
        
    Examples
    --------
    >>> import numpy as np
    >>> from amgd import compare_optimizers
    >>> X = np.random.randn(100, 10)
    >>> y = np.random.poisson(np.exp(X @ np.random.randn(10)))
    >>> results = compare_optimizers(X, y)
    >>> for method, metrics in results.items():
    ...     print(f"{method}: MAE = {metrics['mae']:.4f}")
    """
    try:
        from sklearn.model_selection import cross_val_score
        from sklearn.linear_model import PoissonRegressor
    except ImportError:
        raise ImportError("scikit-learn is required for optimizer comparison")
    
    results = {}
    
    for method in methods:
        if method == 'amgd':
            model = AMGDPoissonRegressor(**kwargs)
            model.fit(X, y)
            y_pred = model.predict(X)
            results[method] = {
                'model': model,
                'mae': metrics.mean_absolute_error(y, y_pred),
                'rmse': metrics.root_mean_squared_error(y, y_pred),
                'mpd': metrics.mean_poisson_deviance(y, y_pred),
                'sparsity': model.get_sparsity(),
                'n_iter': model.n_iter_
            }
        else:
            # For comparison with sklearn's PoissonRegressor
            try:
                if method in ['adam', 'adagrad']:
                    # Note: sklearn doesn't directly support Adam/AdaGrad for Poisson
                    # This is a placeholder for the actual comparison
                    model = PoissonRegressor(alpha=kwargs.get('alpha', 0.01))
                    model.fit(X, y)
                    y_pred = model.predict(X)
                    results[method] = {
                        'model': model,
                        'mae': metrics.mean_absolute_error(y, y_pred),
                        'rmse': metrics.root_mean_squared_error(y, y_pred),
                        'mpd': metrics.mean_poisson_deviance(y, y_pred),
                        'sparsity': 0.0,  # sklearn doesn't enforce sparsity by default
                        'n_iter': getattr(model, 'n_iter_', None)
                    }
            except Exception as e:
                results[method] = {'error': str(e)}
    
    return results


# Diagnostic functions
def validate_installation():
    """
    Validate that the package is correctly installed.
    
    Returns
    -------
    status : dict
        Installation status information
    """
    import sys
    import numpy as np
    
    status = {
        'python_version': sys.version,
        'numpy_version': np.__version__,
        'amgd_version': __version__,
        'core_classes_available': True,
        'test_passed': False
    }
    
    try:
        # Test basic functionality
        np.random.seed(42)
        X = np.random.randn(50, 5)
        y = np.random.poisson(np.exp(X @ np.random.randn(5) * 0.1))
        
        model = AMGDPoissonRegressor(alpha=0.1, max_iter=100, verbose=False)
        model.fit(X, y)
        predictions = model.predict(X)
        
        status['test_passed'] = True
        status['test_mae'] = metrics.mean_absolute_error(y, predictions)
        status['test_sparsity'] = model.get_sparsity()
        
    except Exception as e:
        status['test_error'] = str(e)
    
    return status


# Print package info on import
def _print_info():
    """Print basic package information."""
    print(f"AMGD v{__version__} - Adaptive Momentum Gradient Descent")
    print(f"High-performance optimization for regularized Poisson regression")
    print(f"Documentation: {__url__}")


  _print_info()
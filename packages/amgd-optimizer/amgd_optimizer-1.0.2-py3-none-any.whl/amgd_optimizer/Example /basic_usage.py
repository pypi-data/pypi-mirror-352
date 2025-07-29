"""
Basic usage examples for AMGD-Python package.

This script demonstrates the key functionality of the AMGD package
for regularized Poisson regression.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_regression

# Import AMGD classes
from amgd import AMGDPoissonRegressor, AMGDOptimizer, quick_fit
from amgd.utils.metrics import compute_metrics_summary


def generate_poisson_data(n_samples=1000, n_features=20, n_informative=5, noise=0.1, random_state=42):
    """Generate synthetic Poisson regression data."""
    np.random.seed(random_state)
    
    # Generate base regression data
    X, y_continuous = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        noise=noise,
        random_state=random_state
    )
    
    # Convert to Poisson counts
    # Scale down to avoid overflow in exp
    y_continuous = y_continuous / np.std(y_continuous) * 0.5
    rates = np.exp(y_continuous - np.max(y_continuous) + 2)  # Ensure positive rates
    y_poisson = np.random.poisson(rates)
    
    return X, y_poisson


def example_1_basic_fitting():
    """Example 1: Basic model fitting and prediction."""
    print("="*60)
    print("EXAMPLE 1: Basic Model Fitting")
    print("="*60)
    
    # Generate data
    X, y = generate_poisson_data(n_samples=500, n_features=15, n_informative=8)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print(f"Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Target statistics: mean={np.mean(y_train):.2f}, std={np.std(y_train):.2f}")
    
    # Fit AMGD model
    model = AMGDPoissonRegressor(
        alpha=0.01,
        l1_ratio=0.7,  # 70% L1, 30% L2
        max_iter=1000,
        verbose=True
    )
    
    print("\nFitting AMGD model...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Compute metrics
    train_metrics = compute_metrics_summary(y_train, y_pred_train)
    test_metrics = compute_metrics_summary(y_test, y_pred_test)
    
    print(f"\nModel Results:")
    print(f"Convergence: {model.get_convergence_info()['converged']}")
    print(f"Iterations: {model.n_iter_}")
    print(f"Sparsity: {model.get_sparsity():.2%}")
    print(f"Active features: {np.sum(np.abs(model.coef_) > 1e-8)}/{len(model.coef_)}")
    
    print(f"\nTraining Metrics:")
    print(f"  MAE: {train_metrics['mae']:.4f}")
    print(f"  RMSE: {train_metrics['rmse']:.4f}")
    print(f"  R²: {train_metrics['r2']:.4f}")
    
    print(f"\nTest Metrics:")
    print(f"  MAE: {test_metrics['mae']:.4f}")
    print(f"  RMSE: {test_metrics['rmse']:.4f}")
    print(f"  R²: {test_metrics['r2']:.4f}")
    
    return model, X_test, y_test


def example_2_regularization_comparison():
    """Example 2: Compare different regularization types."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Regularization Comparison")
    print("="*60)
    
    # Generate data
    X, y = generate_poisson_data(n_samples=800, n_features=25, n_informative=10)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Test different regularization types
    regularizations = [
        ('Pure L1 (Lasso)', {'alpha': 0.01, 'l1_ratio': 1.0}),
        ('Pure L2 (Ridge)', {'alpha': 0.01, 'l1_ratio': 0.0}),
        ('Elastic Net (50/50)', {'alpha': 0.01, 'l1_ratio': 0.5}),
        ('Elastic Net (70/30)', {'alpha': 0.01, 'l1_ratio': 0.7}),
    ]
    
    results = []
    
    for name, params in regularizations:
        print(f"\nFitting {name}...")
        
        model = AMGDPoissonRegressor(**params, max_iter=500, verbose=False)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        metrics = compute_metrics_summary(y_test, y_pred)
        
        result = {
            'name': name,
            'model': model,
            'mae': metrics['mae'],
            'rmse': metrics['rmse'],
            'r2': metrics['r2'],
            'sparsity': model.get_sparsity(),
            'n_features': np.sum(np.abs(model.coef_) > 1e-8),
            'iterations': model.n_iter_
        }
        results.append(result)
        
        print(f"  MAE: {result['mae']:.4f}")
        print(f"  Sparsity: {result['sparsity']:.2%}")
        print(f"  Features: {result['n_features']}")
    
    # Summary table
    print(f"\n{'Method':<20} {'MAE':<8} {'RMSE':<8} {'R²':<8} {'Sparsity':<10} {'Features':<10}")
    print("-" * 75)
    for result in results:
        print(f"{result['name']:<20} {result['mae']:<8.4f} {result['rmse']:<8.4f} "
              f"{result['r2']:<8.4f} {result['sparsity']:<10.2%} {result['n_features']:<10}")
    
    return results


def example_3_feature_selection_path():
    """Example 3: Feature selection regularization path."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Feature Selection Path")
    print("="*60)
    
    # Generate data with known sparse structure
    X, y = generate_poisson_data(n_samples=600, n_features=30, n_informative=8)
    
    # Test different regularization strengths
    alphas = np.logspace(-3, 0, 15)  # From 0.001 to 1.0
    
    results = []
    for alpha in alphas:
        model = AMGDPoissonRegressor(alpha=alpha, l1_ratio=1.0, max_iter=300, verbose=False)
        model.fit(X, y)
        
        y_pred = model.predict(X)
        mae = np.mean(np.abs(y - y_pred))
        
        results.append({
            'alpha': alpha,
            'mae': mae,
            'sparsity': model.get_sparsity(),
            'n_features': np.sum(np.abs(model.coef_) > 1e-8),
            'coef': model.coef_.copy()
        })
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: MAE vs Regularization
    axes[0, 0].semilogx([r['alpha'] for r in results], [r['mae'] for r in results], 'o-')
    axes[0, 0].set_xlabel('Regularization Strength (α)')
    axes[0, 0].set_ylabel('Mean Absolute Error')
    axes[0, 0].set_title('Prediction Error vs Regularization')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Sparsity vs Regularization
    axes[0, 1].semilogx([r['alpha'] for r in results], [r['sparsity'] for r in results], 'o-', color='red')
    axes[0, 1].set_xlabel('Regularization Strength (α)')
    axes[0, 1].set_ylabel('Sparsity Ratio')
    axes[0, 1].set_title('Sparsity vs Regularization')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Number of features vs Regularization
    axes[1, 0].semilogx([r['alpha'] for r in results], [r['n_features'] for r in results], 'o-', color='green')
    axes[1, 0].set_xlabel('Regularization Strength (α)')
    axes[1, 0].set_ylabel('Number of Selected Features')
    axes[1, 0].set_title('Feature Count vs Regularization')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Coefficient paths
    coef_matrix = np.array([r['coef'] for r in results]).T
    for i in range(min(10, coef_matrix.shape[0])):  # Plot first 10 features
        axes[1, 1].semilogx([r['alpha'] for r in results], coef_matrix[i], alpha=0.7)
    axes[1, 1].set_xlabel('Regularization Strength (α)')
    axes[1, 1].set_ylabel('Coefficient Value')
    axes[1, 1].set_title('Coefficient Paths')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\nRegularization Path Summary:")
    print(f"Min MAE: {min(r['mae'] for r in results):.4f} at α={results[np.argmin([r['mae'] for r in results])]['alpha']:.4f}")
    print(f"Max sparsity: {max(r['sparsity'] for r in results):.2%}")
    print(f"Feature selection range: {min(r['n_features'] for r in results)} - {max(r['n_features'] for r in results)} features")
    
    return results


def example_4_quick_fit_convenience():
    """Example 4: Using convenience functions."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Convenience Functions")
    print("="*60)
    
    # Generate data
    X, y = generate_poisson_data(n_samples=400, n_features=15)
    
    print("Using quick_fit function for rapid prototyping...")
    
    # Quick fitting with different penalties
    models = {}
    for penalty in ['l1', 'l2', 'elasticnet']:
        print(f"\nFitting {penalty.upper()} model...")
        model = quick_fit(X, y, penalty=penalty, alpha=0.05, verbose=False)
        models[penalty] = model
        
        y_pred = model.predict(X)
        mae = np.mean(np.abs(y - y_pred))
        
        print(f"  MAE: {mae:.4f}")
        print(f"  Sparsity: {model.get_sparsity():.2%}")
        print(f"  Features: {np.sum(np.abs(model.coef_) > 1e-8)}")
        print(f"  Iterations: {model.n_iter_}")
    
    return models


def example_5_low_level_optimizer():
    """Example 5: Using the low-level optimizer directly."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Low-Level Optimizer Usage")
    print("="*60)
    
    # Generate data
    X, y = generate_poisson_data(n_samples=300, n_features=12)
    
    print("Using AMGDOptimizer directly for custom applications...")
    
    # Create optimizer with custom parameters
    optimizer = AMGDOptimizer(
        learning_rate=0.02,
        momentum_beta1=0.95,     # Higher momentum
        momentum_beta2=0.999,
        lambda1=0.01,            # L1 regularization
        lambda2=0.001,           # L2 regularization
        penalty='elasticnet',
        decay_rate=5e-4,         # Learning rate decay
        gradient_clip=3.0,       # Gradient clipping
        max_iter=500,
        tol=1e-7,
        verbose=True
    )
    
    # Fit the optimizer
    optimizer.fit(X, y)
    
    # Get results
    coefficients = optimizer.coef_
    predictions = optimizer.predict(X)
    
    print(f"\nOptimizer Results:")
    print(f"Convergence: {optimizer.convergence_info_['converged']}")
    print(f"Final loss: {optimizer.convergence_info_['final_loss']:.6f}")
    print(f"Iterations: {optimizer.n_iter_}")
    print(f"Feature importance: {optimizer.get_feature_importance()}")
    print(f"Sparsity: {optimizer.get_sparsity():.2%}")
    
    # Plot convergence
    plt.figure(figsize=(10, 6))
    plt.plot(optimizer.loss_history_)
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.title('AMGD Convergence History')
    plt.grid(True, alpha=0.3)
    plt.show()
    
    return optimizer


def main():
    """Run all examples."""
    print("AMGD-Python: Comprehensive Usage Examples")
    print("==========================================")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    try:
        # Run examples
        model1, X_test, y_test = example_1_basic_fitting()
        results2 = example_2_regularization_comparison()
        results3 = example_3_feature_selection_path()
        models4 = example_4_quick_fit_convenience()
        optimizer5 = example_5_low_level_optimizer()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Final summary
        print(f"\nPackage validation:")
        from amgd import validate_installation
        status = validate_installation()
        print(f"Installation status: {'✓ PASSED' if status['test_passed'] else '✗ FAILED'}")
        if status['test_passed']:
            print(f"Test MAE: {status['test_mae']:.4f}")
            print(f"Test sparsity: {status['test_sparsity']:.2%}")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
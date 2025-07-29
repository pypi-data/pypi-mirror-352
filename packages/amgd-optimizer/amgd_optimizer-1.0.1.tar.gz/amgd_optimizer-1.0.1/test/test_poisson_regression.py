"""
Tests for AMGDPoissonRegressor class.
"""

import pytest
import numpy as np
import warnings
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error

from amgd.regressors.poisson_regression import AMGDPoissonRegressor
from amgd.utils.metrics import mean_poisson_deviance, compute_metrics_summary


class TestAMGDPoissonRegressor:
    """Test suite for AMGDPoissonRegressor."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample Poisson regression data."""
        np.random.seed(42)
        X, y_cont = make_regression(
            n_samples=200, n_features=15, n_informative=8,
            noise=0.1, random_state=42
        )
        # Convert to Poisson counts
        y_cont = y_cont / np.std(y_cont) * 0.3
        rates = np.exp(y_cont - np.max(y_cont) + 1)
        y = np.random.poisson(rates)
        return train_test_split(X, y, test_size=0.3, random_state=42)
    
    @pytest.fixture
    def small_data(self):
        """Generate small dataset for quick tests."""
        np.random.seed(42)
        X = np.random.randn(50, 5)
        linear_pred = X @ np.random.randn(5) * 0.2
        y = np.random.poisson(np.exp(linear_pred))
        return X, y
    
    def test_initialization(self):
        """Test regressor initialization with default parameters."""
        regressor = AMGDPoissonRegressor()
        
        # Check default parameters
        assert regressor.alpha == 1.0
        assert regressor.l1_ratio == 0.5
        assert regressor.fit_intercept == True
        assert regressor.normalize == False
        assert regressor.max_iter == 1000
        assert regressor.learning_rate == 0.01
    
    def test_parameter_validation(self):
        """Test parameter validation during initialization."""
        # Test negative alpha
        with pytest.raises(ValueError, match="alpha must be non-negative"):
            regressor = AMGDPoissonRegressor(alpha=-1.0)
            regressor._validate_params()
        
        # Test invalid l1_ratio
        with pytest.raises(ValueError, match="l1_ratio must be between 0 and 1"):
            regressor = AMGDPoissonRegressor(l1_ratio=1.5)
            regressor._validate_params()
        
        # Test invalid max_iter
        with pytest.raises(ValueError, match="max_iter must be positive"):
            regressor = AMGDPoissonRegressor(max_iter=-10)
            regressor._validate_params()
        
        # Test invalid learning_rate
        with pytest.raises(ValueError, match="learning_rate must be positive"):
            regressor = AMGDPoissonRegressor(learning_rate=0)
            regressor._validate_params()
    
    def test_penalty_type_determination(self):
        """Test penalty type determination from l1_ratio."""
        # Pure L2 (Ridge)
        regressor = AMGDPoissonRegressor(l1_ratio=0.0)
        assert regressor._determine_penalty_type() == 'l2'
        
        # Pure L1 (Lasso)
        regressor = AMGDPoissonRegressor(l1_ratio=1.0)
        assert regressor._determine_penalty_type() == 'l1'
        
        # Elastic Net
        regressor = AMGDPoissonRegressor(l1_ratio=0.5)
        assert regressor._determine_penalty_type() == 'elasticnet'
    
    def test_basic_fit_predict(self, sample_data):
        """Test basic fitting and prediction functionality."""
        X_train, X_test, y_train, y_test = sample_data
        
        regressor = AMGDPoissonRegressor(
            alpha=0.01, 
            l1_ratio=0.7, 
            max_iter=100,
            verbose=False
        )
        
        # Fit the model
        regressor.fit(X_train, y_train)
        
        # Check fitted attributes
        assert hasattr(regressor, 'coef_')
        assert hasattr(regressor, 'intercept_')
        assert hasattr(regressor, 'n_iter_')
        assert len(regressor.coef_) == X_train.shape[1]
        
        # Test predictions
        y_pred = regressor.predict(X_test)
        assert len(y_pred) == len(y_test)
        assert np.all(y_pred >= 0)  # Poisson predictions should be non-negative
        assert np.all(np.isfinite(y_pred))
    
    def test_fit_with_intercept(self, small_data):
        """Test fitting with intercept."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(
            fit_intercept=True,
            alpha=0.1,
            max_iter=50,
            verbose=False
        )
        
        regressor.fit(X, y)
        
        # Should have intercept
        assert hasattr(regressor, 'intercept_')
        assert np.isfinite(regressor.intercept_)
    
    def test_fit_without_intercept(self, small_data):
        """Test fitting without intercept."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(
            fit_intercept=False,
            alpha=0.1,
            max_iter=50,
            verbose=False
        )
        
        regressor.fit(X, y)
        
        # Intercept should be zero
        assert regressor.intercept_ == 0.0
    
    def test_fit_with_normalization(self, small_data):
        """Test fitting with feature normalization."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(
            normalize=True,
            alpha=0.1,
            max_iter=50,
            verbose=False
        )
        
        regressor.fit(X, y)
        
        # Should have scaler
        assert hasattr(regressor, 'scaler_')
        assert regressor.scaler_ is not None
        
        # Should be able to predict
        y_pred = regressor.predict(X)
        assert len(y_pred) == len(y)
    
    def test_different_regularization_types(self, small_data):
        """Test different regularization types."""
        X, y = small_data
        
        # Test L1 (Lasso)
        regressor_l1 = AMGDPoissonRegressor(
            alpha=0.1, 
            l1_ratio=1.0,
            max_iter=50,
            verbose=False
        )
        regressor_l1.fit(X, y)
        
        # Test L2 (Ridge)
        regressor_l2 = AMGDPoissonRegressor(
            alpha=0.1, 
            l1_ratio=0.0,
            max_iter=50,
            verbose=False
        )
        regressor_l2.fit(X, y)
        
        # Test Elastic Net
        regressor_en = AMGDPoissonRegressor(
            alpha=0.1, 
            l1_ratio=0.5,
            max_iter=50,
            verbose=False
        )
        regressor_en.fit(X, y)
        
        # All should fit successfully
        for reg in [regressor_l1, regressor_l2, regressor_en]:
            assert hasattr(reg, 'coef_')
            y_pred = reg.predict(X)
            assert len(y_pred) == len(y)
    
    def test_sparsity_functionality(self, sample_data):
        """Test sparsity calculation and feature selection."""
        X_train, X_test, y_train, y_test = sample_data
        
        # High L1 regularization should induce sparsity
        regressor = AMGDPoissonRegressor(
            alpha=0.5,  # High regularization
            l1_ratio=1.0,  # Pure L1
            max_iter=100,
            verbose=False
        )
        
        regressor.fit(X_train, y_train)
        
        # Check sparsity
        sparsity = regressor.get_sparsity()
        assert 0 <= sparsity <= 1
        assert sparsity > 0  # Should achieve some sparsity
        
        # Check feature importance
        importance = regressor.get_feature_importance()
        assert len(importance) == X_train.shape[1]
        assert np.all(importance >= 0)
    
    def test_predict_log_rate(self, small_data):
        """Test prediction of log rates (linear predictor)."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(alpha=0.1, max_iter=50, verbose=False)
        regressor.fit(X, y)
        
        log_rates = regressor.predict_log_rate(X)
        
        # Check properties
        assert len(log_rates) == len(y)
        assert np.all(np.isfinite(log_rates))
        
        # Should match with exp of predict
        predictions = regressor.predict(X)
        np.testing.assert_array_almost_equal(
            predictions, 
            np.exp(log_rates), 
            decimal=10
        )
    
    def test_scoring_metrics(self, sample_data):
        """Test different scoring metrics."""
        X_train, X_test, y_train, y_test = sample_data
        
        regressor = AMGDPoissonRegressor(
            alpha=0.01, 
            max_iter=100,
            verbose=False
        )
        regressor.fit(X_train, y_train)
        
        # Test different metrics
        deviance_score = regressor.score(X_test, y_test, metric='deviance')
        mae_score = regressor.score(X_test, y_test, metric='mae')
        mse_score = regressor.score(X_test, y_test, metric='mse')
        
        # All scores should be finite and positive
        assert np.isfinite(deviance_score) and deviance_score >= 0
        assert np.isfinite(mae_score) and mae_score >= 0
        assert np.isfinite(mse_score) and mse_score >= 0
        
        # Test invalid metric
        with pytest.raises(ValueError, match="Unknown metric"):
            regressor.score(X_test, y_test, metric='invalid')
    
    def test_convergence_info(self, small_data):
        """Test convergence information retrieval."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(
            alpha=0.1, 
            max_iter=50, 
            tol=1e-6,
            verbose=False
        )
        regressor.fit(X, y)
        
        info = regressor.get_convergence_info()
        
        # Check convergence info structure
        assert isinstance(info, dict)
        assert 'converged' in info
        assert 'final_loss' in info
        assert 'n_iterations' in info
        assert isinstance(info['converged'], bool)
        assert info['final_loss'] > 0
        assert info['n_iterations'] <= 50
    
    def test_negative_targets_validation(self):
        """Test validation for negative target values."""
        X = np.random.randn(50, 5)
        y_negative = np.array([-1, 0, 1, 2, 3] * 10)
        
        regressor = AMGDPoissonRegressor(alpha=0.1, max_iter=10, verbose=False)
        
        # Should raise ValueError for negative targets
        with pytest.raises(ValueError, match="Poisson regression requires non-negative"):
            regressor.fit(X, y_negative)
    
    def test_sklearn_compatibility(self, sample_data):
        """Test compatibility with scikit-learn interfaces."""
        X_train, X_test, y_train, y_test = sample_data
        
        regressor = AMGDPoissonRegressor(alpha=0.01, max_iter=50, verbose=False)
        
        # Test get_params and set_params
        params = regressor.get_params()
        assert 'alpha' in params
        assert 'l1_ratio' in params
        
        # Test set_params
        regressor.set_params(alpha=0.05, l1_ratio=0.8)
        assert regressor.alpha == 0.05
        assert regressor.l1_ratio == 0.8
        
        # Test fit and predict
        regressor.fit(X_train, y_train)
        y_pred = regressor.predict(X_test)
        
        # Should work with sklearn metrics
        mae = mean_absolute_error(y_test, y_pred)
        assert np.isfinite(mae) and mae >= 0
    
    def test_grid_search_compatibility(self, small_data):
        """Test compatibility with GridSearchCV."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(max_iter=30, verbose=False)
        
        param_grid = {
            'alpha': [0.01, 0.1],
            'l1_ratio': [0.5, 1.0]
        }
        
        # Should work with GridSearchCV
        grid_search = GridSearchCV(
            regressor, 
            param_grid, 
            cv=3, 
            scoring='neg_mean_absolute_error'
        )
        
        grid_search.fit(X, y)
        
        # Check that it found best parameters
        assert hasattr(grid_search, 'best_params_')
        assert 'alpha' in grid_search.best_params_
        assert 'l1_ratio' in grid_search.best_params_
    
    def test_plot_convergence(self, small_data):
        """Test convergence plotting functionality."""
        X, y = small_data
        
        regressor = AMGDPoissonRegressor(alpha=0.1, max_iter=30, verbose=False)
        regressor.fit(X, y)
        
        try:
            import matplotlib.pyplot as plt
            
            # Should create plot without error
            ax = regressor.plot_convergence()
            assert ax is not None
            
            # Close the plot to avoid display issues in tests
            plt.close()
            
        except ImportError:
            # If matplotlib not available, should raise ImportError
            with pytest.raises(ImportError, match="matplotlib is required"):
                regressor.plot_convergence()
    
    def test_repr_string(self):
        """Test string representation of the regressor."""
        regressor = AMGDPoissonRegressor(alpha=0.05, l1_ratio=0.8)
        repr_str = repr(regressor)
        
        assert 'AMGDPoissonRegressor' in repr_str
        assert 'alpha=0.05' in repr_str
        assert 'l1_ratio=0.8' in repr_str
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with empty data
        X_empty = np.array([]).reshape(0, 5)
        y_empty = np.array([])
        
        regressor = AMGDPoissonRegressor(verbose=False)
        
        with pytest.raises((ValueError, IndexError)):
            regressor.fit(X_empty, y_empty)
        
        # Test prediction before fitting
        X = np.random.randn(10, 5)
        regressor_unfitted = AMGDPoissonRegressor()
        
        with pytest.raises(ValueError):
            regressor_unfitted.predict(X)
        
        with pytest.raises(ValueError):
            regressor_unfitted.get_sparsity()
    
    def test_single_sample(self):
        """Test behavior with single sample."""
        X = np.array([[1, 2, 3, 4, 5]])
        y = np.array([3])
        
        regressor = AMGDPoissonRegressor(alpha=0.1, max_iter=10, verbose=False)
        regressor.fit(X, y)
        
        # Should handle single sample
        assert hasattr(regressor, 'coef_')
        pred = regressor.predict(X)
        assert len(pred) == 1
        assert pred[0] >= 0


class TestAMGDPoissonRegressorIntegration:
    """Integration tests for AMGDPoissonRegressor."""
    
    def test_feature_selection_consistency(self):
        """Test that feature selection is consistent across runs."""
        np.random.seed(42)
        
        # Create data with known sparse structure
        n_samples, n_features = 150, 20
        n_informative = 6
        
        X = np.random.randn(n_samples, n_features)
        true_coef = np.zeros(n_features)
        true_coef[:n_informative] = np.random.randn(n_informative) * 0.5
        
        linear_pred = X @ true_coef
        y = np.random.poisson(np.exp(linear_pred))
        
        # Fit multiple models with same parameters
        models = []
        for i in range(3):
            regressor = AMGDPoissonRegressor(
                alpha=0.1,
                l1_ratio=1.0,  # Pure L1
                random_state=42,
                max_iter=200,
                verbose=False
            )
            regressor.fit(X, y)
            models.append(regressor)
        
        # Check that feature selection is consistent
        sparsities = [model.get_sparsity() for model in models]
        assert len(set(sparsities)) == 1  # All should have same sparsity
        
        # Check coefficient consistency
        for i in range(1, len(models)):
            np.testing.assert_array_almost_equal(
                models[0].coef_, 
                models[i].coef_, 
                decimal=6
            )
    
    def test_regularization_path(self):
        """Test behavior across regularization path."""
        np.random.seed(42)
        
        # Generate test data
        X = np.random.randn(100, 10)
        true_coef = np.random.randn(10) * 0.2
        linear_pred = X @ true_coef
        y = np.random.poisson(np.exp(linear_pred))
        
        # Test different regularization strengths
        alphas = [0.001, 0.01, 0.1, 1.0]
        results = []
        
        for alpha in alphas:
            regressor = AMGDPoissonRegressor(
                alpha=alpha,
                l1_ratio=1.0,  # Pure L1
                max_iter=100,
                verbose=False,
                random_state=42
            )
            
            regressor.fit(X, y)
            y_pred = regressor.predict(X)
            
            results.append({
                'alpha': alpha,
                'sparsity': regressor.get_sparsity(),
                'mae': mean_absolute_error(y, y_pred),
                'n_features': np.sum(np.abs(regressor.coef_) > 1e-8),
                'converged': regressor.get_convergence_info()['converged']
            })
        
        # All should converge
        assert all(r['converged'] for r in results)
        
        # Sparsity should generally increase with regularization
        sparsities = [r['sparsity'] for r in results]
        assert sparsities[-1] >= sparsities[0]
        
        # Number of features should decrease with regularization
        n_features = [r['n_features'] for r in results]
        assert n_features[-1] <= n_features[0]
    
    def test_comparison_with_baseline(self):
        """Test performance comparison with baseline methods."""
        np.random.seed(42)
        
        # Generate challenging sparse data
        n_samples, n_features = 200, 25
        n_informative = 8
        
        X = np.random.randn(n_samples, n_features)
        true_coef = np.zeros(n_features)
        true_coef[:n_informative] = np.random.randn(n_informative) * 0.3
        
        linear_pred = X @ true_coef
        y = np.random.poisson(np.exp(linear_pred))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # Fit AMGD model
        amgd_model = AMGDPoissonRegressor(
            alpha=0.05,
            l1_ratio=0.8,
            max_iter=300,
            verbose=False,
            random_state=42
        )
        
        amgd_model.fit(X_train, y_train)
        y_pred_amgd = amgd_model.predict(X_test)
        
        # Calculate metrics
        mae_amgd = mean_absolute_error(y_test, y_pred_amgd)
        sparsity_amgd = amgd_model.get_sparsity()
        
        # Basic performance checks
        assert mae_amgd < np.mean(y_test)  # Better than predicting mean
        assert sparsity_amgd > 0.1  # Should achieve meaningful sparsity
        assert np.all(y_pred_amgd >= 0)  # Predictions should be non-negative
        
        # Convergence check
        assert amgd_model.get_convergence_info()['converged']
    
    def test_real_world_workflow(self):
        """Test a complete real-world workflow."""
        np.random.seed(42)
        
        # Simulate ecological count data
        n_samples, n_features = 300, 12
        
        # Create realistic feature matrix (environmental variables)
        X = np.random.randn(n_samples, n_features)
        
        # Create realistic coefficient structure
        # - Few important features (pollution, temperature, etc.)
        # - Many irrelevant features
        true_coef = np.zeros(n_features)
        true_coef[0] = 0.8   # Primary environmental factor
        true_coef[1] = -0.6  # Negative impact factor
        true_coef[2] = 0.4   # Secondary factor
        # Features 3-11 are noise/irrelevant
        
        linear_pred = X @ true_coef + np.random.normal(0, 0.1, n_samples)
        y = np.random.poisson(np.exp(linear_pred))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )
        
        # Model selection workflow
        alphas = [0.01, 0.05, 0.1, 0.2]
        l1_ratios = [0.7, 0.8, 0.9, 1.0]
        
        best_score = float('inf')
        best_model = None
        
        for alpha in alphas:
            for l1_ratio in l1_ratios:
                model = AMGDPoissonRegressor(
                    alpha=alpha,
                    l1_ratio=l1_ratio,
                    max_iter=200,
                    verbose=False,
                    random_state=42
                )
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                score = mean_absolute_error(y_test, y_pred)
                
                if score < best_score:
                    best_score = score
                    best_model = model
        
        # Analyze best model
        assert best_model is not None
        assert best_model.get_sparsity() > 0.5  # Should identify sparse structure
        assert best_score < np.mean(y_test)  # Should beat naive baseline
        
        # Feature importance should identify true important features
        importance = best_model.get_feature_importance()
        top_features = np.argsort(importance)[-3:]  # Top 3 features
        assert 0 in top_features  # Should identify feature 0 as important
        assert 1 in top_features  # Should identify feature 1 as important
        
        # Generate comprehensive metrics
        y_pred_final = best_model.predict(X_test)
        metrics = compute_metrics_summary(y_test, y_pred_final)
        
        # All metrics should be reasonable
        assert metrics['mae'] > 0
        assert metrics['rmse'] > 0
        assert metrics['r2'] <= 1.0
        assert metrics['mean_poisson_deviance'] > 0
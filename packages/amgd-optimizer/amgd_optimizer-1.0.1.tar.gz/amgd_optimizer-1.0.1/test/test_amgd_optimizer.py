"""
Tests for AMGDOptimizer class.
"""

import pytest
import numpy as np
from sklearn.datasets import make_regression

from amgd.core.amgd_optimizer import AMGDOptimizer


class TestAMGDOptimizer:
    """Test suite for AMGDOptimizer."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample Poisson regression data."""
        np.random.seed(42)
        X, y_continuous = make_regression(
            n_samples=100, n_features=10, n_informative=5, 
            noise=0.1, random_state=42
        )
        # Convert to Poisson counts
        y_continuous = y_continuous / np.std(y_continuous) * 0.3
        rates = np.exp(y_continuous - np.max(y_continuous) + 1)
        y = np.random.poisson(rates)
        return X, y
    
    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = AMGDOptimizer()
        
        # Check default parameters
        assert optimizer.learning_rate == 0.01
        assert optimizer.momentum_beta1 == 0.9
        assert optimizer.momentum_beta2 == 0.999
        assert optimizer.penalty == 'l1'
        assert optimizer.max_iter == 1000
    
    def test_invalid_parameters(self):
        """Test parameter validation."""
        with pytest.raises(ValueError):
            AMGDOptimizer(learning_rate=-0.01)
        
        with pytest.raises(ValueError):
            AMGDOptimizer(momentum_beta1=1.5)
        
        with pytest.raises(ValueError):
            AMGDOptimizer(lambda1=-0.1)
        
        with pytest.raises(ValueError):
            AMGDOptimizer(penalty='invalid')
    
    def test_fit_basic(self, sample_data):
        """Test basic fitting functionality."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(
            penalty='l1', 
            lambda1=0.01, 
            max_iter=100,
            verbose=False
        )
        
        # Should not raise an exception
        optimizer.fit(X, y)
        
        # Check that coefficients are fitted
        assert hasattr(optimizer, 'coef_')
        assert len(optimizer.coef_) == X.shape[1]
        assert hasattr(optimizer, 'n_iter_')
        assert optimizer.n_iter_ <= 100
    
    def test_fit_l2_penalty(self, sample_data):
        """Test fitting with L2 penalty."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(
            penalty='l2',
            lambda2=0.01,
            max_iter=100,
            verbose=False
        )
        
        optimizer.fit(X, y)
        assert hasattr(optimizer, 'coef_')
    
    def test_fit_elasticnet_penalty(self, sample_data):
        """Test fitting with Elastic Net penalty."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(
            penalty='elasticnet',
            lambda1=0.01,
            lambda2=0.01,
            max_iter=100,
            verbose=False
        )
        
        optimizer.fit(X, y)
        assert hasattr(optimizer, 'coef_')
    
    def test_predict(self, sample_data):
        """Test prediction functionality."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(max_iter=50, verbose=False)
        optimizer.fit(X, y)
        
        predictions = optimizer.predict(X)
        
        # Check predictions shape and properties
        assert len(predictions) == len(y)
        assert np.all(predictions >= 0)  # Poisson predictions should be non-negative
        assert np.all(np.isfinite(predictions))
    
    def test_predict_before_fit(self, sample_data):
        """Test that predict raises error before fitting."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer()
        
        with pytest.raises(ValueError):
            optimizer.predict(X)
    
    def test_sparsity_l1(self, sample_data):
        """Test that L1 penalty induces sparsity."""
        X, y = sample_data
        
        # High regularization should induce sparsity
        optimizer = AMGDOptimizer(
            penalty='l1',
            lambda1=0.5,  # High regularization
            max_iter=200,
            verbose=False
        )
        
        optimizer.fit(X, y)
        sparsity = optimizer.get_sparsity()
        
        # Should have some zero coefficients
        assert sparsity > 0
        assert 0 <= sparsity <= 1
    
    def test_no_sparsity_l2(self, sample_data):
        """Test that L2 penalty doesn't induce sparsity."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(
            penalty='l2',
            lambda2=0.1,
            max_iter=100,
            verbose=False
        )
        
        optimizer.fit(X, y)
        sparsity = optimizer.get_sparsity()
        
        # L2 should not induce exact sparsity
        assert sparsity < 0.1  # Very few coefficients should be exactly zero
    
    def test_convergence_info(self, sample_data):
        """Test convergence information."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(max_iter=50, tol=1e-6, verbose=False)
        optimizer.fit(X, y)
        
        info = optimizer.convergence_info_
        assert 'converged' in info
        assert 'final_loss' in info
        assert 'n_iterations' in info
        assert isinstance(info['converged'], bool)
        assert info['final_loss'] > 0
    
    def test_loss_history(self, sample_data):
        """Test loss history tracking."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(max_iter=50, verbose=False)
        optimizer.fit(X, y)
        
        # Check loss history
        assert hasattr(optimizer, 'loss_history_')
        assert len(optimizer.loss_history_) > 0
        assert len(optimizer.loss_history_) <= 50
        
        # Loss should generally decrease
        if len(optimizer.loss_history_) > 10:
            early_loss = np.mean(optimizer.loss_history_[:5])
            late_loss = np.mean(optimizer.loss_history_[-5:])
            assert late_loss <= early_loss  # Should improve over time
    
    def test_feature_importance(self, sample_data):
        """Test feature importance calculation."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(max_iter=50, verbose=False)
        optimizer.fit(X, y)
        
        importance = optimizer.get_feature_importance()
        
        assert len(importance) == X.shape[1]
        assert np.all(importance >= 0)  # Should be absolute values
        assert np.all(np.isfinite(importance))
    
    def test_gradient_clipping(self, sample_data):
        """Test gradient clipping functionality."""
        X, y = sample_data
        
        # Add some extreme values to test clipping
        X_extreme = X.copy()
        X_extreme[0, :] = 100  # Extreme values
        
        optimizer = AMGDOptimizer(
            gradient_clip=1.0,  # Low clipping threshold
            max_iter=50,
            verbose=False
        )
        
        # Should not raise overflow errors
        optimizer.fit(X_extreme, y)
        assert hasattr(optimizer, 'coef_')
    
    def test_adaptive_learning_rate(self, sample_data):
        """Test adaptive learning rate decay."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(
            learning_rate=0.1,
            decay_rate=0.01,  # Strong decay
            max_iter=100,
            verbose=False
        )
        
        optimizer.fit(X, y)
        
        # Should converge despite high initial learning rate
        assert hasattr(optimizer, 'coef_')
        assert optimizer.n_iter_ <= 100
    
    def test_reproducibility(self, sample_data):
        """Test that results are reproducible with same random state."""
        X, y = sample_data
        
        optimizer1 = AMGDOptimizer(random_state=42, max_iter=50, verbose=False)
        optimizer2 = AMGDOptimizer(random_state=42, max_iter=50, verbose=False)
        
        optimizer1.fit(X, y)
        optimizer2.fit(X, y)
        
        # Should get identical results
        np.testing.assert_array_almost_equal(optimizer1.coef_, optimizer2.coef_, decimal=6)
    
    def test_different_penalties_convergence(self, sample_data):
        """Test that all penalty types can converge."""
        X, y = sample_data
        
        penalties = ['l1', 'l2', 'elasticnet']
        
        for penalty in penalties:
            optimizer = AMGDOptimizer(
                penalty=penalty,
                lambda1=0.01,
                lambda2=0.01,
                max_iter=100,
                verbose=False
            )
            
            optimizer.fit(X, y)
            
            # All should converge successfully
            assert hasattr(optimizer, 'coef_')
            assert len(optimizer.coef_) == X.shape[1]
            
            # Should be able to make predictions
            pred = optimizer.predict(X)
            assert len(pred) == len(y)
    
    def test_score(self, sample_data):
        """Test scoring functionality."""
        X, y = sample_data
        
        optimizer = AMGDOptimizer(max_iter=50, verbose=False)
        optimizer.fit(X, y)
        
        score = optimizer.score(X, y)
        
        # R² score should be between -∞ and 1
        assert score <= 1.0
        assert np.isfinite(score)
    
    def test_empty_data(self):
        """Test behavior with empty data."""
        X = np.array([]).reshape(0, 5)
        y = np.array([])
        
        optimizer = AMGDOptimizer(verbose=False)
        
        with pytest.raises((ValueError, IndexError)):
            optimizer.fit(X, y)
    
    def test_single_sample(self):
        """Test behavior with single sample."""
        X = np.array([[1, 2, 3, 4, 5]])
        y = np.array([5])
        
        optimizer = AMGDOptimizer(max_iter=10, verbose=False)
        optimizer.fit(X, y)
        
        # Should handle single sample
        assert hasattr(optimizer, 'coef_')
        pred = optimizer.predict(X)
        assert len(pred) == 1
    
    def test_negative_targets_warning(self):
        """Test warning for negative target values."""
        X = np.random.randn(50, 5)
        y = np.array([-1, 0, 1, 2, 3] * 10)  # Include negative values
        
        optimizer = AMGDOptimizer(max_iter=10, verbose=False)
        
        with pytest.warns(UserWarning):
            optimizer.fit(X, y)


class TestAMGDOptimizerIntegration:
    """Integration tests for AMGDOptimizer."""
    
    def test_comparison_with_known_solution(self):
        """Test on a problem with known sparse solution."""
        np.random.seed(42)
        
        # Create data with known sparse structure
        n_samples, n_features = 200, 20
        n_informative = 5
        
        X = np.random.randn(n_samples, n_features)
        true_coef = np.zeros(n_features)
        true_coef[:n_informative] = np.random.randn(n_informative)
        
        # Generate Poisson targets
        linear_pred = X @ true_coef
        linear_pred = linear_pred - np.max(linear_pred) + 1  # Ensure positive rates
        y = np.random.poisson(np.exp(linear_pred))
        
        # Fit AMGD with L1 penalty
        optimizer = AMGDOptimizer(
            penalty='l1',
            lambda1=0.01,
            max_iter=500,
            verbose=False,
            random_state=42
        )
        
        optimizer.fit(X, y)
        
        # Check that it identifies some sparse structure
        estimated_coef = optimizer.coef_
        sparsity = optimizer.get_sparsity()
        
        # Should achieve some sparsity
        assert sparsity > 0.1
        
        # Should be able to predict reasonably well
        y_pred = optimizer.predict(X)
        mae = np.mean(np.abs(y - y_pred))
        
        # MAE should be reasonable (less than mean of y)
        assert mae < np.mean(y)
    
    def test_performance_different_regularizations(self):
        """Test performance across different regularization strengths."""
        np.random.seed(42)
        
        # Generate test data
        X = np.random.randn(150, 15)
        true_coef = np.random.randn(15) * 0.1
        linear_pred = X @ true_coef
        y = np.random.poisson(np.exp(linear_pred))
        
        lambdas = [0.001, 0.01, 0.1]
        results = []
        
        for lam in lambdas:
            optimizer = AMGDOptimizer(
                penalty='l1',
                lambda1=lam,
                max_iter=200,
                verbose=False,
                random_state=42
            )
            
            optimizer.fit(X, y)
            y_pred = optimizer.predict(X)
            mae = np.mean(np.abs(y - y_pred))
            sparsity = optimizer.get_sparsity()
            
            results.append({
                'lambda': lam,
                'mae': mae,
                'sparsity': sparsity,
                'converged': optimizer.convergence_info_['converged']
            })
        
        # All should converge
        assert all(r['converged'] for r in results)
        
        # Sparsity should generally increase with regularization
        sparsities = [r['sparsity'] for r in results]
        assert sparsities[-1] >= sparsities[0]  # Highest lambda should give highest sparsity
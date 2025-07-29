"""Tests for the optimizers module."""

import numpy as np
import pytest
from qsppack import lbfgs, coordinate_minimization, newton

def test_lbfgs_basic():
    """Test basic functionality of L-BFGS optimizer."""
    # Simple objective function: f(x) = x^2
    def obj(x, delta, opts):
        return np.array([x[0]**2])
    
    # Gradient of objective function: f'(x) = 2x
    def grad(x, delta, opts):
        return np.array([[2*x[0]]]), np.array([x[0]**2])
    
    # Test parameters
    delta = np.array([1.0])
    x0 = np.array([2.0])
    opts = {
        'maxiter': 100,
        'criteria': 1e-6,
        'print': False
    }
    
    x, obj_value, iter = lbfgs(obj, grad, delta, x0, opts)
    
    assert isinstance(x, np.ndarray)
    assert isinstance(obj_value, float)
    assert isinstance(iter, int)
    assert abs(x[0]) < 1e-3  # Should be close to 0
    assert obj_value < 1e-6  # Objective should be small

def test_coordinate_minimization_basic():
    """Test basic functionality of coordinate minimization."""
    coef = np.array([1.0])
    parity = 1
    opts = {
        'maxiter': 100,
        'criteria': 1e-6,
        'print': False
    }
    
    phi, err, iter, runtime = coordinate_minimization(coef, parity, opts)
    
    assert isinstance(phi, np.ndarray)
    assert isinstance(err, float)
    assert isinstance(iter, int)
    assert isinstance(runtime, float)
    assert err < 1e-6  # Error should be small

def test_newton_basic():
    """Test basic functionality of Newton's method."""
    coef = np.array([1.0])
    parity = 1
    opts = {
        'maxiter': 100,
        'criteria': 1e-6,
        'print': False
    }
    
    phi, err, iter, runtime = newton(coef, parity, opts)
    
    assert isinstance(phi, np.ndarray)
    assert isinstance(err, float)
    assert isinstance(iter, int)
    assert isinstance(runtime, float)
    assert err < 1e-6  # Error should be small 
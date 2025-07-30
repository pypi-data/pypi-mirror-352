"""Tests for the solver module."""

import numpy as np
import pytest
from qsppack import solve

def test_solve_basic():
    """Test basic functionality of solve function."""
    # Test case: simple polynomial P(x) = x
    coef = np.array([1.0])
    parity = 1  # odd polynomial
    opts = {
        'criteria': 1e-12,
        'useReal': True,
        'targetPre': True,
        'method': 'FPI',
        'typePhi': 'full'
    }
    
    phi, out = solve(coef, parity, opts)
    
    # Basic assertions
    assert phi is not None
    assert out is not None
    assert isinstance(phi, np.ndarray)
    assert isinstance(out, dict)
    assert 'iter' in out
    assert 'time' in out
    assert 'value' in out
    assert out['parity'] == parity
    assert out['targetPre'] == opts['targetPre']
    assert out['typePhi'] == opts['typePhi']

def test_solve_invalid_method():
    """Test solve function with invalid method."""
    coef = np.array([1.0])
    parity = 1
    opts = {
        'method': 'INVALID_METHOD'
    }
    
    phi, out = solve(coef, parity, opts)
    assert phi is None
    assert out is None

def test_solve_different_parity():
    """Test solve function with even parity polynomial."""
    # Test case: simple polynomial P(x) = x^2
    coef = np.array([1.0])
    parity = 0  # even polynomial
    opts = {
        'criteria': 1e-12,
        'useReal': True,
        'targetPre': True,
        'method': 'FPI',
        'typePhi': 'full'
    }
    
    phi, out = solve(coef, parity, opts)
    
    assert phi is not None
    assert out is not None
    assert out['parity'] == parity 
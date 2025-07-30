"""Tests for the solver module."""

import numpy as np
import pytest
from qsppack.solver import solve
from qsppack.utils import cvx_poly_coef

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

def test_solve_gibbs():
    """Test solve function for Gibbs state preparation."""
    # set parameters for polynomial approximation
    beta = 2
    targ = lambda x: np.exp(-beta * x)
    deg = 151
    parity = deg % 2
    delta = 0.2

    # options for cvx_poly_coef
    opts = {
        'intervals': [delta, 1],
        'objnorm': 2,
        'epsil': 0.2,
        'npts': 500,
        'fscale': 1,
        'isplot': False,
        'method': 'cvxpy',
        'maxiter': 100
    }

    coef_full = cvx_poly_coef(targ, deg, opts)
    coef = coef_full[parity::2]
    
    opts['criteria'] = 1e-12
    opts['useReal'] = False
    opts['targetPre'] = True
    opts['method'] = 'Newton'
    angles, out = solve(coef, parity, opts)
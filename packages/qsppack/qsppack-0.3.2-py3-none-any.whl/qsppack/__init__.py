"""Quantum Signal Processing Package.

This package provides tools for optimizing phase factors in Quantum Signal
Processing problems.
"""

from .solver import solve
from .utils import (
    get_unitary, get_unitary_sym, get_entry, reduced_to_full,
    chebyshev_to_func, cvx_poly_coef
)
from .objective import obj_sym, grad_sym, grad_sym_real
from .optimizers import lbfgs, coordinate_minimization, newton

__all__ = [
    # solver
    'solve',
    # utils
    'get_unitary',
    'get_unitary_sym',
    'get_entry',
    'reduced_to_full',
    'chebyshev_to_func',
    'cvx_poly_coef',
    # objective
    'obj_sym',
    'grad_sym',
    'grad_sym_real',
    # optimizers
    'lbfgs',
    'coordinate_minimization',
    'newton',
] 
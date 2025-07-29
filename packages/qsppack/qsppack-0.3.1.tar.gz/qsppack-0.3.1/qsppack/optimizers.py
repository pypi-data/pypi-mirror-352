"""Optimization methods for Quantum Signal Processing.

This module provides various optimization algorithms for finding phase factors
in Quantum Signal Processing problems.
"""

import numpy as np
import time
from .objective import (
    obj_sym, grad_sym, grad_sym_real,
    get_pim_sym, get_pim_sym_real,
    get_pim_deri_sym, get_pim_deri_sym_real
)
from .utils import F, F_Jacobian
from .nlfa import b_from_cheb, weiss, inverse_nonlinear_FFT

def lbfgs(obj, grad, delta, phi, opts):
    """L-BFGS optimization for QSP phase factors.

    This function implements the Limited-memory BFGS optimization algorithm
    for finding optimal phase factors in QSP problems.

    Parameters
    ----------
    obj : callable
        Objective function to minimize
    grad : callable
        Gradient function of the objective
    x0 : array_like
        Initial points for evaluation
    phi0 : array_like
        Initial phase factors
    opts : dict
        Options dictionary containing:
        
        - maxiter : int
            Maximum number of iterations
        - criteria : float
            Convergence criteria
        - gamma : float
            Line search retraction rate (default 0.5)
        - accrate : float
            Line search accept ratio (default 1e-3)
        - minstep : float
            Minimal step size (default 1e-5)
        - lmem : int
            L-BFGS memory size (default 200)
        - print : bool
            Whether to print progress (default True)
        - itprint : int
            Print frequency (default 1)
        - parity : int
            Parity of polynomial (0 for even, 1 for odd)

    Returns
    -------
    phi : ndarray
        Optimized phase factors
    obj_value : float
        Objective value at optimal point
    iter : int
        Number of iterations performed
    """
    # Options for L-BFGS solver
    opts.setdefault('maxiter', 50000)
    opts.setdefault('gamma', 0.5)
    opts.setdefault('accrate', 1e-3)
    opts.setdefault('minstep', 1e-5)
    opts.setdefault('criteria', 1e-12)
    opts.setdefault('lmem', 200)
    opts.setdefault('print', 1)
    opts.setdefault('itprint', 1)

    # Copy value to parameters
    maxiter = opts['maxiter']
    gamma = opts['gamma']
    accrate = opts['accrate']
    lmem = opts['lmem']
    minstep = opts['minstep']
    pri = opts['print']
    itprint = opts['itprint']
    crit = opts['criteria']

    # Setup print format
    str_head = "{:4s} {:13s} {:10s} {:10s}\n".format('iter', 'obj', 'stepsize', 'des_ratio')
    str_num = "{:4d}  {:+5.4e} {:+3.2e} {:+3.2e}\n"

    # Initial computation
    iter = 0
    d = len(phi)
    mem_size = 0
    mem_now = 0
    mem_grad = np.zeros((lmem, d))
    mem_obj = np.zeros((lmem, d))
    mem_dot = np.zeros(lmem)
    grad_s, obj_s = grad(phi, delta, opts)
    obj_value = np.mean(obj_s)
    GRAD = np.mean(grad_s, axis=0)

    # Start L-BFGS algorithm
    if pri:
        print('L-BFGS solver started')

    while True:
        iter += 1
        theta_d = GRAD.copy()
        alpha = np.zeros(mem_size)
        for i in range(mem_size):
            subsc = (mem_now - i - 1) % lmem
            alpha[i] = mem_dot[subsc] * np.dot(mem_obj[subsc, :], theta_d)
            theta_d -= alpha[i] * mem_grad[subsc, :]

        theta_d *= 0.5
        if opts['parity'] == 0:
            theta_d[0] *= 2

        for i in range(mem_size):
            subsc = (mem_now - (mem_size - i) - 1) % lmem
            beta = mem_dot[subsc] * np.dot(mem_grad[subsc, :], theta_d)
            theta_d += (alpha[mem_size - i - 1] - beta) * mem_obj[subsc, :]

        step = 1
        exp_des = np.dot(GRAD, theta_d)
        while True:
            theta_new = phi - step * theta_d
            obj_snew = obj(theta_new, delta, opts)
            obj_valuenew = np.mean(obj_snew)
            ad = obj_value - obj_valuenew
            if ad > exp_des * accrate * step or step < minstep:
                break
            step *= gamma

        phi = theta_new
        obj_value = obj_valuenew
        obj_max = np.max(obj_snew)
        grad_s, _ = grad(phi, delta, opts)
        GRAD_new = np.mean(grad_s, axis=0)
        mem_size = min(lmem, mem_size + 1)
        mem_now = (mem_now + 1) % lmem
        mem_grad[mem_now, :] = GRAD_new - GRAD
        mem_obj[mem_now, :] = -step * theta_d
        mem_dot[mem_now] = 1 / np.dot(mem_grad[mem_now, :], mem_obj[mem_now, :])
        GRAD = GRAD_new

        if pri and iter % itprint == 0:
            if iter == 1 or (iter - itprint) % (itprint * 10) == 0:
                print(str_head, end='')
            print(str_num.format(iter, obj_max, step, ad / (exp_des * step)), end='')

        if iter >= maxiter:
            print("Max iteration reached.")
            break
        if obj_max < crit**2:
            print("Stop criteria satisfied.")
            break

    return phi, obj_value, iter

def coordinate_minimization(coef, parity, opts):
    """Coordinate minimization optimization for QSP phase factors.

    This function implements the coordinate minimization algorithm for
    finding optimal phase factors in QSP problems.

    Parameters
    ----------
    coef : array_like
        Coefficients of polynomial P under Chebyshev basis
    parity : int
        Parity of polynomial P (0 for even, 1 for odd)
    opts : dict
        Options dictionary containing optimization parameters

    Returns
    -------
    phi : ndarray
        Optimized phase factors
    err : float
        Final error value
    iter : int
        Number of iterations performed
    runtime : float
        Total runtime in seconds
    """
    # Setup options for CM solver
    opts.setdefault('maxiter', int(1e5))
    opts.setdefault('criteria', 1e-12)
    opts.setdefault('targetPre', True)
    opts.setdefault('useReal', True)
    opts.setdefault('print', 1)
    opts.setdefault('itprint', 1)

    start_time = time.time()

    # Copy value to parameters
    maxiter = opts['maxiter']
    crit = opts['criteria']
    pri = opts['print']
    itprint = opts['itprint']

    # Setup print format
    str_head = "{:4s} {:13s}\n".format('iter', 'err')
    str_num = "{:4d}  {:+5.4e}\n"

    # Initial preparation
    if opts['targetPre']:
        coef = -coef  # inverse is necessary
    phi = coef / 2
    iter = 0

    # Solve by contraction mapping algorithm
    while True:
        Fval = F(phi, parity, opts)
        res = Fval - coef

        # debugging
        # Fval_j, DFval = F_Jacobian(phi, parity, opts)
        # print("Fval from F:", Fval)
        # print("Fval from F_Jacobian:", Fval_j)

        err = np.linalg.norm(res, 1)
        iter += 1
        if iter >= maxiter:
            print("Max iteration reached.")
            break
        if err < crit:
            print("Stop criteria satisfied.")
            break
        phi = phi - res / 2
        if pri and iter % itprint == 0:
            if iter == 1 or (iter - itprint) % (itprint * 10) == 0:
                print(str_head, end='')
            print(str_num.format(iter, err), end='')

    runtime = time.time() - start_time
    return phi, err, iter, runtime

def newton(coef, parity, opts):
    """Newton's method optimization for QSP phase factors.

    This function implements Newton's method for finding optimal phase
    factors in QSP problems.

    Parameters
    ----------
    coef : array_like
        Coefficients of polynomial P under Chebyshev basis
    parity : int
        Parity of polynomial P (0 for even, 1 for odd)
    opts : dict
        Options dictionary containing optimization parameters

    Returns
    -------
    phi : ndarray
        Optimized phase factors
    err : float
        Final error value
    iter : int
        Number of iterations performed
    runtime : float
        Total runtime in seconds
    """
    # Setup options for Newton solver
    opts.setdefault('maxiter', int(1e5))
    opts.setdefault('criteria', 1e-12)
    opts.setdefault('targetPre', True)
    opts.setdefault('useReal', True)
    opts.setdefault('print', 1)
    opts.setdefault('itprint', 1)

    start_time = time.time()

    # Copy value to parameters
    maxiter = opts['maxiter']
    crit = opts['criteria']
    pri = opts['print']
    itprint = opts['itprint']

    # Setup print format
    str_head = "{:4s} {:13s}\n".format('iter', 'err')
    str_num = "{:4d}  {:+5.4e}\n"

    # Initial preparation
    if opts['targetPre']:
        coef = -coef  # inverse is necessary
    phi = coef / 2
    iter = 0

    # Solve by Newton's method
    while True:
        Fval, DFval = F_Jacobian(phi, parity, opts)
        res = Fval - coef
        err = np.linalg.norm(res, 1)
        iter += 1
        if iter >= maxiter:
            print("Max iteration reached.")
            break
        if err < crit:
            print("Stop criteria satisfied.")
            break
        phi = phi - np.linalg.solve(DFval, res)
        if pri and iter % itprint == 0:
            if iter == 1 or (iter - itprint) % (itprint * 10) == 0:
                print(str_head, end='')
            print(str_num.format(iter, err), end='')

    runtime = time.time() - start_time
    return phi, err, iter, runtime 

def nlft(coef, parity, opts):
    """NLFT optimization for QSP phase factors.

    This function implements the NLFT algorithm for finding optimal phase
    factors in QSP problems.

    Parameters
    ----------
    coef : array_like
        Coefficients of polynomial P under Chebyshev basis
    parity : int
        Parity of polynomial P (0 for even, 1 for odd)
    opts : dict
    """
    opts.setdefault('N', 256)

    start_time = time.time()
    b_coeffs = b_from_cheb(coef, parity)
    a_coeffs = weiss(b_coeffs, opts['N'])
    gammas, _, _ = inverse_nonlinear_FFT(a_coeffs, b_coeffs)
    phis = np.arctan(gammas)
    runtime = time.time() - start_time
    return phis, -1, -1, runtime
"""Utility functions for QSP optimization.

This module provides utility functions for working with Chebyshev polynomials
and other mathematical operations needed in QSP optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, linprog
from scipy.special import chebyt
import cvxpy as cp

def chebyshev_to_func(x, coef, parity, partialcoef):
    """Convert Chebyshev coefficients to function values.

    This function evaluates a polynomial represented in the Chebyshev basis
    at given points.

    Parameters
    ----------
    x : array_like or float
        Points at which to evaluate the polynomial. Can be a single point
        or an array of points.
    coef : array_like
        Coefficients in Chebyshev basis, ordered from lowest to highest degree
    parity : int
        Parity of the polynomial (0 for even, 1 for odd)
    partialcoef : bool, optional
        Whether to return only coefficients of odd/even order

    Returns
    -------
    ndarray or float
        Function values at the given points. Returns a scalar if input is
        scalar, array otherwise.
    """
    ret = np.zeros(len(x))
    y = np.arccos(x)
    if partialcoef:
        if parity == 0:
            for k in range(len(coef)):
                ret += coef[k] * np.cos(2 * k * y)
        else:
            for k in range(len(coef)):
                ret += coef[k] * np.cos((2 * k + 1) * y)
    else:
        if parity == 0:
            for k in range(0, len(coef), 2):
                ret += coef[k] * np.cos(k * y)
        else:
            for k in range(1, len(coef), 2):
                ret += coef[k] * np.cos(k * y)
    return ret

def cvx_poly_coef(func, deg, opts):
    """Compute coefficients for a polynomial approximation using convex optimization.

    This function computes the coefficients of a polynomial that best approximates
    a target function over specified intervals in a least-squares sense. The function
    is called with a target function, the degree of the polynomial, and an options
    dictionary.

    Parameters
    ----------
    func : callable
        The target function to approximate.
    deg : int
        The degree of the polynomial.
    opts : dict
        Options dictionary with the following fields:
        
        - intervals : list
            [min, max] interval for x values.
        - npts : int
            Number of points to evaluate the function at.
        - objnorm : float
            Norm to use for optimization.
        - epsil : float
            Epsilon for numerical stability.
        - fscale : float
            Scale factor for function values.
        - isplot : bool
            Whether to plot results.

    Returns
    -------
    ndarray
        Coefficients of the best-fit polynomial in the Chebyshev basis.
    """
    # Set default options if not provided
    opts.setdefault('npts', 200)
    opts.setdefault('epsil', 0.01)
    opts.setdefault('fscale', 1 - opts['epsil'])
    opts.setdefault('intervals', [0, 1])
    opts.setdefault('isplot', False)
    opts.setdefault('objnorm', np.inf)
    opts.setdefault('method', 'SLSQP')

    # Check variables and assign local variables
    assert len(opts['intervals']) % 2 == 0
    parity = deg % 2
    epsil = opts['epsil']
    npts = opts['npts']

    # Generate Chebyshev points
    xpts = np.cos(np.pi * np.arange(2 * npts) / (2 * npts - 1))
    xpts = np.union1d(xpts, opts['intervals'])
    xpts = xpts[xpts >= 0]
    npts = len(xpts)

    n_interval = len(opts['intervals']) // 2
    ind_union = np.array([], dtype=int)
    ind_set = []

    for i in range(n_interval):
        ind = np.where((xpts >= opts['intervals'][2 * i]) & (xpts <= opts['intervals'][2 * i + 1]))[0]
        ind_set.append(ind)
        ind_union = np.union1d(ind_union, ind)

    # Evaluate the target function
    fx = np.zeros(npts)
    fx[ind_union] = opts['fscale'] * func(xpts[ind_union])

    # Prepare the Chebyshev polynomials
    n_coef = deg // 2 + 1 if parity == 0 else (deg + 1) // 2
    Ax = np.zeros((npts, n_coef))

    for k in range(1, n_coef + 1):
        Tcheb = chebyt(2 * (k - 1)) if parity == 0 else chebyt(2 * k - 1)
        Ax[:, k-1] = Tcheb(xpts)

    # Use optimization to find the Chebyshev coefficients
    coef = np.zeros(n_coef)
    if opts['method'] == 'SLSQP':
        def objective(coef):
            y = Ax @ coef
            return np.linalg.norm(y[ind_union] - fx[ind_union], opts['objnorm'])

        constraints = [{'type': 'ineq', 'fun': lambda coef: 1 - epsil - Ax @ coef},
                    {'type': 'ineq', 'fun': lambda coef: Ax @ coef + (1 - epsil)}]

        result = minimize(objective, np.zeros(n_coef), constraints=constraints)
        coef = result.x
    
    elif opts['method'] == 'cvxpy':
        c = cp.Variable(n_coef)
        y = Ax @ c
        residual = y[ind_union] - fx[ind_union]
        objective = cp.Minimize(cp.norm_inf(residual))
        constraints = [
            y <= 1 - epsil,
            y >= -(1-epsil)
        ]
        problem = cp.Problem(objective, constraints)
        problem.solve()
        coef = c.value

    elif opts['method'] == 'linprog':
        e0 = np.zeros(n_coef+1)
        e0[0] = 1
        A_prime = Ax[ind_union, :]

        # Build A_ub and b_ub
        neg_one = -np.ones((A_prime.shape[0], 1))
        zero_one = np.zeros((Ax.shape[0], 1))

        A_ub = np.vstack([
            np.hstack([neg_one, A_prime]),       # A'c - t <= f
            np.hstack([neg_one, -A_prime]),      # -A'c - t <= -f
            np.hstack([zero_one, Ax]),            # A c <= 1 - epsil
            np.hstack([zero_one, -Ax])            # -A c <= 1 - epsil
        ])

        b_ub = np.concatenate([
            fx[ind_union],
            -fx[ind_union],
            (1 - epsil) * np.ones(Ax.shape[0]),
            (1 - epsil) * np.ones(Ax.shape[0])
        ])

        # Solve
        result = linprog(c=e0, A_ub=A_ub, b_ub=b_ub, method='highs')

        if result.success:
            coef = result.x[1:n_coef+1]
        else:
            raise ValueError(f'Linear programming failed to find an optimal solution, status: {result.status}')

    else:
        raise ValueError(f'Method {opts["method"]} not supported')

    err_inf = np.linalg.norm((Ax @ coef)[ind_union] - fx[ind_union], opts['objnorm'])
    print(f'norm error = {err_inf}')

    # Make sure the maximum is less than 1
    coef_full = np.zeros(deg + 1)
    if parity == 0:
        coef_full[::2] = coef
    else:
        coef_full[1::2] = coef

    max_sol = np.max(np.abs(np.polynomial.chebyshev.chebval(xpts, coef_full)))
    print(f'max of solution = {max_sol}')
    if max_sol > 1.0 - 1e-10:
        raise ValueError('Solution is not bounded by 1. Increase npts')

    if opts['isplot']:
        plt.figure(1)
        plt.clf()
        plt.plot(xpts, Ax @ coef, 'ro', linewidth=1.5)
        for ind in ind_set:
            plt.plot(xpts[ind], fx[ind], 'b-', linewidth=2)
        plt.xlabel('$x$', fontsize=15)
        plt.ylabel('$f(x)$', fontsize=15)
        plt.legend(['polynomial', 'target'], fontsize=15)

        plt.figure(2)
        plt.clf()
        for ind in ind_set:
            plt.plot(xpts[ind], np.abs(Ax[ind] @ coef - fx[ind]), 'k-', linewidth=1.5)
        plt.xlabel('$x$', fontsize=15)
        plt.ylabel('$|f_\\mathrm{poly}(x)-f(x)|$', fontsize=15)
        plt.show()

    return coef_full

def get_unitary_sym(phi, x, parity):
    """Get the QSP unitary matrix based on given phase vector and point x.

    This function constructs the full QSP unitary matrix for a given set of
    phase factors at a specific point, handling both even and odd parity cases.

    Parameters
    ----------
    phi : array_like
        Phase factors for the QSP circuit:
        
        - For parity=1: reduced phase factors
        - For parity=0: phi[0] differs from reduced phase factors by factor of 2
    x : float
        Point at which to evaluate the unitary, must be in [-1, 1].
    parity : int
        Parity of the phase factors:
        
        - 0 : even parity
        - 1 : odd parity

    Returns
    -------
    ndarray
        The QSP unitary matrix constructed from the phase factors and point x.

    Notes
    -----
    The construction of the unitary matrix differs based on parity:
    
    - For odd parity: Uses full phase factors with a final gate transformation
    - For even parity: Uses a different construction with modified first phase
    """
    Wx = np.array([[x, 1j * np.sqrt(1 - x**2)], [1j * np.sqrt(1 - x**2), x]])
    gate = np.array([[np.exp(1j * np.pi / 4), 0], [0, np.conj(np.exp(1j * np.pi / 4))]])
    expphi = np.exp(1j * phi)

    if parity == 1:
        ret = np.array([[expphi[0], 0], [0, np.conj(expphi[0])]])
        for k in range(1, len(expphi)):
            ret = np.dot(np.dot(ret, Wx), np.array([[expphi[k], 0], [0, np.conj(expphi[k])]]))
        ret = np.dot(ret, gate)
        qspmat = np.dot(np.dot(ret.T, Wx), ret)
    else:
        ret = np.eye(2)
        for k in range(1, len(expphi)):
            ret = np.dot(ret, Wx * np.array([[expphi[k], np.conj(expphi[k])]]))
        ret = np.dot(ret, gate)
        qspmat = np.dot(np.dot(ret.T, np.array([[expphi[0], 0], [0, np.conj(expphi[0])]])), ret)

    return qspmat

def get_pim_sym(phi, x, parity):
    """Compute imaginary part of QSP unitary matrix element.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    x : float
        Point at which to evaluate
    parity : int
        Parity of phase factors (0 for even, 1 for odd)

    Returns
    -------
    float
        Imaginary part of (1,1) element of QSP unitary
    """
    qspmat = get_unitary_sym(phi, x, parity)
    return np.imag(qspmat[0, 0])

def get_pim_sym_real(phi, x, parity):
    """Compute imaginary part using real arithmetic.

    Similar to get_pim_sym but uses only real arithmetic for efficiency.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    x : float
        Point at which to evaluate
    parity : int
        Parity of phase factors (0 for even, 1 for odd)

    Returns
    -------
    float
        Imaginary part of (1,1) element of QSP unitary
    """
    n = len(phi)
    theta = np.arccos(x)
    B = np.array([[np.cos(2 * theta), 0, -np.sin(2 * theta)],
                  [0, 1, 0],
                  [np.sin(2 * theta), 0, np.cos(2 * theta)]])
    
    L = np.zeros((n, 3))
    L[n-1, :] = [0, 1, 0]
    
    for k in range(n-2, -1, -1):
        L[k, :] = np.dot(L[k+1, :], np.dot(np.array([[np.cos(2 * phi[k+1]), -np.sin(2 * phi[k+1]), 0],
                                                     [np.sin(2 * phi[k+1]), np.cos(2 * phi[k+1]), 0],
                                                     [0, 0, 1]]), B))
    
    R = np.zeros((3, n))
    if parity == 0:
        R[:, 0] = [1, 0, 0]
    else:
        R[:, 0] = [np.cos(theta), 0, np.sin(theta)]
    
    for k in range(1, n):
        R[:, k] = np.dot(B, np.dot(np.array([[np.cos(2 * phi[k-1]), -np.sin(2 * phi[k-1]), 0],
                                             [np.sin(2 * phi[k-1]), np.cos(2 * phi[k-1]), 0],
                                             [0, 0, 1]]), R[:, k-1]))
    
    return np.dot(L[n-1, :], np.dot(np.array([[np.cos(2 * phi[n-1]), -np.sin(2 * phi[n-1]), 0],
                                              [np.sin(2 * phi[n-1]), np.cos(2 * phi[n-1]), 0],
                                              [0, 0, 1]]), R[:, n-1]))

def get_pim_deri_sym(phi, x, parity):
    """Compute Pim and its derivatives.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    x : float
        Point at which to evaluate
    parity : int
        Parity of phase factors (0 for even, 1 for odd)

    Returns
    -------
    ndarray
        Array containing Pim and its derivatives
    """
    n = len(phi)
    theta = np.arccos(x)
    B = np.array([[np.cos(2 * theta), 0, -np.sin(2 * theta)],
                  [0, 1, 0],
                  [np.sin(2 * theta), 0, np.cos(2 * theta)]])
    
    L = np.zeros((n, 3))
    L[n-1, :] = [0, 1, 0]
    
    for k in range(n-2, -1, -1):
        L[k, :] = np.dot(L[k+1, :], np.dot(np.array([[np.cos(2 * phi[k+1]), -np.sin(2 * phi[k+1]), 0],
                                                     [np.sin(2 * phi[k+1]), np.cos(2 * phi[k+1]), 0],
                                                     [0, 0, 1]]), B))
    
    R = np.zeros((3, n))
    if parity == 0:
        R[:, 0] = [1, 0, 0]
    else:
        R[:, 0] = [np.cos(theta), 0, np.sin(theta)]
    
    for k in range(1, n):
        R[:, k] = np.dot(B, np.dot(np.array([[np.cos(2 * phi[k-1]), -np.sin(2 * phi[k-1]), 0],
                                             [np.sin(2 * phi[k-1]), np.cos(2 * phi[k-1]), 0],
                                             [0, 0, 1]]), R[:, k-1]))
    
    y = np.zeros(n+1)
    for k in range(n):
        y[k] = 2 * np.dot(L[k, :], np.dot(np.array([[-np.sin(2 * phi[k]), -np.cos(2 * phi[k]), 0],
                                                    [np.cos(2 * phi[k]), -np.sin(2 * phi[k]), 0],
                                                    [0, 0, 0]]), R[:, k]))
    y[n] = np.dot(L[n-1, :], np.dot(np.array([[np.cos(2 * phi[n-1]), -np.sin(2 * phi[n-1]), 0],
                                              [np.sin(2 * phi[n-1]), np.cos(2 * phi[n-1]), 0],
                                              [0, 0, 1]]), R[:, n-1]))
    
    return y

def get_pim_deri_sym_real(phi, x, parity):
    """
    Compute Pim and its Jacobian matrix values at a single point x using the real matrix representation of Pim.

    P_im: the imaginary part of the (1,1) element of the QSP unitary matrix.
    
    .. note::
        Theta MUST be a number.

    :param phi: Phase factors for QSP circuit
    :type phi: array_like
    :param x: Point at which to evaluate
    :type x: float
    :param parity: Parity of phase factors (0 for even, 1 for odd)
    :type parity: int

    :returns: Array containing Pim and its derivatives
    :rtype: ndarray
    """
    n = len(phi)
    theta = np.arccos(x)
    B = np.array([[np.cos(2 * theta), 0, -np.sin(2 * theta)],
                  [0, 1, 0],
                  [np.sin(2 * theta), 0, np.cos(2 * theta)]])
    L = np.zeros((n, 3))
    L[n-1, :] = [0, 1, 0]
    for k in range(n-2, -1, -1):
        L[k, :] = np.dot(L[k+1, :], np.dot(np.array([[np.cos(2 * phi[k+1]), -np.sin(2 * phi[k+1]), 0],
                                                     [np.sin(2 * phi[k+1]), np.cos(2 * phi[k+1]), 0],
                                                     [0, 0, 1]]), B))
    R = np.zeros((3, n))
    if parity == 0:
        R[:, 0] = [1, 0, 0]
    else:
        R[:, 0] = [np.cos(theta), 0, np.sin(theta)]
    for k in range(1, n):
        R[:, k] = np.dot(B, np.dot(np.array([[np.cos(2 * phi[k-1]), -np.sin(2 * phi[k-1]), 0],
                                             [np.sin(2 * phi[k-1]), np.cos(2 * phi[k-1]), 0],
                                             [0, 0, 1]]), R[:, k-1]))

    y = np.zeros(n+1)
    for k in range(n):
        y[k] = 2 * np.dot(L[k, :], np.dot(np.array([[-np.sin(2 * phi[k]), -np.cos(2 * phi[k]), 0],
                                                    [np.cos(2 * phi[k]), -np.sin(2 * phi[k]), 0],
                                                    [0, 0, 0]]), R[:, k]))
    y[n] = np.dot(L[n-1, :], np.dot(np.array([[np.cos(2 * phi[n-1]), -np.sin(2 * phi[n-1]), 0],
                                              [np.sin(2 * phi[n-1]), np.cos(2 * phi[n-1]), 0],
                                              [0, 0, 1]]), R[:, n-1]))

    return y
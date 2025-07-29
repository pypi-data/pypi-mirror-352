"""Objective and gradient functions for QSP optimization.

This module provides functions for computing objective values and gradients
needed in QSP optimization problems.
"""

import numpy as np
from .utils import get_unitary_sym, get_pim_sym, get_pim_sym_real, get_pim_deri_sym, get_pim_deri_sym_real
from .core import get_entry

def obj_sym(phi, delta, opts):
    """Compute objective function value for QSP optimization.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    delta : array_like
        Samples
    opts : dict
        Options dictionary containing target function and parameters

    Returns
    -------
    float
        Objective function value
    """
    m = len(delta)
    obj = np.zeros(m)
    for i in range(m):
        qspmat = get_unitary_sym(phi, delta[i], opts['parity'])
        obj[i] = 0.5 * (np.real(qspmat[0, 0]) - opts['target']([delta[i]]))**2

    return obj

def grad_sym(phi, delta, opts):
    """Compute gradient of objective function.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    delta : array_like
        Samples
    opts : dict
        Options dictionary containing target function and parameters

    Returns
    -------
    grad : ndarray
        Gradient of objective function
    obj : ndarray
        Objective function value
    """
    # Initial computation
    m = len(delta)
    d = len(phi)
    obj = np.zeros(m)
    grad = np.zeros((m, d))
    gate = np.array([[np.exp(1j * np.pi / 4), 0], [0, np.conj(np.exp(1j * np.pi / 4))]])
    exptheta = np.exp(1j * phi)
    targetx = opts['target']
    parity = opts['parity']

    # Start gradient evaluation
    for i in range(m):
        x = delta[i]
        Wx = np.array([[x, 1j * np.sqrt(1 - x**2)], [1j * np.sqrt(1 - x**2), x]])
        tmp_save1 = np.zeros((2, 2, d), dtype=complex)
        tmp_save2 = np.zeros((2, 2, d), dtype=complex)
        tmp_save1[:, :, 0] = np.eye(2)
        tmp_save2[:, :, 0] = np.dot(np.array([[exptheta[d-1], 0], [0, np.conj(exptheta[d-1])]]), gate)
        for j in range(1, d):
            tmp_save1[:, :, j] = np.dot(tmp_save1[:, :, j-1], np.dot(np.diag([exptheta[j-1], np.conj(exptheta[j-1])]), Wx))
            tmp_save2[:, :, j] = np.dot(np.dot(np.array([[exptheta[d-j-1], 0], [0, np.conj(exptheta[d-j-1])]]), Wx), tmp_save2[:, :, j-1])
        if parity == 1:
            qspmat = np.dot(np.dot(tmp_save2[:, :, d-1].T, Wx), tmp_save2[:, :, d-1])
            gap = np.real(qspmat[0, 0]) - targetx(x)
            leftmat = np.dot(tmp_save2[:, :, d-1].T, Wx)
            for j in range(d):
                grad_tmp = np.dot(np.dot(leftmat, tmp_save1[:, :, j]), np.array([[1j, -1j]]).T) * tmp_save2[:, :, d-j-1]
                grad[i, j] = 2 * np.real(grad_tmp[0, 0]) * gap
            obj[i] = 0.5 * (np.real(qspmat[0, 0]) - targetx(x))**2
        else:
            qspmat = np.dot(np.dot(tmp_save2[:, :, d-2].T, Wx), tmp_save2[:, :, d-1])
            gap = np.real(qspmat[0, 0]) - targetx(x)
            leftmat = np.dot(tmp_save2[:, :, d-2].T, Wx)
            for j in range(d):
                grad_tmp = np.dot(np.dot(leftmat, tmp_save1[:, :, j]), np.array([[1j, -1j]]).T) * tmp_save2[:, :, d-j-1]
                grad[i, j] = 2 * np.real(grad_tmp[0, 0]) * gap
            grad[i, 0] /= 2
            obj[i] = 0.5 * (np.real(qspmat[0, 0]) - targetx(x))**2

    return grad, obj

def grad_sym_real(phi, delta, opts):
    """Compute gradient using real arithmetic.

    Similar to grad_sym but uses only real arithmetic for efficiency.

    Parameters
    ----------
    phi : array_like
        Phase factors for QSP circuit
    delta : array_like
        Samples
    opts : dict
        Options dictionary containing target function and parameters

    Returns
    -------
    grad : ndarray
        Gradient of objective function
    obj : ndarray
        Objective function value
    """
    # Initial computation
    m = len(delta)
    d = len(phi)
    obj = np.zeros(m)
    grad = np.zeros((m, d))
    targetx = opts['target']
    parity = opts['parity']

    # Convert the phase factor used in LBFGS solver to reduced phase factors
    if parity == 0:
        phi[0] = phi[0] / 2

    # Start gradient evaluation
    for i in range(m):
        x = delta[i]
        y = get_pim_deri_sym_real(phi, x, parity)
        if parity == 0:
            y[0] = y[0] / 2
        y = -y  # Flip the sign
        gap = y[-1] - targetx([x])
        obj[i] = 0.5 * gap**2
        grad[i, :] = y[:-1] * gap

    return grad, obj
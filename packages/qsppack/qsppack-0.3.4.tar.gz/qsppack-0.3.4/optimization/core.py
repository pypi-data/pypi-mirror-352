"""Core Quantum Signal Processing functionality.

This module provides the fundamental operations needed for Quantum Signal Processing,
including unitary matrix construction and manipulation of phase factors.
"""

import numpy as np
from .utils import get_unitary_sym, get_pim_sym, get_pim_sym_real, get_pim_deri_sym, get_pim_deri_sym_real

def get_unitary(phase, x):
    """Compute QSP unitary matrix for given phase factors.

    This function constructs the full QSP unitary matrix for a given set of phase
    factors at a specific point. The unitary is built by alternating W(x) gates
    and phase rotations.

    Parameters
    ----------
    phase : array_like
        Phase factors for the QSP circuit. These are used to construct the
        phase rotation gates in the circuit.
    x : float
        Point at which to evaluate the unitary, must be in [-1, 1].

    Returns
    -------
    float
        Real part of the (1,1) element of the QSP unitary matrix, which
        represents the QSP approximation of the target function.

    Notes
    -----
    The unitary is constructed as:
    U = R(phi_0) * W(x) * R(phi_1) * W(x) * ... * R(phi_n)
    where R(phi) is a phase rotation gate and W(x) is the signal processing gate.
    """
    Wx = np.array([[x, 1j * np.sqrt(1 - x**2)], [1j * np.sqrt(1 - x**2), x]])
    expphi = np.exp(1j * phase)

    ret = np.array([[expphi[0], 0], [0, np.conj(expphi[0])]])

    for k in range(1, len(expphi)):
        temp = np.array([[expphi[k], 0], [0, np.conj(expphi[k])]])
        ret = np.dot(np.dot(ret, Wx), temp)

    targ = np.real(ret[0, 0])

    return targ

def get_entry(xlist, phase, opts):
    """Compute QSP unitary matrix entries for multiple points.

    This function evaluates the QSP unitary matrix at multiple points, handling
    both full and reduced phase factors. It can compute either the real or
    imaginary part of the (1,1) element based on the options.

    Parameters
    ----------
    xlist : array_like
        Points at which to evaluate the QSP unitary, must be in [-1, 1].
    phase : array_like
        Phase factors for the QSP circuit. Can be either full or reduced
        phase factors depending on opts['typePhi'].
    opts : dict
        Options dictionary containing:
        
        - targetPre : bool
            If True, compute real part (Pre), otherwise compute imaginary part (Pim)
        - parity : int
            Parity of the polynomial (0 for even, 1 for odd)
        - typePhi : {'full', 'reduced'}
            Type of phase factors provided:
            
            - 'full' : complete set of phase factors
            - 'reduced' : reduced set of phase factors (will be expanded)

    Returns
    -------
    ndarray
        QSP approximation values at each point in xlist. For targetPre=True,
        returns real part of (1,1) element; for targetPre=False, returns
        imaginary part.

    Notes
    -----
    When typePhi='reduced', the function expands the reduced phase factors to
    full phase factors using symmetry. For targetPre=False, it also adjusts
    the first and last phase factors by -π/4 to compute the imaginary part.
    """
    typePhi = opts['typePhi']
    targetPre = opts['targetPre']
    parity = opts['parity']

    d = len(xlist)
    ret = np.zeros(d)

    if typePhi == 'reduced':
        dd = 2 * len(phase) - 1 + parity
        phi = np.zeros(dd)
        phi[(dd - len(phase)):] = phase
        phi[:len(phase)] += phase[::-1]
    else:
        phi = phase

    if not targetPre:
        phi[0] -= np.pi / 4
        phi[-1] -= np.pi / 4

    for i in range(d):
        x = xlist[i]
        ret[i] = get_unitary(phi, x)

    return ret

def reduced_to_full(phi_cm, parity, targetPre):
    """Convert reduced phase factors to full phase factors for QSP.

    This function constructs the full set of phase factors required for the
    Quantum Signal Processing (QSP) unitary matrix from a reduced set. The
    conversion uses symmetry properties of the phase factors and handles
    both even and odd parity cases.

    Parameters
    ----------
    phi_cm : array_like
        Reduced phase factors. For even parity, these represent half the
        total phase factors; for odd parity, they represent the unique
        phase factors.
    parity : int
        Parity of the phase factors:
        
        - 0 : even parity (full length = 2*len(phi_cm) - 1)
        - 1 : odd parity (full length = 2*len(phi_cm))
    targetPre : bool
        Whether to adjust for target preparation:
        
        - True : add π/4 to the last phase factor
        - False : use phase factors as is

    Returns
    -------
    ndarray
        Full phase factors constructed by mirroring the reduced factors.
        The length depends on parity:
        
        - For even parity: 2*len(phi_cm) - 1
        - For odd parity: 2*len(phi_cm)

    Notes
    -----
    The full phase factors are constructed by:
    1. Copying the reduced factors to the right half
    2. Mirroring them to the left half
    3. Adjusting the last factor if targetPre is True
    """
    phi_right = phi_cm.copy()
    if targetPre:
        phi_right[-1] += np.pi / 4

    dd = 2 * len(phi_right)
    if parity == 0:
        dd -= 1

    phi_full = np.zeros(dd)
    phi_full[(dd - len(phi_right)):] = phi_right
    phi_full[:len(phi_right)] += phi_right[::-1]

    return phi_full

def F(phi, parity, opts):
    """Compute the Chebyshev coefficients of P_im.
    
    P_im is the imaginary part of the (1,1) element of the QSP unitary matrix.

    Parameters
    ----------
    phi : array_like
        Reduced phase factors
    parity : int
        Parity of phi (0 for even, 1 for odd)
    opts : dict
        Options dictionary with fields:
            - useReal : bool
                Whether to use real matrix multiplication

    Returns
    -------
    ndarray
        Chebyshev coefficients of P_im w.r.t. 
        T_(2k) for even parity or T_(2k-1) for odd parity
    """
    # Setup options for CM solver
    opts.setdefault('useReal', True)

    # Initial preparation
    d = len(phi)
    dd = 2 * d
    theta = np.arange(d + 1) * np.pi / dd
    M = np.zeros(2 * dd)

    if opts['useReal']:
        f = lambda x: [get_pim_sym_real(phi, xval, parity) for xval in x]
    else:
        f = lambda x: [get_pim_sym(phi, xval, parity) for xval in x]

    # Start Chebyshev coefficients evaluation
    M[:d+1] = f(np.cos(theta))
    M[d+1:dd+1] = (-1)**parity * M[d-1::-1]
    M[dd+1:] = M[dd-1:0:-1]
    M = np.fft.fft(M)  # FFT w.r.t. columns.
    M = np.real(M)
    M /= (2 * dd)
    M[1:-1] *= 2
    coe = M[parity:2*d:2]

    return coe

def F_Jacobian(phi, parity, opts):
    """Compute the Jacobian matrix of Chebyshev coefficients.

    Parameters
    ----------
    phi : array_like
        Reduced phase factors
    parity : int
        Parity of phi (0 for even, 1 for odd)
    opts : dict
        Options dictionary with fields:
            - useReal : bool
                Whether to use real matrix multiplication

    Returns
    -------
    ndarray
        Jacobian matrix of Chebyshev coefficients
    """
    # Setup options
    opts.setdefault('useReal', True)

    # Initial preparation
    if opts['useReal']:
        f = lambda x: get_pim_deri_sym_real(phi, x, parity)
    else:
        f = lambda x: get_pim_deri_sym(phi, x, parity)

    d = len(phi)
    dd = 2 * d
    theta = np.arange(d + 1) * np.pi / dd
    M = np.zeros((2 * dd, d + 1))

    for n in range(d + 1):
        M[n, :] = f(np.cos(theta[n]))

    M[d + 1:dd + 1, :] = (-1) ** parity * M[d - 1::-1, :]
    M[dd + 1:, :] = M[dd - 1:0:-1, :]

    M = np.fft.fft(M, axis=0)  # FFT w.r.t. columns.
    M = np.real(M[:dd + 1, :])
    M[1:-1, :] *= 2
    M /= (2 * dd)

    f = M[parity::2, -1][:d]
    df = M[parity::2, :-1][:d]

    return f, df
# import necessary dependencies
import numpy as np
from scipy.signal import fftconvolve
from scipy.fft import fft, ifft
import sympy as sp
from sympy import Poly


def b_from_cheb(c, parity):
    """
    Generate coefficients of b from Chebyshev coefficients of approximating polynomial.

    This function takes an array of Chebyshev coefficients of definite parity and returns a new
    array based on the specified parity. If the parity is even, the function
    creates an array of size `2*len(c) - 1`, otherwise it creates an array of
    size `2*len(c)`.

    Parameters
    ----------
    c : array_like
        Array of Chebyshev coefficients of the approximating polynomial with definite parity.
    parity : int
        Parity of the approximating polynomial.

    Returns
    -------
    ndarray
        An array of coefficients of complex polynomial b.

    Notes
    -----
    The function handles the input array differently based on the specified
    parity. For even parity, the new array is constructed by reversing the
    input array, halving it, and then adding the original array (also halved)
    starting from the middle. For odd parity, the process is similar but the
    new array is one element longer.

    Examples
    --------
    >>> b_from_cheb(np.array([2,-1,6,-7,1]), 0)
    array([ 0.5, -3.5,  3. , -0.5,  2. , -0.5,  3. , -3.5,  0.5])
    >>> b_from_cheb([1, 2, 3], 1)
    array([1.5, 1. , 0.5, 0.5, 1. , 1.5])
    """
    lenc = len(c)
    if parity == 0:  # even
        c_new = np.zeros(2*lenc-1)
        c_new[:lenc] = c[::-1] / 2
        c_new[lenc-1:] += c / 2
        return c_new
    else:  # odd
        c_new = np.zeros(2*lenc)
        c_new[:lenc] = c[::-1] / 2
        c_new[lenc:] = c / 2
        return c_new
    

def weiss(b, N):
    """
    Compute the Weiss algorithm to get coefficients of a given b.

    This function calculates the Weiss algorithm to get coefficients of a given b.
    The algorithm involves evaluating the polynomial at the Nth roots of unity, computing
    a logarithmic function, and applying the Fast Fourier Transform (FFT).

    Parameters
    ----------
    b : array_like
        Coefficients of the input polynomial.
    N : int
        The number of roots of unity to consider.

    Returns
    -------
    ndarray
        The polynomial coefficients of a.
    
    Examples
    --------
    >>> weiss(np.array([0.38157934, 0.05342111, 0.45789521]), 8)
    array([ 0.76099391, -0.08783997, -0.23742773])
    >>> weiss(np.array([ 2.37136846e-01,  1.06711580e-01,  4.32585034e-01, -3.04180174e-01, -4.74273691e-04,  5.21701060e-01]), 64)
    array([ 0.47379318,  0.09424218,  0.11612456, -0.24713393, -0.06540336, -0.26132533])
    """
    z = np.exp(1j*2*np.arange(N)*np.pi/N)  # get the Nth roots of unity
    bz = np.array([np.dot(b, np.pow(zj, np.arange(len(b)))) for zj in z])  # evaluate b(z) for all roots of unity
    R = 0.5 * np.log1p(-np.abs(bz)**2 + 0j)
    R_hat_full = fft(R) / N
    R_hat = np.append(R_hat_full[0], 2*R_hat_full[int(N/2):][::-1])  # discard positive frequencies, double negative frequencies
    G_star = np.array([np.dot(R_hat, np.pow(zj, np.arange(len(R_hat)))) for zj in z])
    a_star = ifft(np.exp(G_star))
    return np.real_if_close(np.append(a_star[0],a_star[-len(b)+1:][::-1]))


def inverse_nonlinear_FFT(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes the inverse nonlinear FFT of a and b.

    Parameters
    ----------
    a : np.ndarray
        Input array a of length n.
    b : np.ndarray
        Input array b of length n.

    Returns
    -------
    tuple of np.ndarray
        A tuple containing gammas, xi_n, and eta_n.
    
    Examples
    --------
    >>> inverse_nonlinear_FFT(np.array([0.1, -0.5, -0.6]), np.array([0.2, -0.5, 0.3]))[0]
    array([2., 1., 3.])
    """
    n = len(a)

    # Step 1: base case
    if n == 1:
        gammas = np.array([b[0]/a[0]])
        eta_1 = np.array([1 / np.sqrt(1 + np.abs(gammas[0])**2)])
        xi_1 = gammas * eta_1
        return gammas, xi_1, eta_1
    
    # Step 2: first recursive call
    m = int(np.ceil(n/2))
    gammas = np.zeros(n)
    gammas[:m], xi_m, eta_m = inverse_nonlinear_FFT(a[:m], b[:m])

    # Step 3: compute coefficients of am and bm
    eta_m_sharp = np.append(0, eta_m[::-1])
    xi_m_sharp = np.append(0, xi_m[::-1])
    am = (fftconvolve(eta_m_sharp, a) + fftconvolve(xi_m_sharp, b))[m:]
    bm = (fftconvolve(eta_m, b) - fftconvolve(xi_m, a))[m:]

    # Step 4: second recursive call
    gammas[m:], xi_mn, eta_mn = inverse_nonlinear_FFT(am[:n-m], bm[:n-m])

    # Step 5: final calculation and output
    xi_n = fftconvolve(eta_m_sharp, xi_mn) + np.append(fftconvolve(xi_m, eta_mn), 0)
    eta_n = np.append(fftconvolve(eta_m, eta_mn), 0) - fftconvolve(xi_m_sharp, xi_mn)
    return gammas, xi_n, eta_n


def forward_nlft(gammas):
    """
    Computes the forward nonlinear Fourier transform (NLFT) for a given set of gammas.

    This function constructs a matrix product based on the input gammas and extracts
    the polynomial coefficients from the resulting matrix.

    Parameters
    ----------
    gammas : array_like
        An array of gamma values used in the transformation.

    Returns
    -------
    np.ndarray
        An array of polynomial coefficients derived from the transformation.

    Examples
    --------
    >>> forward_nlft(np.array([0.1, -0.5, 0.3]))
    array([...])  # Example output, replace with actual expected result
    """
    z = sp.symbols('z')
    res = np.eye(2)
    for k, gamma in enumerate(gammas):
        res = res @ np.array([[1, gamma*(z**k)], [-np.conj(gamma)*(z**(-k)), 1]]) / np.sqrt(1 + np.abs(gamma)**2)
    return np.array(Poly(res[0,1]).all_coeffs()[::-1], dtype=np.float64)
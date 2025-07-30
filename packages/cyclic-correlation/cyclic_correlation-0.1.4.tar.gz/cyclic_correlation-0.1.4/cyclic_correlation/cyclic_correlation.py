"""
cyclic_correlation.py

A module for computing the cyclic cross-correlation between two 1D signals.
Supports both FFT-based and analytic methods, with optional normalization and padding.

Author: Andrea Novero
License: BSD 3-Clause License
"""

import warnings
import numpy as np


def ZC_sequence(r, q, N):
    """
    Generates a discrete Zadoff-Chu (ZC) sequence.

    A Zadoff-Chu sequence is a complex-valued sequence with constant amplitude and zero autocorrelation properties, 
    commonly used in communication systems such as LTE.

    Parameters:
        r (int): Root index of the ZC sequence. Must satisfy 1 <= r <= N.
        q (int): Cyclic shift of the sequence. Must satisfy q >= 0.
        N (int): Length of the sequence. Must satisfy N >= 1.

    Returns:
        numpy.ndarray: The generated Zadoff-Chu sequence of length N.

    Raises:
        ValueError: If r is not in the range [1, N], or if q < 0, or if N < 1.

    Notes:
        - The sequence is generated according to the formula:
          ZC[k] = exp(-1j * (pi / N) * r * ((k % N) + N % 2 + 2 * (q % N)) * (k % N))
        - The input parameters should be integers.
    """

    # Input validation
    if not (isinstance(r, int) and isinstance(q, int) and isinstance(N, int)):
        raise ValueError("Parameters r, q, and N must all be integers.")
    if N < 1:
        raise ValueError("Parameter N must be >= 1.")
    if not (1 <= r <= N):
        raise ValueError("Parameter r must satisfy 1 <= r <= N.")
    if q < 0:
        raise ValueError("Parameter q must be >= 0.")

    k = np.arange(0, N)
    #Compute Z_q1
    ZC = np.exp(-1j * (np.pi / N) * r * ((k%N)+ N%2 + 2 * (q%N)) * (k%N))
    return ZC
    
def check_inputs_define_limits(s1, s2, method, padded):
    """
    Validates and preprocesses input signals for cyclic correlation.

    Parameters
    ----------
    s1 : array-like
        First input signal (1D).
    s2 : array-like
        Second input signal (1D).
    method : str
        Correlation method, either 'fft' or 'analytic'.
    padded : bool
        If True, pad shorter signal to match the length of the longer one.
        If False, truncate longer signal to match the length of the shorter one.

    Returns
    -------
    s1 : np.ndarray
        Processed first signal.
    s2 : np.ndarray
        Processed second signal.

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    # Check for None inputs
    if s1 is None or s2 is None:
        raise ValueError("Input signals s1 and s2 must not be None.")

    # Ensure inputs are array-like
    if not (isinstance(s1, (list, np.ndarray)) and isinstance(s2, (list, np.ndarray))):
        raise ValueError("Input signals s1 and s2 must be lists or numpy arrays.")

    # Convert to numpy arrays
    s1 = np.array(s1) if not isinstance(s1, np.ndarray) else s1
    s2 = np.array(s2) if not isinstance(s2, np.ndarray) else s2

    # Ensure 1D arrays
    if s1.ndim != 1 or s2.ndim != 1:
        raise ValueError("Both s1 and s2 must be 1D arrays.")

    # Validate method
    valid_methods = ("fft", "analytic")
    if method not in valid_methods:
        raise ValueError(f"Invalid method '{method}'. Supported methods are {valid_methods}.")

    # Handle length mismatch
    if s1.shape[0] != s2.shape[0]:
        if padded:
            # Pad the shorter signal
            if s1.shape[0] > s2.shape[0]:
                s2 = np.pad(s2, (0, s1.shape[0] - s2.shape[0]), mode='constant')
                warnings.warn("s2 is padded to s1 length")
            else:
                s1 = np.pad(s1, (0, s2.shape[0] - s1.shape[0]), mode='constant')
                warnings.warn("s1 is padded to s2 length")
        else:
            # Truncate the longer signal
            min_len = min(s1.shape[0], s2.shape[0])
            s1 = s1[:min_len]
            s2 = s2[:min_len]
            warnings.warn("Signals are truncated to the length of the shorter one")

    return s1, s2

def cyclic_corr(s1, s2, method="fft", padded=True, normalized=True):
    """
    Compute the cyclic cross-correlation between two 1D signals.

    Parameters
    ----------
    s1 : array-like
        First input signal (1D). Must be a list or numpy array.
    s2 : array-like
        Second input signal (1D). Must be a list or numpy array.
    method : str, optional
        Correlation method: 'fft' (default) or 'analytic'.
    padded : bool, optional
        If True, pad shorter signal to match the longer one (default True).
        If False, truncate longer signal to match the shorter one.
    normalized : bool, optional
        If True, normalize the correlation output (default True).

    Returns
    -------
    Z : np.ndarray
        Cyclic cross-correlation sequence.
    max_val : float
        Maximum absolute value in the correlation sequence.
    t_max : int
        Index of the maximum absolute value.
    min_val : float
        Minimum absolute value in the correlation sequence.

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    # Only allow list or numpy array types for s1 and s2
    if not (isinstance(s1, (list, np.ndarray)) and isinstance(s2, (list, np.ndarray))):
        raise ValueError("Input signals s1 and s2 must be lists or numpy arrays.")

    s1, s2 = check_inputs_define_limits(s1, s2, method, padded)

    n= max(s1.shape[0],s2.shape[0])

    if not padded:
        n = min(s1.shape[0], s2.shape[0])


    if method == "analytic":
        # Analytic computation of cyclic cross-correlation
        Z = []
        for t in range(n):
            Zk = 0
            for k in range(n):
                Zk += s1[k] * np.conj(s2[(k + t) % n])
            Zl = 0
            for l in range(n):
                Zl += np.conj(s1[l]) * s2[(l + t) % n]
            Z.append(Zk * Zl)
        Z = np.array(Z)
        if normalized:
            Z = Z / (n ** 2)
    else:
        # FFT-based computation
        X = np.fft.fft(s1)
        Y = np.fft.fft(s2)
        Z = np.fft.ifft(X * np.conj(Y))
        if normalized:
            Z = Z / n

    abs_Z = np.abs(Z)
    max_val = np.max(abs_Z)
    min_val = np.min(abs_Z)
    t_max = np.argmax(abs_Z)

    return Z, max_val, t_max, min_val

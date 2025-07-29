from functools import cached_property
from typing import Callable, Tuple

import numpy as np
from numba import njit
from numpy import signedinteger


# noinspection PyPep8Naming
class FwtTools:
    def __init__(
            self,
            scaling_func: Callable[[np.ndarray], np.ndarray] = None,
            h_coeffs: np.ndarray = None,
            kmin: int = -100,
            kmax: int = 100
    ):
        if (scaling_func is None and h_coeffs is None) or (scaling_func is not None and h_coeffs is not None):
            raise ValueError("Must provide either h_coeffs or scaling_func")

        self.kmax = kmax
        self.kmin = kmin
        self.k_range = np.arange(self.kmin, self.kmax + 1)

        if scaling_func is not None:
            if not callable(scaling_func):
                raise TypeError("scaling_func must be a callable object")

            if not isinstance(kmax, int) or kmax < 0:
                raise ValueError("K_MAX must be a non-negative integer")

            self.scaling_func = scaling_func
            self.h_coeffs = self.__h_coeffs
        elif h_coeffs is not None:
            self.h_coeffs = h_coeffs

    def __fourier_nodal_func(self, x: np.ndarray) -> np.ndarray:
        """
        Numerical calculation of coefficients c of the system of orthogonal shifts of the nodal function,
        by guided by the equality: D(t) = 1 / Ф(t)
        Source: C.K.Chui, An Introduction to Wavelets, 2001
        """
        # scaling function values array
        scaling_func_values = self.scaling_func(self.k_range)
        # mask Ф(t) values array
        mask_f = np.fft.fft(scaling_func_values)
        # mask D(t) values array
        mask_d = 1 / mask_f
        # nodal function values array
        dk_shuffled = np.fft.ifft(mask_d).real
        dk = np.roll(dk_shuffled, -1)

        # sum over all k's
        return np.sum(self.scaling_func(x) * dk[self.k_range + self.kmax], axis=1)

    @cached_property
    def __c_coeffs(self) -> np.ndarray:
        """ Scaling function coefficients """
        # to obtain the h_coeffs coefficients,
        # we need to find the values of the nodal function on the segment [-kmax/2;kmax/2] with step 1/2
        x_step = 0.5
        x = self.k_range * x_step
        x_minus_k = x[:, None] - self.k_range[None, :]  # shape (2M+1, K)
        return self.__fourier_nodal_func(x_minus_k)

    @cached_property
    def __h_coeffs(self) -> np.ndarray:
        """ Normalized scaling function coefficients used by Mallat algorithm """
        return self.__c_coeffs / np.sqrt(2)

    def nodal_func(self, x: np.ndarray, k_range: np.ndarray) -> np.ndarray:
        x_minus_k = x[:, None] - k_range[None, :]

        # scaling function values array
        scaling_func_values = self.scaling_func(k_range)
        # mask Ф(t) values array
        mask_f = np.fft.fft(scaling_func_values)
        # mask D(t) values array
        mask_d = 1 / mask_f
        # nodal function values array
        dk_shuffled = np.fft.ifft(mask_d).real
        dk = np.roll(dk_shuffled, -1)

        # sum over all k's
        kmax = int(np.max(k_range))
        return np.sum(self.scaling_func(x_minus_k) * dk[k_range + kmax], axis=1)

    def fwt(
            self,
            signal: np.ndarray,
            alpha: float = 1.,
            upscale: int = 0,
            on_iter: Callable[[np.ndarray, int], None] = lambda S_main, j: None,
    ) -> np.ndarray:
        """
        Fast wavelet transform algorithm realization

            :param signal: array of values of the analyzed signal
            :param alpha: percentage of wavelet transform coefficients preserved after filtering
            :param upscale: how many iterations to skip before stopping the algorithm
            :param on_iter: function, that invokes on each iteration

            :returns: coefficients preserved after filtering
        """
        if not (0 <= alpha <= 1):
            raise ValueError("Alpha must be a number between 0 and 1")
        M, J = _get_signal_info(signal)

        S_main = np.copy(signal)
        # Buffer array
        S_buf = np.zeros(M)

        for j in range(1, J + 1 - upscale):
            _iter_mallat_analyze(S_main, S_buf, M, j, self.h_coeffs, self.kmin, self.kmax)
            on_iter(S_main, j)

        return _compress(S_main, M, alpha)

    def ifwt(self, wavelet_coefficients: np.ndarray, scaling_func_coeffs: np.ndarray = None,
             downscale: int = 0) -> np.ndarray:
        if scaling_func_coeffs is None:
            scaling_func_coeffs = self.h_coeffs
        M, J = _get_signal_info(wavelet_coefficients)
        if J - downscale < 1:
            raise ValueError(f"Downscale must be lower than {J}")

        return _mallat_synthesize(wavelet_coefficients, M, J, scaling_func_coeffs, self.kmin, self.kmax, downscale)


def _get_signal_info(values: np.ndarray) -> Tuple[int, int]:
    if len(values.shape) > 1:
        raise ValueError("Values must be a 1D array")

    values_len = len(values)
    M = values_len
    frac, J = np.modf(np.log2(M))
    if not np.isclose(frac // 1, 0):
        raise ValueError(f"Values length must be the power of 2, values length = {values_len}")

    return M, int(J)


# noinspection PyPep8Naming
@njit(cache=True, parallel=True, nogil=True, fastmath=True)
def _iter_mallat_analyze(
        S_main: np.ndarray,
        S_buf: np.ndarray,
        M: int,
        j: int,
        h: np.ndarray,
        kmin: int,
        kmax: int,
) -> None:
    S_len = M // (2 ** j)  # number of S coefficients on layer j
    for m in range(S_len):
        # S
        S_buf[m] = 0
        for k in range(kmin + 2 * m, kmax + 2 * m + 1):
            S_buf[m] += h[k - 2 * m - kmin] * S_main[np.mod(k, 2 * S_len)]

        # D
        S_buf[m + S_len] = 0
        for k in range(1 + 2 * m - kmax, 1 + 2 * m - kmin + 1):
            S_buf[m + S_len] += ((-1) ** k) * h[1 - k + 2 * m - kmin] * S_main[np.mod(k, 2 * S_len)]

    # copying
    S_main[0:(2 * S_len)] = S_buf[0:(2 * S_len)]


# noinspection PyPep8Naming
def _compress(
        wavelet_coefficients: np.ndarray,
        M: int,
        alpha: float,
) -> np.ndarray:
    S_main = np.copy(wavelet_coefficients)
    if alpha == 1:
        return S_main
    buf = np.sort(np.abs(S_main))[::-1]  # Sorting by decreasing modulus
    num = round(alpha * M)  # Number of the last wavelet transform coefficient to store
    lvl = buf[num - 1]  # Zeroing threshold
    # Zeroing of elements whose modulus is less than the zeroing threshold
    for m in range(M):
        if abs(S_main[m]) < lvl:
            S_main[m] = 0
    return S_main


# noinspection PyPep8Naming
@njit(cache=True, fastmath=True)
def _mallat_synthesize(
        wavelet_coefficients: np.ndarray,
        M: int,
        J: int,
        h: np.ndarray,
        kmin: int,
        kmax: int,
        downscale: int,
) -> np.ndarray:
    S_main = np.copy(wavelet_coefficients)
    # Buffer array
    S_buf = np.zeros_like(S_main)

    for j in range(J - 1 - downscale, -1, -1):
        _iter_mallat_synthesize(S_main, S_buf, M, j, h, kmin, kmax)
    return S_main


# noinspection PyPep8Naming
@njit(cache=True, parallel=True, nogil=True, fastmath=True)
def _iter_mallat_synthesize(
        S_main: np.ndarray,
        S_buf: np.ndarray,
        M: int,
        j: signedinteger,
        h: np.ndarray,
        kmin: int,
        kmax: int,
) -> None:
    S_len = round(M / 2 ** j)  # number of S coefficients on layer j
    previous_layer_S_len = round(M / 2 ** (j + 1))  # number of S coefficients on layer j + 1

    for m in range(S_len):
        sum_1 = 0
        for k in range(int(np.ceil((m - kmax) / 2)), int(np.floor((m - kmin) / 2)) + 1):
            sum_1 += h[m - 2 * k - kmin] * S_main[(k % previous_layer_S_len)]

        sum_2 = 0
        for k in range(int(np.ceil((m + kmin - 1) / 2)), int(np.floor((m + kmax - 1) / 2)) + 1):
            sum_2 += h[1 - m + 2 * k - kmin] * S_main[(k % previous_layer_S_len) + previous_layer_S_len]

        S_buf[m] = sum_1 + (-1) ** m * sum_2

    # copying
    S_main[:S_len] = S_buf[:S_len]

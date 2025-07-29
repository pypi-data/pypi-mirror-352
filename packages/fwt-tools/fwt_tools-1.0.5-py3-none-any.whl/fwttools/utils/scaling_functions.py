from typing import Callable

import numpy as np


def build_lorentzian(sigma: float = 1, shift: float = 0.25) -> Callable[[np.ndarray], np.ndarray]:
    """
    Constructs a Lorentzian function with the specified width and center.

    Parameters:
        sigma (float): The scale parameter (related to half-width at half-maximum). Default is 1.
        shift (float): The center location of the peak. Default is 0.25.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that computes the Lorentzian profile
        at given input values.
    """
    sigma_pow_2 = sigma ** 2

    def lorentzian(x: np.ndarray) -> np.ndarray:
        return sigma_pow_2 / (((x - shift) ** 2) + sigma_pow_2)

    return lorentzian


def build_gaussian(sigma: float = 1, shift: float = 0.25) -> Callable[[np.ndarray], np.ndarray]:
    """
    Constructs a Gaussian function with the specified standard deviation and center.

    Parameters:
        sigma (float): The standard deviation (spread) of the Gaussian. Default is 1.
        shift (float): The mean (center) of the Gaussian peak. Default is 0.25.

    Returns:
        Callable[[np.ndarray], np.ndarray]: A function that computes the Gaussian profile
        at given input values.
    """
    double_sigma_pow_2 = (2 * sigma ** 2)

    def gaussian(x: np.ndarray) -> np.ndarray:
        return np.exp(-(x - shift) ** 2 / double_sigma_pow_2)

    return gaussian


def meyer(t: np.ndarray) -> np.ndarray:
    """https://en.wikipedia.org/wiki/Meyer_wavelet using Valenzuela and de Oliveira formula"""
    result = np.zeros_like(t)

    # t = 0
    zero_mask = t == 0
    result[zero_mask] = 2 / 3 + 4 / (3 * np.pi)

    # t ≠ 0
    nonzero_mask = ~zero_mask
    t_nz = t[nonzero_mask]
    numerator = np.sin((2 * np.pi / 3) * t_nz) + (4 / 3) * t_nz * np.cos((4 * np.pi / 3) * t_nz)
    denominator = np.pi * t_nz - (16 * np.pi / 9) * t_nz ** 3
    result[nonzero_mask] = numerator / denominator

    return result


def haar(x: np.ndarray) -> np.ndarray:
    return ((0 <= x) & (x < 1)).astype(int)


def build_lanczos(a: float, shift=0.25) -> Callable[[np.ndarray], np.ndarray]:
    """https://en.wikipedia.org/wiki/Lanczos_resampling"""

    def lanczos(x: np.ndarray) -> np.ndarray:
        pi = np.pi
        x_shifted = x - shift
        result = np.zeros_like(x_shifted)

        # x == 0 → L(x) = 1
        zero_mask = np.isclose(x_shifted, 0.0)
        result[zero_mask] = 1.0

        # -a <= x < a and x ≠ 0
        inside_mask = (~zero_mask) & (np.abs(x_shifted) < a)
        x_inside = x_shifted[inside_mask]

        numerator = a * np.sin(pi * x_inside) * np.sin(pi * x_inside / a)
        denominator = (pi * x_inside) ** 2
        result[inside_mask] = numerator / denominator

        return result

    return lanczos


def build_b_spline(n: int, shift: float = 0.25) -> Callable[[np.ndarray], np.ndarray]:
    if n < 1:
        raise ValueError("n must be greater than 0")

    def b_spline(x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64) - shift
        factor1 = (n + 2 * x) / (2 * (n - 1))
        factor2 = (n - 2 * x) / (2 * (n - 1))

        prev_b_spline = build_b_spline(n - 1)
        return factor1 * prev_b_spline(x + 0.5) + factor2 * prev_b_spline(x - 0.5)

    # Base case: B1(x)
    if n == 1:
        return lambda x: np.where(np.abs(x) <= 0.5, 1.0, 0.0)
    else:
        return b_spline

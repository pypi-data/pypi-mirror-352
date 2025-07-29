import numpy as np
from numba import njit


@njit(cache=True, fastmath=True)
def __scaling_func_coeffs(
        omega: float,
        theta_1s_0_q12: float,
        sigma: float,
        p_range: np.ndarray
) -> np.ndarray:
    # Integer array for p to preserve behavior of (-1)**p
    p_vals = p_range[np.newaxis, :]  # shape (1, N)
    k_vals = p_range[:, np.newaxis]  # shape (N, 1)

    # Compute exponent matrix
    exponent = ((k_vals + 0.25) ** 2 - (p_vals + 0.5) ** 2) / (2 * sigma ** 2)

    # Apply the mask p >= |k| to exclude invalid terms
    exponent = np.where(p_vals >= np.abs(k_vals), exponent, -np.inf)  # use -inf to zero out exp()

    term = ((-1.) ** p_vals) * np.exp(exponent)  # now safe due to integer p_vals
    result = np.sum(term, axis=1)

    return (omega / theta_1s_0_q12) * result


@njit(cache=True, parallel=True, nogil=True, fastmath=True)
def nodal_func(x: float, sigma: float, p_max: int) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive float")
    if p_max <= 0:
        raise ValueError("p_max must be positive integer")

    p_range = np.arange(-p_max, p_max + 1)
    q = np.exp(-1 / (2 * sigma ** 2))

    theta_2_0_q12 = np.sum(q ** (((p_range + 0.5) ** 2) / 2))
    theta_1s_0_q12 = np.sum((4 * p_range + 1) * np.exp(-(2 * p_range + 0.5) ** 2 / (2 * sigma ** 2)))

    omega = np.sqrt(theta_2_0_q12 / (2 * sigma * np.sqrt(np.pi)))
    scaling_func_coeffs = __scaling_func_coeffs(omega, theta_1s_0_q12, sigma, p_range)

    gaussians = np.exp(-(x - p_range) ** 2 / (2 * sigma ** 2))
    result = np.sum(scaling_func_coeffs * gaussians)

    return result


def h_coeffs(sigma: float, h_max: int, p_max: int = 100, shift: float = 0.25) -> np.ndarray:
    if h_max <= 0 or p_max <= 0 or sigma <= 0:
        raise ValueError("All parameters must be positive")

    two_sqrt = np.sqrt(2)
    k_range = np.arange(-h_max, h_max + 1)
    x_vals = k_range / 2 - shift

    fi_vals = np.array([nodal_func(x, sigma, p_max) for x in x_vals])

    return fi_vals / two_sqrt

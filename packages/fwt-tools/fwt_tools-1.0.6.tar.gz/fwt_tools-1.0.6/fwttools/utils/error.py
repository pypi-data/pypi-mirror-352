import numpy as np


def relative_rmse_error(signal: np.ndarray, approximation: np.ndarray) -> float:
    """Compute relative root-mean-square error"""
    return np.linalg.norm(approximation - signal) / np.linalg.norm(signal)


def parseval_identity(f_time: np.ndarray, f_freq: np.ndarray) -> tuple[float, float]:
    """Return left and right sides of Parseval's equality."""
    time_energy = np.sum(np.abs(f_time) ** 2)
    freq_energy = np.sum(np.abs(f_freq) ** 2)
    return time_energy, freq_energy

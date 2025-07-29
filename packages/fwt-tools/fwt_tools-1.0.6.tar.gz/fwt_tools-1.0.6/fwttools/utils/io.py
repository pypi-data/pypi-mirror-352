import csv

import numpy as np

from fwttools.fwt_tools import FwtTools


def f_write_h_coeffs(fwt_tools: FwtTools, filename: str):
    """ Write computed coefficients h to file """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["k", "H(k)"])
        writer.writerows(zip(fwt_tools.k_range, fwt_tools.h_coeffs))

def f_read_h_coeffs(filename: str) -> FwtTools:
    """ Read computed coefficients h from file"""
    k_list = []
    h_list = []

    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Пропускаем заголовок

        for row in reader:
            k = int(row[0])
            h = np.float64(row[1])
            k_list.append(k)
            h_list.append(h)

    k_range = np.array(k_list, dtype=int)
    h_coeffs = np.array(h_list, dtype=np.float64)

    kmin, kmax = k_range.min(), k_range.max()
    arange = np.arange(kmin, kmax + 1)

    if np.allclose(k_range, arange):
        raise ValueError('k_range from file in have a bad format')

    return FwtTools(h_coeffs=h_coeffs, kmin=kmin, kmax=k_range.max())

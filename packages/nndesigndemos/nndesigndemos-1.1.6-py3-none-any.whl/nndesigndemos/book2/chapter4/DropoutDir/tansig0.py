import numpy as np


def tansig0(n, code):
    if code == 'f':
        a = 2 / (1 + np.exp(-2 * n)) - 1
        a[~np.isfinite(a)] = np.sign(n[~np.isfinite(a)])  # Handling non-finite values
        return a
    elif code == 'd':
        a = n
        return 1 - (a ** 2)

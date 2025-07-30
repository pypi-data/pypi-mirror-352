import numpy as np


def softmax0(n, code):
    if code == 'f':
        numer = np.exp(n)
        denom = np.sum(numer, axis=0)
        return numer / denom
    elif code == 'd':
        a = n
        d = []
        for q in range(a.shape[1]):
            d_q = np.diag(a[:, q]) * np.sum(a[:, q]) - np.outer(a[:, q].T, a[:, q])
            d.append(d_q)
        return d

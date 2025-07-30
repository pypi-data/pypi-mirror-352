import numpy as np


def crossentr(a, t, code):
    if code == 'f':
        return np.sum(-t * np.log(a))
    elif code == 'd':
        return -t / a
    else:
        print(f'Cross-entropy code {code} is not valid.')

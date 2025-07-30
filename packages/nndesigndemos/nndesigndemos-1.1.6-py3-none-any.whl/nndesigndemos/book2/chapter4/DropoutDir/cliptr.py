import numpy as np


def cliptr(tr, epochs):
    """
    Clip the training record to the final number of epochs.

    Parameters:
    tr : dict
        Training record dictionary, where each key holds a matrix representing values for each epoch.
    epochs : int
        The final number of epochs to retain in the training record.

    Returns:
    tr : dict
        The clipped training record dictionary.
    """
    for name in tr.keys():
        tr[name] = tr[name][:epochs+1]

    return tr

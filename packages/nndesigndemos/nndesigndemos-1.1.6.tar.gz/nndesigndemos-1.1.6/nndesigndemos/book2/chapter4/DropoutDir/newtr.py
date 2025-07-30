import numpy as np


def newtr(epochs, *args):
    """
    Create a new training record with any number of optional fields.

    Parameters:
    epochs : int or list
        If an integer, it defines the number of epochs.
        If a list, it defines the range [firstEpoch, epochs].
    *args : str
        Optional field names to add to the training record.

    Returns:
    tr : dict
        A dictionary representing the training record.
    """
    # Check input arguments
    if len(args) < 0:
        raise ValueError("Not enough input arguments.")

    # Create training record dictionary
    tr = {}
    tr['epochs'] = np.arange(0, epochs + 1)
    num_epochs = epochs + 1

    # Add optional fields initialized to NaN
    blank = np.full(num_epochs, np.nan)
    for name in args:
        tr[name] = blank.copy()  # Copy ensures each field gets its own blank array

    return tr

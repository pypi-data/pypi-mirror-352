import numpy as np


def getx(net):
    """
    Get all network weights and biases as a single vector.

    Parameters:
    net : dict
        Neural network structure containing weights (net['w']) and biases (net['b']).

    Returns:
    x : numpy array
        Vector of weight and bias values.
    """
    M = len(net['f'])  # Number of layers
    x = []

    for i in range(M):
        x.extend(net['w'][i].T.ravel())  # Flatten the weights and append
        x.extend(net['b'][i].ravel())  # Append the biases

    return np.array(x)  # Convert to numpy array

import numpy as np


def simnet(net, P):
    """
    Simulate the neural network with input P.

    Parameters:
    net : dict
        Neural network structure containing weights, biases, activation functions, etc.
    P : numpy array
        Input data to the network (each column is an input vector).

    Returns:
    a : list
        List of activations for each layer.
    """
    do = net['do']
    mask = net['mask']
    doflag = net['doflag']
    M = len(net['f'])
    r, q = P.shape

    if r != net['R']:
        print(f"Input dimension {r} does not match network size {net['R']}.")
        return None

    a = [P]  # Initialize activations with input

    # Iterate through each layer
    for m in range(M):
        n = np.dot(net['w'][m], a[m]) + net['b'][m] * np.ones((1, q))
        a_m = net['f'][m](n, 'f')  # Apply activation function
        if do[m] != 1 and doflag:
            a_m = mask[m] * a_m  # Apply dropout mask if needed
        a.append(a_m)

    return a[1:]  # Return activations for each layer, excluding input

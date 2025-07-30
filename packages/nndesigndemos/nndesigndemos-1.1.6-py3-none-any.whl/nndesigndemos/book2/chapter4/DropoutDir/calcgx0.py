import numpy as np
import logging
from nndesigndemos.book2.chapter4.DropoutDir.softmax0 import softmax0
from nndesigndemos.book2.chapter4.DropoutDir.crossentr import crossentr
from nndesigndemos.book2.chapter4.DropoutDir.tansig0 import tansig0

# Setup logging
logging.basicConfig(level=logging.WARN)


def calcgx0(net, p, a, t):
    """
    Calculate the gradient of the network's loss function with respect to weights and biases.

    Parameters:
    net : dict
        Neural network structure containing weights, biases, activation functions, etc.
    p : numpy array
        Input data to the network.
    a : list
        Activations from each layer of the network (output of simnet).
    t : numpy array
        Target output data for calculating performance.

    Returns:
    gX : numpy array
        Flattened vector of the gradients of weights and biases.
    """
    doflag = net['doflag']
    do = net['do']
    mask = net['mask']
    S = net['S']
    M = len(S)  # Number of layers
    r, q = p.shape

    if r != net['R']:
        logging.error(f"Input dimension {r} does not match network size {net['R']}.")
        return None

    logging.info(f"Network has {M} layers. Batch size is {q}.")

    s = [None] * M  # Initialize list to hold sensitivities
    gw = [None] * M  # Gradient for weights
    gb = [None] * M  # Gradient for biases

    # Output layer sensitivities
    dp = net['perf'](a[M - 1], t, 'd')  # Gradient of performance function
    df = net['f'][M - 1](a[M - 1], 'd')  # Derivative of activation function

    s[M - 1] = np.zeros((S[M - 1], q))  # Sensitivity for last layer
    logging.info(f"Calculating sensitivities for output layer {M}.")

    if isinstance(df, list):  # If df is cell-like (list), process for each input
        for qq in range(q):
            s[M - 1][:, qq] = np.dot(df[qq], dp[:, qq])
    else:
        s[M - 1] = df * dp

    # Apply dropout mask if necessary
    if do[M - 1] != 1 and doflag:
        s[M - 1] = mask[M - 1] * s[M - 1]

    # Gradients for output layer
    gw[M - 1] = np.dot(s[M - 1], a[M - 2].T)  # Weights gradient
    gb[M - 1] = np.dot(s[M - 1], np.ones((q, 1)))  # Biases gradient
    logging.info(f"Gradients for output layer {M} calculated.")

    # Backpropagate through hidden layers
    for i in range(M - 2, -1, -1):
        logging.info(f"Backpropagating through layer {i + 1}.")
        s[i] = np.dot(net['w'][i + 1].T, s[i + 1])  # Sensitivity for current layer

        tf = net['f'][i]
        if tf == 'purelin0':  # Linear activation
            logging.debug("Using purelin activation.")
        elif tf == tansig0:  # Tanh activation
            logging.debug("Using tansig activation.")
            s[i] = (1 - (a[i] ** 2)) * s[i]
        elif tf == 'logsig0':  # Logistic sigmoid activation
            logging.debug("Using logsig activation.")
            s[i] = a[i] * (1 - a[i]) * s[i]
        else:  # Other activation functions
            Fdot = net['f'][i](a[i], 'd')
            if isinstance(Fdot, list):
                for qq in range(q):
                    s[i][:, qq] = np.dot(Fdot[qq], s[i][:, qq])
            else:
                s[i] = Fdot * s[i]

        # Apply dropout mask if necessary
        if do[i] != 1 and doflag:
            s[i] = mask[i] * s[i]

        # Calculate gradients
        if i == 0:
            gw[i] = np.dot(s[i], p.T)
        else:
            gw[i] = np.dot(s[i], a[i - 1].T)
        gb[i] = np.dot(s[i], np.ones((q, 1)))
        logging.info(f"Gradients for layer {i + 1} calculated.")

    # Flatten and concatenate all gradients into a single vector
    gX = []
    for i in range(M):
        gX.extend(gw[i].T.ravel())
        gX.extend(gb[i].T.ravel())

    logging.info("All gradients calculated and concatenated into a single vector.")

    return np.array(gX)

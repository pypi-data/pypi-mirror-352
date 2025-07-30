from nndesigndemos.book2.chapter4.DropoutDir.simnet import simnet


def calcperf0(net, p, t):
    """
    Calculate the performance of the neural network.

    Parameters:
    net : dict
        Neural network structure containing weights, biases, performance function, etc.
    p : numpy array
        Input data to the network (each column is an input vector).
    t : numpy array
        Target output data for calculating performance.

    Returns:
    perf : float
        Performance value calculated using the network's performance function.
    a : list
        List of activations for each layer.
    """
    M = len(net['f'])  # Number of layers
    a = simnet(net, p)  # Get activations by simulating the network
    perf = net['perf'](a[M - 1], t, 'f')  # Calculate performance using the last layer output
    return perf, a

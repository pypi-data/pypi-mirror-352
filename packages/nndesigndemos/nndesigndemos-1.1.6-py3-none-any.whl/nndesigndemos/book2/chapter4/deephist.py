import numpy as np
import matplotlib.pyplot as plt


# Tanh activation function
def tansig1(n):
    return np.tanh(n)


# ReLU's activation function
def poslin1(n):
    return np.maximum(0, n)


def batch_norm(x, gamma, beta, eps=1e-5):
    mean = np.mean(x, axis=1, keepdims=True)
    variance = np.var(x, axis=1, keepdims=True)
    x_norm = (x - mean) / np.sqrt(variance + eps)
    return gamma * x_norm + beta


# Simulation function
def simdeep(net, p, batch_norm_enabled):
    M = len(net['w'])
    # q = p.shape[1]
    a = [None] * (M + 1)
    a[0] = p

    for m in range(M):
        z = np.dot(net['w'][m], a[m]) + net['b'][m].reshape(-1, 1)
        if batch_norm_enabled:
            z = batch_norm(z, net['gamma'][m], net['beta'][m])
        a[m + 1] = net['tf'](z)

    return a


# Plot histograms function
def plothist(a):
    M1 = len(a)
    plt.figure(num="Histograms of Inputs & Layer Outputs")

    for k in range(M1):
        plt.subplot(1, M1, k + 1)
        plt.hist(a[k].ravel(), bins=20, range=(-3, 3))
        plt.title(f'a_{k}')

    plt.show()


# Deep network simulation and histogram plotting
def deephist(r, q, initial, input_distrib, act_func_key, layer_size, batch_norm_enabled):

    # Mean and variance of the input
    pmean = np.zeros((r, 1))
    pstd = np.ones((r, 1))

    if input_distrib == 'Uniform':
        samples = (np.random.uniform(size=(r, q)) - 0.5) * np.sqrt(12)
    elif input_distrib == 'Normal':
        samples = np.random.randn(r, q)
    else:
        return

    # print('np.mean(samples), np.var(samples)', round(np.mean(samples), 1), round(np.var(samples), 1), samples.shape)

    # Generate inputs
    p = np.diag(pstd.flatten()) @ samples + pmean @ np.ones((1, q))

    # Layer sizes
    s = [4] * layer_size
    rr = [r] + s[:-1]
    M = len(s)

    act_func_dic = {
        'tansig': tansig1,
        'poslin': poslin1,
    }
    act_func = act_func_dic[act_func_key]

    # Set activation functions and initialize weights and biases
    net = {
        'tf': act_func,
        'w': [],
        'b': [],
        'gamma': [],
        'beta': [],
    }

    for m in range(M):
        if initial == 'Xavier':
            stdw = np.sqrt(2 / (s[m] + rr[m]))
        elif initial == 'Kaiming':
            stdw = np.sqrt(2 / rr[m])
        elif initial == 'Small random':
            stdw = 0.1
        else:
            print(f'{initial} is not a valid weight initialization type.')
            return

        w = stdw * np.random.randn(s[m], rr[m])
        b = np.zeros((s[m], 1))
        gamma = np.ones((s[m], 1))
        beta = np.zeros((s[m], 1))
        net['w'].append(w)
        net['b'].append(b)
        net['gamma'].append(gamma)
        net['beta'].append(beta)

    # Run the network
    a = simdeep(net, p, batch_norm_enabled)
    return a


if __name__ == '__main__':
    r = 6  # Input dimension
    q = 2000  # Number of examples

    # Set weight initialization algorithm
    initial = ["Small random", "Xavier", "Kaiming"][1]

    # Activation functions
    act_func_key = ["tansig", "poslin"][0]

    input_distrib = ["Normal", "Uniform"][0]

    layer_size = 4
    batch_norm_enabled = True

    # Run the simulation
    a = deephist(r, q, initial, input_distrib, act_func_key, layer_size, batch_norm_enabled)
    print(len(a))
    # Plot histograms
    plothist(a)

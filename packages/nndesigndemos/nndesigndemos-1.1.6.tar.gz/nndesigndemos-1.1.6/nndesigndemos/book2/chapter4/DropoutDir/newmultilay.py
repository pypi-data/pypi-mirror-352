import numpy as np


# Helper function for weight initialization
def initialize_weights(r, s, initial_type, m):
    if initial_type == 'xav':
        stdw = np.sqrt(2 / (s + r))
        w = stdw * np.random.randn(s, r)
        b = np.zeros((s, 1))

        # # The following four lines are for the test purpose
        # stdw = 0.0814
        # rng = np.random.default_rng(seed=m+4)
        # w = rng.standard_normal((s, r))
        # np.savetxt(f"random_numbers{m}.txt", w)

    elif initial_type == 'kai':
        stdw = np.sqrt(2 / r)
        w = stdw * np.random.randn(s, r)
        b = np.zeros((s, 1))
    elif initial_type == 'smr':
        stdw = 0.1
        w = stdw * np.random.randn(s, r)
        b = np.zeros((s, 1))
    else:
        raise ValueError(f"{initial_type} is not a valid weight initialization type.")
    return w, b


def newmultilay(params):
    r = params['R']
    f = params['f']
    s = params['S']
    initial = params['Init']

    net = {
        'R': r, # Input size
        'S': s, # Layer sizes
        'f': f, # Assign activation functions
        'perf': params['perf'], # Assign performance function
        'w': [],
        'b': [],
        'mask': [],
    }

    dimX = 0
    rr = [r] + s[:-1]  # layer sizes

    for m in range(len(s)):
        w, b = initialize_weights(rr[m], s[m], initial, m)
        net['w'].append(w)
        net['b'].append(b)
        net['mask'].append(np.ones((s[m], 1)))  # Placeholder for masks, default is ones
        dimX += w.shape[0] * (w.shape[1] + 1)  # count weights and biases

    net['dimX'] = dimX

    net['do'] = params['do']
    net['doflag'] = params['doflag']

    return net


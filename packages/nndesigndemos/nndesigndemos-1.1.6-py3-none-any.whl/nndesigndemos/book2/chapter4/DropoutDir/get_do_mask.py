import numpy as np


def get_do_mask(net, P):
    """
    Generate dropout masks for each layer of the network.

    Parameters:
    net : dict
        Neural network structure containing layer sizes ('S') and dropout probabilities ('do').
    P : numpy array
        Input data to the network (each column is an input vector).

    Returns:
    net : dict
        Updated network structure with dropout masks stored in 'mask'.
    """
    do = net['do']
    s = net['S']
    M = len(net['f'])  # Number of layers
    _, q = P.shape  # Get the batch size from the input data

    mask = [None] * M  # Initialize mask list

    # Generate dropout masks for each layer
    for m in range(M):
        if do[m] != 1:  # Apply dropout only if dropout probability is not 1 (i.e., no dropout)
            sm = s[m]  # Number of neurons in layer m
            num = round(do[m] * sm)  # Number of neurons to keep (based on dropout rate)

            # # The following line gives a certain list for test usage
            # ind1 = np.array([112, 245, 240, 114, 135, 269, 41, 42, 230, 146, 196, 248, 24, 166, 201, 33, 242, 252, 297, 154, 123, 35, 181, 19, 211, 210, 81, 199, 132, 2, 193, 179, 40, 257, 60, 7, 209, 249, 29, 237, 11, 276, 189, 235, 75, 236, 102, 150, 225, 90, 116, 285, 293, 266, 0, 45, 69, 229, 217, 65, 117, 106, 12, 36, 3, 115, 148, 105, 299, 282, 113, 83, 216, 164, 213, 37, 1, 138, 58, 80, 130, 215, 220, 14, 73, 142, 70, 247, 187, 251, 21, 174, 291, 78, 244, 25, 71, 232, 289, 190, 280, 121, 147, 195, 294, 5, 28, 108, 74, 136, 202, 125, 177, 141, 18, 140, 175, 227, 263, 182, 4, 47, 159, 77, 139, 128, 290, 30, 226, 208, 233, 288, 207, 6, 278, 64, 87, 39, 231, 212, 188, 10, 93, 119, 268, 270, 149, 44, 89, 52, 110, 143, 185, 158, 219, 206, 183, 101, 172, 250, 296, 170, 284, 95, 168, 243, 163, 161, 104, 218, 292, 178, 55, 118, 22, 272, 261, 171, 169, 200, 84, 223, 144, 23, 46, 221, 287, 273, 224, 51, 38, 184, 57, 264, 31, 63, 156, 254, 56, 96, 111, 129, 191, 100, 186, 256, 260, 124, 94, 99, 91, 267, 277, 271, 145, 203, 155, 198, 32, 79, 241, 53, 82, 34, 67, 17, 279, 61, 298, 192, 134, 109, 88, 228, 13, 275, 133, 72, 137, 20, 295, 194, 107, 167, 66, 92, 103, 120, 54, 127, 15, 165, 49, 197, 26, 62, 205, 214, 152, 258, 265, 162, 222, 255, 50, 239, 234, 153, 180, 98, 97, 274, 122, 246, 253, 43, 131, 286, 204, 238, 68, 160, 86, 76, 262, 259, 157, 176, 281, 8, 173, 16, 126, 48, 85, 9, 151, 59, 27, 283])[:num]

            ind1 = np.random.permutation(sm)[:num]  # Randomly select neurons to keep
            temp = np.zeros(sm)  # Initialize a temporary mask
            temp[ind1] = 1  # Set selected neurons to 1 (keep them)
            mask[m] = np.outer(temp, np.ones(q))  # Create mask for the entire batch size

    net['mask'] = mask  # Store the dropout masks in the network structure

    return net

import numpy as np
import math
from scipy.io import savemat, loadmat
from nndesigndemos.get_package_path import PACKAGE_PATH


def logsig(x):
    return 1 / (1 + math.e ** (-x))


N_POINTS = 200

# Optimal parameters
W1, B1 = np.array([[10], [10]]), np.array([[-5], [5]])
W2, B2 = np.array([[1, 1]]), np.array([[-1]])

# Function to approximate
p = np.arange(-2, 2.1, 0.1).reshape(1, -1)
f_target = logsig(W2.dot(logsig(W1.dot(p) + B1)) + B2)

# Varying W1_1, W2_1
W1_1, W2_1 = np.linspace(-5, 15, N_POINTS), np.linspace(-5, 15, N_POINTS)
e_w11_w21 = np.zeros((N_POINTS, N_POINTS))
for i in range(N_POINTS):
    for j in range(N_POINTS):
        w1, w2 = np.array([[W1_1[i]], [10]]), np.array([[W2_1[j], 1]])
        a2 = logsig(np.dot(w2, logsig(np.dot(w1, p) + B1)) + B2)
        e = (f_target - a2)
        e_w11_w21[i, j] = np.sum(e ** 2)
f_data = loadmat(PACKAGE_PATH + "Data/nndbp{}.mat".format(1))
savemat(PACKAGE_PATH + "Data/nndbp_new_1.mat", {"x1": W1_1, "y1": W2_1, "E1": e_w11_w21.T, "levels": f_data["levels"]})

# Varying W1_1, b1_1
W1_1, B1_1 = np.linspace(-10, 30, N_POINTS), np.linspace(-30, 20, N_POINTS)
e_w11_b11 = np.zeros((N_POINTS, N_POINTS))
for i in range(N_POINTS):
    for j in range(N_POINTS):
        w1, b1 = np.array([[W1_1[i]], [10]]), np.array([[B1_1[j]], [5]])
        a2 = logsig(np.dot(W2, logsig(np.dot(w1, p) + b1)) + B2)
        e = (f_target - a2)
        e_w11_b11[i, j] = np.sum(e ** 2)
f_data = loadmat(PACKAGE_PATH + "Data/nndbp{}.mat".format(2))
savemat(PACKAGE_PATH + "Data/nndbp_new_2.mat", {"x1": W1_1, "y1": B1_1, "E1": e_w11_b11.T, "levels": f_data["levels"]})

# Varying b1_1, b1_2
B1_1, B1_2 = np.linspace(-10, 10, N_POINTS), np.linspace(-10, 10, N_POINTS)
e_b11_b21 = np.zeros((N_POINTS, N_POINTS))
for i in range(N_POINTS):
    for j in range(N_POINTS):
        b1 = np.array([[B1_1[i]], [B1_2[j]]])
        a2 = logsig(np.dot(W2, logsig(np.dot(W1, p) + b1)) + B2)
        e = (f_target - a2)
        e_b11_b21[i, j] = np.sum(e ** 2)
f_data = loadmat(PACKAGE_PATH + "Data/nndbp{}.mat".format(3))
savemat(PACKAGE_PATH + "Data/nndbp_new_3.mat", {"x1": B1_1, "y1": B1_2, "E1": e_b11_b21.T, "levels": f_data["levels"]})


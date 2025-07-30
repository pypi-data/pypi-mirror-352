import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class MarquardtStep(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(MarquardtStep, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Marquardt Step", 12, "\n\nClick on the contour plot\nto do a single step of the\n"
                                                "Marquardt learning\nalgorithm.\n\nThe black arrow indicates\nthe "
                                                "Gauss-Newton step.\n\nThe red arrow indicates\nthe gradient direction.\n\n"
                                                "The blue line indicates\nthe Marquardt step as\nmu is ajusted.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 90, 500, 200), description_coords=(535, 90, 450, 300))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)

        self.make_plot(1, (65, 285, 390, 390))
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.path, = self.axes.plot([], label="Gradient Descent Path", color="blue")
        self.x_data, self.y_data = [], []
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.v1 = self.axes.quiver([0], [0], [0], [0], units="xy", scale=1, color="r")
        self.v2 = self.axes.quiver([0], [0], [0], [0], units="xy", scale=1, color="k")
        self.pair_of_params = 1
        self.pair_params = [["W1(1, 1)", "W2(1, 1)"], ["W1(1, 1)", "b1(1)"], ["b1(1)", "b1(2)"]]
        self.plot_data()

        self.x, self.y = None, None

        self.make_combobox(1, ["W1(1, 1), W2(1, 1)", 'W1(1, 1), b1(1)', 'b1(1), b1(2)'],
                           (525, 400, 175, 50), self.change_pair_of_params,
                           "label_combo", "Pair of parameters", (545, 380, 150, 50))

        self.mu = 0.0012
        self.nu = 1.2
        self.canvas.draw()

    def change_pair_of_params(self, idx):
        self.pair_of_params = idx + 1
        self.init_params()
        self.plot_data()
        self.canvas.draw()

    def plot_data(self):
        self.x_data = []
        self.y_data = []
        self.path.set_data(self.x_data, self.y_data)
        while self.axes.collections:
            for collection in self.axes.collections:
                collection.remove()
        f_data = loadmat(PACKAGE_PATH + "Data/nndbp_new_{}.mat".format(self.pair_of_params))
        x1, y1 = np.meshgrid(f_data["x1"], f_data["y1"])
        self.axes.contour(x1, y1, f_data["E1"], list(f_data["levels"].reshape(-1)))
        if self.pair_of_params == 1:
            self.axes.scatter([self.W1[0, 0]], [self.W2[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-5, 15)
            self.axes.set_ylim(-5, 15)
            self.axes.set_xticks([-5, 0, 5, 10])
            self.axes.set_yticks([-5, 0, 5, 10])
        elif self.pair_of_params == 2:
            self.axes.scatter([self.W1[0, 0]], [self.b1[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 30)
            self.axes.set_ylim(-20, 10)
            self.axes.set_xticks([-10, 0, 10, 20])
            self.axes.set_yticks([-20, -15, -10, -5, 0, 5])
        elif self.pair_of_params == 3:
            self.axes.scatter([self.b1[0, 0]], [self.b1[1, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 10)
            self.axes.set_ylim(-10, 10)
            self.axes.set_xticks([-10, -5, 0, 5])
            self.axes.set_xticks([-10, -5, 0, 5])
        self.axes.set_xlabel(self.pair_params[self.pair_of_params - 1][0], fontsize=8)
        self.axes.xaxis.set_label_coords(0.95, -0.025)
        self.axes.set_ylabel(self.pair_params[self.pair_of_params - 1][1], fontsize=8)
        self.axes.yaxis.set_label_coords(-0.025, 0.95)

    def train_step(self):

        self.mu /= self.nu
        self.a1 = np.kron(self.a1, np.ones((1, 1)))
        d2 = self.log_delta(self.a2)
        d1 = self.log_delta(self.a1, d2, self.W2)
        jac1 = self.marq(np.kron(self.P, np.ones((1, 1))), d1)
        jac2 = self.marq(self.a1, d2)
        jac = np.hstack((jac1, d1.T))
        jac = np.hstack((jac, jac2))
        jac = np.hstack((jac, d2.T))
        if self.pair_of_params == 1:
            jac = np.array([list(jac[:, 0]), list(jac[:, 4])]).T
        elif self.pair_of_params == 2:
            jac = np.array([list(jac[:, 0]), list(jac[:, 2])]).T
        elif self.pair_of_params == 3:
            jac = np.array([list(jac[:, 2]), list(jac[:, 3])]).T

        je = np.dot(jac.T, self.e.T)
        grad = np.sqrt(np.dot(je.T, je)).item()
        if grad < 0:
            return

        jj = np.dot(jac.T, jac)
        dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
        gx, gy = dw[0].item(), dw[1].item()
        dist = np.sqrt(gx ** 2 + gy ** 2)
        self.v2 = self.axes.quiver([self.Lx], [self.Ly], [gx], [gy], units="xy", scale=1, color="black")
        Lx1, Ly1 = self.Lx + gx, self.Ly + gy
        self.x_data.append(Lx1.item())
        self.y_data.append(Ly1.item())

        dw = -je
        gx, gy = dw[0], dw[1]
        gx1 = dist * gx / np.sqrt(gx ** 2 + gy ** 2)
        gy1 = dist * gy / np.sqrt(gx ** 2 + gy ** 2)
        self.v1 = self.axes.quiver([self.Lx], [self.Ly], [gx1], [gy1], units="xy", scale=1, color="r")

        while True:

            dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
            W1, b1, W2, b2 = np.copy(self.W1), np.copy(self.b1), np.copy(self.W2), np.copy(self.b2)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + dw[0], self.W2[0, 0] + dw[1]
                W1[0, 0], W2[0, 0] = self.x, self.y
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + dw[0], self.b1[0] + dw[1]
                W1[0, 0], b1[0] = self.x, self.y
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + dw[0], self.b1[1] + dw[1]
                b1[0], b1[1] = self.x, self.y

            Lx1, Ly1 = self.x, self.y
            self.x_data.append(Lx1.item())
            self.y_data.append(Ly1.item())

            self.a1 = self.logsigmoid_stable(np.dot(W1, self.P) + b1)
            self.a2 = self.logsigmoid_stable(np.dot(W2, self.a1) + b2)
            self.e = self.T - self.a2
            error = np.dot(self.e, self.e.T).item()

            if abs(error - self.error_prev) > 0.001 * self.error_prev:
                self.mu *= self.nu
                if self.mu > 1e10:
                    break
            else:
                break

        if error < self.error_prev:
            self.W1, self.b1, self.W2, self.b2 = np.copy(W1), np.copy(b1), np.copy(W2), np.copy(b2)
            self.error_prev = error


        if self.error_prev <= 0.0000001:
            return

        return

    def on_mouseclick(self, event):

        self.init_params()
        self.plot_data()
        self.x_data, self.y_data = [event.xdata], [event.ydata]
        self.x, self.y = event.xdata, event.ydata
        if self.pair_of_params == 1:
            self.W1[0, 0], self.W2[0, 0] = self.x, self.y
        elif self.pair_of_params == 2:
            self.W1[0, 0], self.b1[0] = self.x, self.y
        elif self.pair_of_params == 3:
            self.b1[0], self.b1[1] = self.x, self.y

        self.path.set_data(self.x_data, self.y_data)
        self.a1 = self.logsigmoid_stable(np.dot(self.W1, self.P) + self.b1)
        self.a2 = self.logsigmoid_stable(np.dot(self.W2, self.a1) + self.b2)
        self.e = self.T - self.a2
        self.error_prev = np.dot(self.e, self.e.T).item()
        self.ii = np.eye(2)
        self.Lx, self.Ly = self.x, self.y

        self.train_step()
        self.path.set_data([self.x_data[0]] + self.x_data[1:][::-1], [self.y_data[0]] + self.y_data[1:][::-1])
        self.canvas.draw()

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])
        self.mu = 0.0012
        self.nu = 1.2

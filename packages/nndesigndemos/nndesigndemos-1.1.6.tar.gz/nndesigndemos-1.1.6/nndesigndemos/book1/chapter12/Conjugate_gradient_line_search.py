import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ConjugateGradientLineSearch(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ConjugateGradientLineSearch, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Conjugate Gradient Line Search", 12, "\nUse the pop up menu below\nto select the network\nparameters"
                                                                " to train\nwith backpropagation.\n\nThe corresponding contour\nplot "
                                                                "is shown below.\n\nClick in the contour graph\nto start "
                                                                "the conjugate\ngradient line search.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 90, 500, 200), description_coords=(535, 90, 450, 300))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)
        self.tau1 = 1 - 0.618
        self.delta = 0.32
        self.tol = 0.03 / 20
        self.scale = 2
        self.b_max = 26
        self.n = 2
        self.lr, self.epochs = None, None

        self.make_plot(1, (20, 280, 480, 400))
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.init_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=6, color="k")
        self.x_data_circ, self.y_data_circ = [], []
        self.path, = self.axes.plot([], linestyle='none', marker='.', color="blue")
        self.x_data, self.y_data = [], []
        self.path_k, =  self.axes.plot([], linestyle='none', marker='.', color="black")
        self.x_data_k, self.y_data_k = [], []
        self.path_r, = self.axes.plot([], linestyle='none', marker='.', color="red")
        self.x_data_r, self.y_data_r = [], []
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        self.pair_of_params = 1
        self.pair_params = [["W1(1, 1)", "W2(1, 1)"], ["W1(1, 1)", "b1(1)"], ["b1(1)", "b1(2)"]]
        self.plot_data()

        self.x, self.y = None, None

        self.make_combobox(1, ["W1(1, 1), W2(1, 1)", 'W1(1, 1), b1(1)', 'b1(1), b1(2)'],
                           (525, 360, 175, 50), self.change_pair_of_params,
                           "label_combo", "Pair of parameters", (545, 340, 150, 50))

        self.canvas.draw()

    def change_pair_of_params(self, idx):
        self.pair_of_params = idx + 1
        self.init_params()
        self.init_point_1.set_data([], [])
        self.plot_data()
        self.canvas.draw()

    def plot_data(self):
        self.x_data, self.x_data_k, self.x_data_r, self.x_data_circ = [], [], [], []
        self.y_data, self.y_data_k, self.y_data_r, self.y_data_circ = [], [], [], []
        self.path.set_data(self.x_data, self.y_data)
        self.path_k.set_data(self.x_data_k, self.y_data_k)
        self.path_r.set_data(self.x_data_k, self.y_data_r)
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

        for idx in range(3):

            a = 0
            aold = 0
            b = self.delta
            faold = self.fa

            W1t, b1t, W2t, b2t = np.copy(self.W1), np.copy(self.b1), np.copy(self.W2), np.copy(self.b2)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.W2[0, 0] + b * self.dW2[0, 0]
                W1t[0, 0] = self.x
                W2t[0, 0] = self.y
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.b1[0] + b * self.db1[0]
                W1t[0, 0] = self.x
                b1t[0] = self.y
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + b * self.db1[0], self.b1[1] + b * self.db1[1]
                b1t[0] = self.x
                b1t[1] = self.y
            n1 = np.dot(W1t, self.P) + b1t
            a1 = self.logsigmoid(n1)
            n2 = np.dot(W2t, a1) + b2t
            a2 = self.logsigmoid(n2)
            e = self.T - a2
            fb = np.sum(e * e)

            while self.fa > fb and b < self.b_max:
                aold = a
                faold = self.fa
                self.fa = fb
                a = b
                b *= self.scale
                if self.pair_of_params == 1:
                    self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.W2[0, 0] + b * self.dW2[0, 0]
                    W1t[0, 0] = self.x
                    W2t[0, 0] = self.y
                elif self.pair_of_params == 2:
                    self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.b1[0] + b * self.db1[0]
                    W1t[0, 0] = self.x
                    b1t[0] = self.y
                elif self.pair_of_params == 3:
                    self.x, self.y = self.b1[0] + b * self.db1[0], self.b1[1] + b * self.db1[1]
                    b1t[0] = self.x
                    b1t[1] = self.y
                n1 = np.dot(W1t, self.P) + b1t
                a1 = self.logsigmoid(n1)
                n2 = np.dot(W2t, a1) + b2t
                a2 = self.logsigmoid(n2)
                e = self.T - a2
                fb = np.sum(e * e)
                self.x_data_circ.append(self.x)
                self.y_data_circ.append(self.y)
            a = aold
            self.fa = faold

            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + a * self.dW1[0, 0], self.W2[0, 0] + a * self.dW2[0, 0]
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + a * self.dW1[0, 0], self.b1[0] + a * self.db1[0]
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + a * self.db1[0], self.b1[1] + a * self.db1[1]
            self.x_data_k.append(self.x)
            self.y_data_k.append(self.y)
            self.x_data_circ.append(self.x)
            self.y_data_circ.append(self.y)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.W2[0, 0] + b * self.dW2[0, 0]
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + b * self.dW1[0, 0], self.b1[0] + b * self.db1[0]
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + b * self.db1[0], self.b1[1] + b * self.db1[1]
            self.x_data_k.append(self.x)
            self.y_data_k.append(self.y)
            self.x_data_circ.append(self.x)
            self.y_data_circ.append(self.y)

            c = a + self.tau1 * (b - a)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + c * self.dW1[0, 0], self.W2[0, 0] + c * self.dW2[0, 0]
                W1t[0, 0] = self.x
                W2t[0, 0] = self.y
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + c * self.dW1[0, 0], self.b1[0] + c * self.db1[0]
                W1t[0, 0] = self.x
                b1t[0] = self.y
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + c * self.db1[0], self.b1[1] + c * self.db1[1]
                b1t[0] = self.x
                b1t[1] = self.y
            n1 = np.dot(W1t, self.P) + b1t
            a1 = self.logsigmoid(n1)
            n2 = np.dot(W2t, a1) + b2t
            a2 = self.logsigmoid(n2)
            e = self.T - a2
            fc = np.sum(e * e)
            self.x_data_k.append(self.x)
            self.y_data_k.append(self.y)

            d = b - self.tau1 * (b - a)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + d * self.dW1[0, 0], self.W2[0, 0] + d * self.dW2[0, 0]
                W1t[0, 0] = self.x
                W2t[0, 0] = self.y
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + d * self.dW1[0, 0], self.b1[0] + d * self.db1[0]
                W1t[0, 0] = self.x
                b1t[0] = self.y
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + d * self.db1[0], self.b1[1] + d * self.db1[1]
                b1t[0] = self.x
                b1t[1] = self.y
            n1 = np.dot(W1t, self.P) + b1t
            a1 = self.logsigmoid(n1)
            n2 = np.dot(W2t, a1) + b2t
            a2 = self.logsigmoid(n2)
            e = self.T - a2
            fd = np.sum(e * e)
            self.x_data_k.append(self.x)
            self.y_data_k.append(self.y)

            while b - a > self.tol:
                if (fc < fd and fb >= np.min([self.fa, fc, fd])) or self.fa < np.min([fb, fc, fd]):
                    b = d
                    d = c
                    fb = fd
                    c = a + self.tau1 * (b - a)
                    fd = fc
                    if self.pair_of_params == 1:
                        self.x, self.y = self.W1[0, 0] + c * self.dW1[0, 0], self.W2[0, 0] + c * self.dW2[0, 0]
                        W1t[0, 0] = self.x
                        W2t[0, 0] = self.y
                    elif self.pair_of_params == 2:
                        self.x, self.y = self.W1[0, 0] + c * self.dW1[0, 0], self.b1[0] + c * self.db1[0]
                        W1t[0, 0] = self.x
                        b1t[0] = self.y
                    elif self.pair_of_params == 3:
                        self.x, self.y = self.b1[0] + c * self.db1[0], self.b1[1] + c * self.db1[1]
                        b1t[0] = self.x
                        b1t[1] = self.y
                    n1 = np.dot(W1t, self.P) + b1t
                    a1 = self.logsigmoid(n1)
                    n2 = np.dot(W2t, a1) + b2t
                    a2 = self.logsigmoid(n2)
                    e = self.T - a2
                    fc = np.sum(e * e)
                    self.x_data_k.append(self.x)
                    self.y_data_k.append(self.y)
                else:
                    a = c
                    c = d
                    self.fa = fc
                    d = b - self.tau1 * (b - a)
                    fc = fd
                    if self.pair_of_params == 1:
                        self.x, self.y = self.W1[0, 0] + d * self.dW1[0, 0], self.W2[0, 0] + d * self.dW2[0, 0]
                        W1t[0, 0] = self.x
                        W2t[0, 0] = self.y
                    elif self.pair_of_params == 2:
                        self.x, self.y = self.W1[0, 0] + d * self.dW1[0, 0], self.b1[0] + d * self.db1[0]
                        W1t[0, 0] = self.x
                        b1t[0] = self.y
                    elif self.pair_of_params == 3:
                        self.x, self.y = self.b1[0] + d * self.db1[0], self.b1[1] + d * self.db1[1]
                        b1t[0] = self.x
                        b1t[1] = self.y
                    n1 = np.dot(W1t, self.P) + b1t
                    a1 = self.logsigmoid(n1)
                    n2 = np.dot(W2t, a1) + b2t
                    a2 = self.logsigmoid(n2)
                    e = self.T - a2
                    fd = np.sum(e * e)
                    self.x_data_k.append(self.x)
                    self.y_data_k.append(self.y)
            self.x_data_r.append(self.x)
            self.y_data_r.append(self.y)
            if self.pair_of_params == 1:
                self.x, self.y = self.W1[0, 0] + a * self.dW1[0, 0], self.W2[0, 0] + a * self.dW2[0, 0]
                self.W1[0, 0] = self.x
                self.W2[0, 0] = self.y
            elif self.pair_of_params == 2:
                self.x, self.y = self.W1[0, 0] + a * self.dW1[0, 0], self.b1[0] + a * self.db1[0]
                self.W1[0, 0] = self.x
                self.b1[0] = self.y
            elif self.pair_of_params == 3:
                self.x, self.y = self.b1[0] + a * self.db1[0], self.b1[1] + a * self.db1[1]
                self.b1[0] = self.x
                self.b1[1] = self.y
            self.x_data.append(self.x)
            self.y_data.append(self.y)
            self.n1 = np.dot(self.W1, self.P) + self.b1
            self.a1 = self.logsigmoid(self.n1)
            self.n2 = np.dot(self.W2, self.a1) + self.b2
            self.a2 = self.logsigmoid(self.n2)
            self.e = self.T - self.a2
            self.D2 = self.a2 * (1 - self.a2) * self.e
            self.D1 = self.a1 * (1 - self.a1) * np.dot(self.W2.T, self.D2)
            self.gW1 = np.dot(self.D1, self.P.T)
            self.gb1 = np.dot(self.D1, np.ones((self.D1.shape[1], 1)))
            self.gW2 = np.dot(self.D2, self.a1.T)
            self.gb2 = np.dot(self.D2, np.ones((self.D1.shape[1], 1)))
            if self.pair_of_params == 1:
                nrmn = self.gW1[0, 0] ** 2 + self.gW2[0, 0] ** 2
            elif self.pair_of_params == 2:
                nrmn = self.gW1[0, 0] ** 2 + self.gb1[0] ** 2
            elif self.pair_of_params == 3:
                nrmn = self.gb1[0] ** 2 + self.gb1[1] ** 2
            if idx % self.n == 0:
                Z = nrmn / self.nrmo
            else:
                Z = 0
            self.dW1_old = self.gW1 + self.dW1_old * Z
            self.db1_old = self.gb1 + self.db1_old * Z
            self.dW2_old = self.gW2 + self.dW2_old * Z
            self.db2_old = self.gb2 + self.db2_old * Z
            self.nrmo = nrmn
            if self.pair_of_params == 1:
                nrm = np.sqrt(self.dW1_old[0, 0] ** 2 + self.dW2_old[0, 0] ** 2)
            elif self.pair_of_params == 2:
                nrm = np.sqrt(self.dW1_old[0, 0] ** 2 + self.db1_old[0] ** 2)
            elif self.pair_of_params == 3:
                nrm = np.sqrt(self.db1_old[0] ** 2 + self.db1_old[1] ** 2)
            self.dW1, self.db1, self.dW2, self.db2 = self.dW1_old / nrm, self.db1_old / nrm, self.dW2_old / nrm, self.db2_old / nrm

    def on_mouseclick(self, event):
        self.init_params()
        self.x_data, self.y_data = [], []
        self.x_data_k, self.y_data_k = [], []
        self.x_data_r, self.y_data_r = [], []
        self.x_data_circ, self.y_data_circ = [], []
        self.path.set_data(self.x_data, self.y_data)
        self.path_k.set_data(self.x_data_k, self.y_data_k)
        self.path_r.set_data(self.x_data_r, self.y_data_r)
        self.x_data, self.y_data = [event.xdata], [event.ydata]
        self.x, self.y = event.xdata, event.ydata
        if self.pair_of_params == 1:
            self.W1[0, 0], self.W2[0, 0] = self.x, self.y
        elif self.pair_of_params == 2:
            self.W1[0, 0], self.b1[0, 0] = self.x, self.y
        elif self.pair_of_params == 3:
            self.b1[0, 0], self.b1[1, 0] = self.x, self.y
        self.n1 = np.dot(self.W1, self.P) + self.b1
        self.a1 = self.logsigmoid(self.n1)
        self.n2 = np.dot(self.W2, self.a1) + self.b2
        self.a2 = self.logsigmoid(self.n2)
        self.e = self.T - self.a2
        self.fa = np.sum(self.e * self.e)
        self.D2 = self.a2 * (1 - self.a2) * self.e
        self.D1 = self.a1 * (1 - self.a1) * np.dot(self.W2.T, self.D2)
        self.gW1 = np.dot(self.D1, self.P.T)
        self.gb1 = np.dot(self.D1, np.ones((self.D1.shape[1], 1)))
        self.gW2 = np.dot(self.D2, self.a1.T)
        self.gb2 = np.dot(self.D2, np.ones((self.D1.shape[1], 1)))
        if self.pair_of_params == 1:
            self.nrmo = self.gW1[0, 0] ** 2 + self.gW2[0, 0] ** 2
        elif self.pair_of_params == 2:
            self.nrmo = self.gW1[0, 0] ** 2 + self.gb1[0] ** 2
        elif self.pair_of_params == 3:
            self.nrmo = self.gb1[0] ** 2 + self.gb1[1] ** 2
        self.nrmrt = np.sqrt(self.nrmo)
        self.dW1_old, self.db1_old, self.dW2_old, self.db2_old = self.gW1, self.gb1, self.gW2, self.gb2
        self.dW1, self.db1, self.dW2, self.db2 = self.gW1 / self.nrmrt, self.gb1 / self.nrmrt, self.gW2 / self.nrmrt, self.gb2 / self.nrmrt
        self.train_step()

        if self.pair_of_params in [2, 3]:
            self.y_data_k = [y[0] for y in self.y_data_k]
            self.y_data = [(y[0] if isinstance(y, np.ndarray) else y) for y in self.y_data]
            self.y_data_r = [y[0] for y in self.y_data_r]
            self.y_data_circ = [y[0] for y in self.y_data_circ]

            if self.pair_of_params == 3:
                self.x_data_k = [x[0] for x in self.x_data_k]
                self.x_data = [(x[0] if isinstance(x, np.ndarray) else x) for x in self.x_data]
                self.x_data_r = [x[0] for x in self.x_data_r]
                self.x_data_circ = [x[0] for x in self.x_data_circ]

        self.path_k.set_data(self.x_data_k, self.y_data_k)
        self.path.set_data(self.x_data, self.y_data)
        self.path_r.set_data(self.x_data_r, self.y_data_r)
        self.init_point_1.set_data([event.xdata] + self.x_data_circ, [event.ydata] + self.y_data_circ)
        self.canvas.draw()

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])

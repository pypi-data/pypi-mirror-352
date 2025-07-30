from PyQt6 import QtWidgets, QtCore
import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class Marquardt(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Marquardt, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Marquardt", 12, "\nUse the pop up menu below\nto select the network\nparameters"
                                           " to train\nwith backpropagation.\n\nThe corresponding contour\nplot "
                                           "is shown below.\n\nClick in the contour graph\nto start "
                                           "the Marquardt\nbackprop algorithm.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 90, 500, 200), description_coords=(535, 90, 450, 300))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)

        self.make_plot(1, (20, 280, 480, 400))
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.path, = self.axes.plot([], linestyle='--', marker='*', label="Gradient Descent Path")
        self.x_data, self.y_data = [], []
        self.init_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.end_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.ani, self.event = None, None

        self.pair_of_params = 1
        self.pair_params = [["W1(1, 1)", "W2(1, 1)"], ["W1(1, 1)", "b1(1)"], ["b1(1)", "b1(2)"]]
        self.plot_data()

        self.x, self.y = None, None

        self.make_combobox(1, ["W1(1, 1), W2(1, 1)", 'W1(1, 1), b1(1)', 'b1(1), b1(2)'],
                           (525, 360, 175, 50), self.change_pair_of_params,
                           "label_combo", "Pair of parameters", (545, 340, 150, 50))

        self.mu = 0.01
        self.make_label("label_mu1", "0.01", (self.x_chapter_usual + 10, 590, self.w_chapter_slider, 50))
        self.make_label("label_mu2", "0.10", (self.x_chapter_usual + 150, 590, self.w_chapter_slider, 50))
        self.make_slider("slider_mu", QtCore.Qt.Orientation.Horizontal, (1, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 1,
                         (self.x_chapter_usual, 560, self.w_chapter_slider, 50), self.slide,
                         "label_mu", "Initial Mu: 0.01", (self.x_chapter_usual + 50, 530, self.w_chapter_slider, 50))

        self.nu = 5
        self.make_label("label_nu1", "1.0", (self.x_chapter_usual + 10, 500, self.w_chapter_slider, 50))
        self.make_label("label_nu2", "10.0", (self.x_chapter_usual + 150, 500, self.w_chapter_slider, 50))
        self.make_slider("slider_nu", QtCore.Qt.Orientation.Horizontal, (10, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 50,
                         (self.x_chapter_usual, 470, self.w_chapter_slider, 50), self.slide,
                         "label_nu", "Constant NU: 5.0", (self.x_chapter_usual + 50, 440, self.w_chapter_slider, 50))

        self.slider_mu.sliderPressed.connect(self.slider_disconnect)
        self.slider_mu.sliderReleased.connect(self.slider_reconnect)
        self.slider_nu.sliderPressed.connect(self.slider_disconnect)
        self.slider_nu.sliderReleased.connect(self.slider_reconnect)
        self.slider_mu.valueChanged.connect(self.slider_update)
        self.slider_nu.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.animation_speed = 100

        self.canvas.draw()

        self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
        self.mc = 0.8

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()

    def slider_update(self):
        self.ani_stop()
        self.mu = float(self.slider_mu.value() / 100)
        self.label_mu.setText("Initial Mu: " + str(round(self.mu, 2)))
        self.nu = float(self.slider_nu.value() / 10)
        self.label_nu.setText("Constant NU: " + str(self.nu))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.slide)

    def slider_reconnect(self):
        self.do_slide = True
        self.sender().valueChanged.connect(self.slide)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_slide = False

    def change_pair_of_params(self, idx):
        self.ani_stop()
        self.pair_of_params = idx + 1
        self.end_point_1.set_data([], [])
        self.init_point_1.set_data([], [])
        self.init_params()
        self.plot_data()

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
        self.canvas.draw()

    def slide(self):
        self.ani_stop()
        if not self.do_slide:
            return
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        if self.x_data:
            self.path.set_data([], [])
            self.x_data, self.y_data = [self.x_data[0]], [self.y_data[0]]
            self.init_point_1.set_data([self.x_data[0]], [self.y_data[0]])
            self.canvas.draw()
            self.run_animation(self.event)

    def animate_init(self):
        self.path.set_data(self.x_data, self.y_data)
        self.a1 = self.logsigmoid_stable(np.dot(self.W1, self.P) + self.b1)
        self.a2 = self.logsigmoid_stable(np.dot(self.W2, self.a1) + self.b2)
        self.e = self.T - self.a2
        self.error_prev = np.dot(self.e, self.e.T).item()
        self.ii = np.eye(2)
        self.end_point_1.set_data([], [])
        return self.path, self.end_point_1

    def on_animate(self, idx):

        self.mu /= self.nu
        # if abs(self.mu * 100) < 1000:
        #     self.slider_mu.setValue(self.mu * 100)
        # self.label_mu.setText("mu: " + str(round(self.mu, 2)))

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
        # grad = np.sqrt(np.dot(je.T, je)).item()
        # if grad < 0.000002:
        #     print("!")
        #     self.slider_do = True
        #     return self.path,

        jj = np.dot(jac.T, jac)
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

        self.a1 = self.logsigmoid_stable(np.dot(W1, self.P) + b1)
        self.a2 = self.logsigmoid_stable(np.dot(W2, self.a1) + b2)
        self.e = self.T - self.a2
        error = np.dot(self.e, self.e.T).item()

        while error >= self.error_prev:

            try:

                self.mu *= self.nu
                # if abs(self.mu * 100) < 1000:
                #     self.slider_mu.setValue(self.mu * 100)
                # self.label_mu.setText("mu: " + str(round(self.mu, 2)))
                if self.mu > 1e10:
                    break

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

                self.a1 = self.logsigmoid_stable(np.dot(W1, self.P) + b1)
                self.a2 = self.logsigmoid_stable(np.dot(W2, self.a1) + b2)
                self.e = self.T - self.a2
                error = np.dot(self.e, self.e.T).item()

            except Exception as e:
                if str(e) == "Singular matrix":
                    print("The matrix was singular... Increasing mu 10-fold")
                    self.mu *= self.nu
                else:
                    raise e

        if error < self.error_prev:
            self.W1, self.b1, self.W2, self.b2 = np.copy(W1), np.copy(b1), np.copy(W2), np.copy(b2)
            self.error_prev = error

        # if self.error_prev <= 0.0000001:
        #     print("!!")
        #     self.slider_do = True
        #     return self.path,

        self.x_data.append(self.x)
        self.y_data.append(self.y)

        self.y_data = [(y[0] if isinstance(y, np.ndarray) else y) for y in self.y_data]
        self.x_data = [(x[0] if isinstance(x, np.ndarray) else x) for x in self.x_data]

        self.path.set_data(self.x_data, self.y_data)

        if idx == 11:
            self.end_point_1.set_data([self.x_data[-1]], [self.y_data[-1]])

        return self.path, self.end_point_1

    def on_mouseclick(self, event):
        self.mu = float(self.slider_mu.value()) / 100
        self.init_params()
        self.event = event
        self.ani_stop()
        self.path.set_data([], [])
        self.x_data, self.y_data = [], []
        self.init_point_1.set_data([event.xdata], [event.ydata])
        self.canvas.draw()
        self.run_animation(event)

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data, self.y_data = [event.xdata], [event.ydata]
            self.x, self.y = event.xdata, event.ydata
            if self.pair_of_params == 1:
                self.W1[0, 0], self.W2[0, 0] = self.x, self.y
            elif self.pair_of_params == 2:
                self.W1[0, 0], self.b1[0] = self.x, self.y
            elif self.pair_of_params == 3:
                self.b1[0], self.b1[1] = self.x, self.y
            self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=12,
                                     interval=self.animation_speed, repeat=False, blit=True)

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])

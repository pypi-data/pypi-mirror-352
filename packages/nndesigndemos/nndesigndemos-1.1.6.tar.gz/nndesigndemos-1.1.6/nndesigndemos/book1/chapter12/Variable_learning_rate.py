from PyQt6 import QtWidgets, QtCore
import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class VariableLearningRate(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(VariableLearningRate, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Variable Learning Rate", 12, "\nUse the pop up menu below\nto select the network\nparameters"
                                                        " to train\nwith backpropagation.\n\nThe corresponding contour\nplot "
                                                        "is shown below.\n\nClick in the contour graph\nto start "
                                                        "the variable learning\nrate backprop algorithm.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 90, 500, 200), description_coords=(535, 90, 450, 300))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)
        self.lr, self.epochs = None, None

        self.make_plot(1, (20, 280, 480, 400))
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.path, = self.axes.plot([], linestyle='--', marker='*', label="Gradient Descent Path")
        self.init_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.end_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.x_data, self.y_data = [], []
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

        self.lr = 14
        self.make_label("label_lr1", "0.0", (self.x_chapter_usual + 10, 610, self.w_chapter_slider, 50))
        self.make_label("label_lr2", "20.0", (self.x_chapter_usual + 150, 610, self.w_chapter_slider, 50))
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 200), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 140,
                         (self.x_chapter_usual, 580, self.w_chapter_slider, 50), self.slide, "label_lr", "lr: 14.0")

        self.increase_rate = 1.05
        self.make_label("label_increase1", "1.00", (self.x_chapter_usual + 10, 460, self.w_chapter_slider, 50))
        self.make_label("label_increase2", "1.20", (self.x_chapter_usual + 150, 460, self.w_chapter_slider, 50))
        self.make_slider("slider_increase", QtCore.Qt.Orientation.Horizontal, (100, 120), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 105,
                         (self.x_chapter_usual, 430, self.w_chapter_slider, 50), self.slide, "label_increase", "Increase rate: 1.05",
                         (self.x_chapter_usual + 50, 400, self.w_chapter_slider, 50))

        self.decrease_rate = 0.7
        self.make_label("label_decrease1", "0.50", (self.x_chapter_usual + 10, 540, self.w_chapter_slider, 50))
        self.make_label("label_decrease2", "1.00", (self.x_chapter_usual + 150, 540, self.w_chapter_slider, 50))
        self.make_slider("slider_decrease", QtCore.Qt.Orientation.Horizontal, (50, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 70,
                         (self.x_chapter_usual, 510, self.w_chapter_slider, 50), self.slide, "label_decrease",
                         "Decrease rate: 0.70", (self.x_chapter_usual + 50, 480, self.w_chapter_slider, 50))

        self.animation_speed = 0

        self.canvas.draw()

        self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
        self.mc = 0.8
        self.slider_do = True

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()

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

        for collection in self.axes.collections:
            collection.remove()

        f_data = loadmat(PACKAGE_PATH + "Data/nndbp_new_{}.mat".format(self.pair_of_params))
        x1, y1 = np.meshgrid(f_data["x1"], f_data["y1"])
        self.axes.contour(x1, y1, f_data["E1"], list(f_data["levels"].reshape(-1)))
        if self.pair_of_params == 1:
            self.axes.scatter([self.W1[0, 0]], [self.W2[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-5, 15)
            self.axes.set_ylim(-5, 15)
            self.axes.set_xticks([-5, 0, 5, 10, 15])
            self.axes.set_yticks([-5, 0, 5, 10, 15])
        elif self.pair_of_params == 2:
            self.axes.scatter([self.W1[0, 0]], [self.b1[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 30)
            self.axes.set_ylim(-20, 10)
            self.axes.set_xticks([-10, 0, 10, 20, 30])
            self.axes.set_yticks([-20, -15, -10, -5, 0, 5, 10])
        elif self.pair_of_params == 3:
            self.axes.scatter([self.b1[0, 0]], [self.b1[1, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 10)
            self.axes.set_ylim(-10, 10)
            self.axes.set_xticks([-10, -5, 0, 5, 10])
            self.axes.set_xticks([-10, -5, 0, 5, 10])
        self.axes.set_xlabel(self.pair_params[self.pair_of_params - 1][0], fontsize=8)
        # self.axes.xaxis.set_label_coords(0.95, -0.025)
        self.axes.set_ylabel(self.pair_params[self.pair_of_params - 1][1], fontsize=8)
        # self.axes.yaxis.set_label_coords(-0.025, 0.95)
        self.canvas.draw()

    def slide(self):
        if self.slider_do:
            self.init_point_1.set_data([], [])
            self.lr = float(self.slider_lr.value()/10)
            self.label_lr.setText("lr: " + str(self.lr))
            self.increase_rate = float(self.slider_increase.value() / 100)
            self.label_increase.setText("Increase rate: " + str(self.increase_rate))
            self.decrease_rate = float(self.slider_decrease.value() / 100)
            self.label_decrease.setText("Decrease rate: " + str(self.decrease_rate))
            # self.animation_speed = int(self.slider_anim_speed.value()) * 100
            # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
            if self.x_data:
                self.ani_stop()
                self.path.set_data([], [])
                self.x_data, self.y_data = [self.x_data[0]], [self.y_data[0]]
                self.canvas.draw()
                # self.run_animation(self.event)

    def animate_init(self):
        self.path.set_data(self.x_data, self.y_data)
        self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
        self.mc = 0.8
        self.n1 = np.dot(self.W1, self.P) + self.b1
        self.a1 = self.logsigmoid(self.n1)
        self.n2 = np.dot(self.W2, self.a1) + self.b2
        self.a2 = self.logsigmoid(self.n2)
        self.e = self.T - self.a2
        self.D2 = self.a2 * (1 - self.a2) * self.e
        self.D1 = self.a1 * (1 - self.a1) * np.dot(self.W2.T, self.D2)
        self.end_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        return self.path, self.end_point_1

    def on_animate(self, idx):

        self.dW1 = self.mc * self.dW1 + (1 - self.mc) * np.dot(self.D1, self.P.T) * self.lr
        self.db1 = self.mc * self.db1 + (1 - self.mc) * np.dot(self.D1, np.ones((self.D1.shape[1], 1))) * self.lr
        self.dW2 = self.mc * self.dW2 + (1 - self.mc) * np.dot(self.D2, self.a1.T) * self.lr
        self.db2 = self.mc * self.db2 + (1 - self.mc) * np.dot(self.D2, np.ones((self.D2.shape[1], 1))) * self.lr
        self.mc = 0.8

        W1, b1, W2, b2 = np.copy(self.W1), np.copy(self.b1), np.copy(self.W2), np.copy(self.b2)
        if self.pair_of_params == 1:
            W1[0, 0] += self.dW1[0, 0]
            W2[0, 0] += self.dW2[0, 0]
            self.x, self.y = W1[0, 0], W2[0, 0]
        elif self.pair_of_params == 2:
            W1[0, 0] += self.dW1[0, 0]
            b1[0, 0] += self.db1[0, 0]
            self.x, self.y = W1[0, 0], b1[0, 0]
        elif self.pair_of_params == 3:
            b1[0, 0] += self.db1[0, 0]
            b1[1, 0] += self.db1[1, 0]
            self.x, self.y = b1[0, 0], b1[1, 0]

        n1_new = np.dot(W1, self.P) + b1
        a1_new = self.logsigmoid(n1_new)
        n2_new = np.dot(W2, a1_new) + b2
        a2_new = self.logsigmoid(n2_new)
        e_new = self.T - a2_new

        if np.sum(e_new * e_new) > np.sum(self.e * self.e) * 1.04:
            self.lr *= self.decrease_rate
            self.mc = 0
            self.slider_do = False
            self.slider_lr.setValue(round(self.lr * 10))
            self.label_lr.setText("lr: " + str(round(self.lr, 2)))
            self.x, self.y = self.x_data[-1], self.y_data[-1]
        else:
            if np.sum(e_new * e_new) < np.sum(self.e * self.e):
                self.lr *= self.increase_rate
                self.slider_do = False
                self.slider_lr.setValue(round(self.lr * 10))
                self.label_lr.setText("lr: " + str(round(self.lr, 2)))
            self.W1, self.b1, self.W2, self.b2 = np.copy(W1), np.copy(b1), np.copy(W2), np.copy(b2)
            self.a1, self.a2 = a1_new, a2_new
            self.e = e_new
            self.D2 = self.a2 * (1 - self.a2) * self.e
            self.D1 = self.a1 * (1 - self.a1) * np.dot(self.W2.T, self.D2)

        if idx == 99:
            self.end_point_1.set_data([self.x_data[-1]], [self.y_data[-1]])

        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.path.set_data(self.x_data, self.y_data)
        self.slider_do = True
        return self.path, self.end_point_1

    def on_mouseclick(self, event):
        self.init_params()
        self.event = event
        self.ani_stop()
        self.path.set_data([], [])
        self.x_data, self.y_data = [], []
        self.init_point_1.set_data([event.xdata], [event.ydata])
        self.end_point_1.set_data([], [])
        self.canvas.draw()
        self.run_animation(event)

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data, self.y_data = [event.xdata], [event.ydata]
            self.x, self.y = event.xdata, event.ydata
            if self.pair_of_params == 1:
                self.W1[0, 0], self.W2[0, 0] = self.x, self.y
            elif self.pair_of_params == 2:
                self.W1[0, 0], self.b1[0, 0] = self.x, self.y
            elif self.pair_of_params == 3:
                self.b1[0, 0], self.b1[1, 0] = self.x, self.y
            self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=100,
                                     interval=self.animation_speed, repeat=False, blit=True)

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])

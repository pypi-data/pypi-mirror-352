from PyQt6 import QtWidgets, QtCore
import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class Momentum(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Momentum, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Momentum", 12, "\nUse the pop up menu below\nto select the network\nparameters"
                                          " to train\nwith backpropagation.\n\nThe corresponding contour\nplot "
                                          "is shown below.\n\nClick in the contour graph\nto start "
                                          "the momentum\nbackprop algorithm.\n\nYou can reset the algorithm\nparameters "
                                          "by using\nthe sliders.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 90, 500, 200), description_coords=(535, 110, 450, 300))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)
        self.lr, self.epochs = None, None

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
                           (525, 410, 175, 50), self.change_pair_of_params,
                           "label_combo", "Pair of parameters", (545, 390, 150, 50))

        self.lr = 3.5
        self.make_label("label_lr1", "0.0", (self.x_chapter_usual + 10, 590, self.w_chapter_slider, 50))
        self.make_label("label_lr2", "20.0", (self.x_chapter_usual + 150, 590, self.w_chapter_slider, 50))
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 200), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 100,
                         (self.x_chapter_usual, 560, self.w_chapter_slider, 50), self.slide, "label_lr", "lr: 10.0")

        self.momentum = 0.9
        self.make_label("label_momentum1", "0.0", (self.x_chapter_usual + 10, 500, self.w_chapter_slider, 50))
        self.make_label("label_momentum2", "1.0", (self.x_chapter_usual + 150, 500, self.w_chapter_slider, 50))
        self.make_slider("slider_momentum", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 90,
                         (self.x_chapter_usual, 470, self.w_chapter_slider, 50), self.slide,
                         "label_momentum", "Momentum: 0.9", (self.x_chapter_usual + 50, 440, self.w_chapter_slider, 50))

        self.slider_lr.sliderPressed.connect(self.slider_disconnect)
        self.slider_lr.sliderReleased.connect(self.slider_reconnect)
        self.slider_momentum.sliderPressed.connect(self.slider_disconnect)
        self.slider_momentum.sliderReleased.connect(self.slider_reconnect)
        self.slider_lr.valueChanged.connect(self.slider_update)
        self.slider_momentum.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.animation_speed = 0

        self.canvas.draw()

        self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0

    def slider_update(self):
        self.ani_stop()
        self.lr = float(self.slider_lr.value() / 10)
        self.label_lr.setText("lr: " + str(self.lr))
        self.momentum = float(self.slider_momentum.value() / 100)
        self.label_momentum.setText("Momentum: " + str(self.momentum))

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
        self.end_point_1.set_data([], [])
        return self.path, self.end_point_1

    def on_animate(self, idx):

        n1 = np.dot(self.W1, self.P) + self.b1
        a1 = self.logsigmoid(n1)
        n2 = np.dot(self.W2, a1) + self.b2
        a2 = self.logsigmoid(n2)

        e = self.T - a2

        D2 = a2 * (1 - a2) * e
        D1 = a1 * (1 - a1) * np.dot(self.W2.T, D2)
        self.dW1 = self.momentum * self.dW1 + (1 - self.momentum) * np.dot(D1, self.P.T) * self.lr
        self.db1 = self.momentum * self.db1 + (1 - self.momentum) * np.dot(D1, np.ones((D1.shape[1], 1))) * self.lr
        self.dW2 = self.momentum * self.dW2 + (1 - self.momentum) * np.dot(D2, a1.T) * self.lr
        self.db2 = self.momentum * self.db2 + (1 - self.momentum) * np.dot(D2, np.ones((D2.shape[1], 1))) * self.lr

        if self.pair_of_params == 1:
            self.W1[0, 0] += self.dW1[0, 0]
            self.W2[0, 0] += self.dW2[0, 0]
            self.x, self.y = self.W1[0, 0], self.W2[0, 0]
        elif self.pair_of_params == 2:
            self.W1[0, 0] += self.dW1[0, 0]
            self.b1[0, 0] += self.db1[0, 0]
            self.x, self.y = self.W1[0, 0], self.b1[0, 0]
        elif self.pair_of_params == 3:
            self.b1[0, 0] += self.db1[0, 0]
            self.b1[1, 0] += self.db1[1, 0]
            self.x, self.y = self.b1[0, 0], self.b1[1, 0]

        if idx == self.epochs - 1:
            self.end_point_1.set_data([self.x_data[-1]], [self.y_data[-1]])

        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.path.set_data(self.x_data, self.y_data)
        return self.path, self.end_point_1

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
    def on_mouseclick(self, event):
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
                self.epochs = 300
            elif self.pair_of_params == 2:
                self.W1[0, 0], self.b1[0, 0] = self.x, self.y
                self.epochs = 300
            elif self.pair_of_params == 3:
                self.b1[0, 0], self.b1[1, 0] = self.x, self.y
                self.epochs = 60
            self.dW1, self.db1, self.dW2, self.db2 = 0, 0, 0, 0
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=self.epochs,
                                     interval=self.animation_speed, repeat=False, blit=True)

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])

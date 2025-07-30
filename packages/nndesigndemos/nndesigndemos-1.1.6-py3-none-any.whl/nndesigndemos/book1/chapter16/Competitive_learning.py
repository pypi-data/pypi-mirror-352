from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class CompetitiveLearning(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(CompetitiveLearning, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Competitive Learning", 16, "\n\n\nClick on the plot to\nadd new input vectors.\n\nClick on the weight\nvectors "
                                                      "and drag the\nmouse to move them.\n\nClick [Learn] to present\n"
                                                      "one input.\n\nClick [Train] to present\nall inputs.",
                          PACKAGE_PATH + "Logo/Logo_Ch_16.svg", None)

        self.alpha = 0.4

        self.make_plot(1, (15, 100, 500, 500))
        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        # self.axes_1.add_patch(plt.Circle((0, 0), 1.7, color='r'))
        self.axes_1.set_yticks([0])
        self.axes_1.set_xticks([0])
        self.axes_1.set_xlim(-1.2, 1.2)
        self.axes_1.set_ylim(-1.2, 1.2)
        self.axes_1.grid(True, linestyle='--')
        self.ani = None

        angles = np.array([[105, 110, 115, 120, -10, -5, 0, 5, -120, -115, -110, -105]]) * np.pi / 180
        self.p_x = list(np.cos(angles).reshape(-1))
        self.p_y = list(np.sin(angles).reshape(-1))
        self.p_points_1, = self.axes_1.plot([], ".", color="r")
        self.p_points_2, = self.axes_1.plot([], ".", color="g")
        self.p_points_3, = self.axes_1.plot([], ".", color="black")
        self.p_point_higlight, = self.axes_1.plot([], "*", color="blue", markersize=12)
        self.P = None

        self.W_1 = [np.sqrt(0.5), np.sqrt(0.5)]
        self.W_2 = [np.sqrt(0.5), -np.sqrt(0.5)]
        self.W_3 = [-1, 0]
        self.W = None
        self.axes1_points = []
        self.axes1_w1 = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, color="r")
        self.axes1_w2 = self.axes_1.quiver([0], [0], [0], [0],  units="xy", scale=1, color="g")
        self.axes1_w3 = self.axes_1.quiver([0], [0], [0], [0],  units="xy", scale=1, color="black")
        self.axes1_proj_line, = self.axes_1.plot([], "-")
        self.update_plot()
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.cid, self.w_change = None, None

        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 4,
                         (15, 610, 500, 50), self.slide, "label_lr", "Learning Rate: 0.4", (225, 585, 200, 50))
        self.alpha = float(self.slider_lr.value() / 10)

        self.make_button("run_button", "Learn", (self.x_chapter_button, 365, self.w_chapter_button, self.h_chapter_button), self.on_learn)
        self.make_button("run_button", "Train", (self.x_chapter_button, 395, self.w_chapter_button, self.h_chapter_button), self.on_run)
        self.make_button("run_button", "Random", (self.x_chapter_button, 425, self.w_chapter_button, self.h_chapter_button), self.init_weights)

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()

    def slide(self):
        self.ani_stop()
        self.alpha = float(self.slider_lr.value() / 10)
        self.label_lr.setText("Learning Rate: {}".format(self.alpha))
        self.update_plot()
        self.canvas.draw()
        # self.on_run()

    def init_weights(self):
        self.ani_stop()
        self.W_1 = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
        self.W_1 /= np.linalg.norm(self.W_1)
        self.W_2 = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
        self.W_2 /= np.linalg.norm(self.W_2)
        self.W_3 = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
        self.W_3 /= np.linalg.norm(self.W_3)
        self.update_plot()
        self.canvas.draw()

    def update_plot(self):
        self.axes1_w1.set_UVC(self.W_1[0], self.W_1[1])
        self.axes1_w2.set_UVC(self.W_2[0], self.W_2[1])
        self.axes1_w3.set_UVC(self.W_3[0], self.W_3[1])
        self.W = np.array([self.W_1, self.W_2, self.W_3])
        self.P = np.array([self.p_x, self.p_y])
        a = self.compet(np.dot(self.W, self.P), axis=0)
        x_1_data, y_1_data, x_2_data, y_2_data, x_3_data, y_3_data = [], [], [], [], [], []
        for i in range(a.shape[1]):
            if np.argmax(a[:, i]) == 0:
                x_1_data.append(self.p_x[i])
                y_1_data.append(self.p_y[i])
            elif np.argmax(a[:, i]) == 1:
                x_2_data.append(self.p_x[i])
                y_2_data.append(self.p_y[i])
            else:
                x_3_data.append(self.p_x[i])
                y_3_data.append(self.p_y[i])
        self.p_points_1.set_data(x_1_data[:], y_1_data[:])
        self.p_points_2.set_data(x_2_data[:], y_2_data[:])
        self.p_points_3.set_data(x_3_data[:], y_3_data[:])

    def animate_init_train(self):
        return self.axes1_w1, self.axes1_w2, self.axes1_w3, self.p_points_1, self.p_points_2, self.p_points_3, self.p_point_higlight, self.axes1_proj_line

    def on_animate_train(self, idx):
        if idx % 2 != 0:
            self.p_point_higlight.set_data([], [])
            self.axes1_proj_line.set_data([], [])
            self.update_plot()
        else:
            idx = int(idx / 2)
            p = self.P[:, idx]
            a = self.compet(np.dot(self.W, p[..., None]), axis=0)
            self.p_point_higlight.set_data([self.P[0, idx]], [self.P[1, idx]])
            if np.argmax(a) == 0:
                W_1 = self.W_1[:]
                self.W_1 = list((1 - self.alpha) * np.array(self.W_1) + self.alpha * p)
                self.axes1_proj_line.set_data([W_1[0], self.W_1[0]], [W_1[1], self.W_1[1]])
            elif np.argmax(a) == 1:
                W_2 = self.W_2[:]
                self.W_2 = list((1 - self.alpha) * np.array(self.W_2) + self.alpha * p)
                self.axes1_proj_line.set_data([W_2[0], self.W_2[0]], [W_2[1], self.W_2[1]])
            else:
                W_3 = self.W_3[:]
                self.W_3 = list((1 - self.alpha) * np.array(self.W_3) + self.alpha * p)
                self.axes1_proj_line.set_data([W_3[0], self.W_3[0]], [W_3[1], self.W_3[1]])
        return self.axes1_w1, self.axes1_w2, self.axes1_w3, self.p_points_1, self.p_points_2, self.p_points_3, self.p_point_higlight, self.axes1_proj_line

    def on_run(self):
        seed = np.random.randint(1, 1000)
        np.random.seed(seed)
        np.random.shuffle(self.p_x)
        np.random.seed(seed)
        np.random.shuffle(self.p_y)
        self.update_plot()
        self.ani_stop()
        self.ani = FuncAnimation(self.figure, self.on_animate_train, init_func=self.animate_init_train, frames=2 * self.P.shape[1],
                                 interval=500, repeat=False, blit=False)
        self.update_plot()
        self.canvas.draw()

    def on_learn(self):
        seed = np.random.randint(1, 1000)
        np.random.seed(seed)
        np.random.shuffle(self.p_x)
        np.random.seed(seed)
        np.random.shuffle(self.p_y)
        self.ani_stop()
        self.ani = FuncAnimation(self.figure, self.on_animate_train, init_func=self.animate_init_train, frames=2,
                                 interval=500, repeat=False, blit=False)
        self.update_plot()
        self.canvas.draw()

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:

            self.ani_stop()

            # https://stackoverflow.com/questions/39840030/distance-between-point-and-a-line-from-two-points/39840218
            d_w_1 = np.linalg.norm(np.cross(
                np.array([self.W_1[0], self.W_1[1]]) - np.array([0, 0]),
                np.array([0, 0]) - np.array([event.xdata, event.ydata])
            )) / np.linalg.norm(np.array([self.W_1[0], self.W_1[1]]) - np.array([0, 0]))
            d_w_2 = np.linalg.norm(np.cross(
                np.array([self.W_2[0], self.W_2[1]]) - np.array([0, 0]),
                np.array([0, 0]) - np.array([event.xdata, event.ydata])
            )) / np.linalg.norm(np.array([self.W_2[0], self.W_2[1]]) - np.array([0, 0]))
            d_w_3 = np.linalg.norm(np.cross(
                np.array([self.W_3[0], self.W_3[1]]) - np.array([0, 0]),
                np.array([0, 0]) - np.array([event.xdata, event.ydata])
            )) / np.linalg.norm(np.array([self.W_3[0], self.W_3[1]]) - np.array([0, 0]))
            min_d_idx, min_d = np.argmin([d_w_1, d_w_2, d_w_3]), np.min([d_w_1, d_w_2, d_w_3])

            if min_d < 0.03:
                self.w_change = min_d_idx + 1
                if self.w_change == 1:
                    self.axes1_w1.set_UVC(0, 0)
                elif self.w_change == 2:
                    self.axes1_w2.set_UVC(0, 0)
                elif self.w_change == 3:
                    self.axes1_w3.set_UVC(0, 0)
                self.canvas.draw()
                self.cid = self.canvas.mpl_connect("button_release_event", self.on_mousepressed)
            else:
                if self.cid:
                    self.canvas.mpl_disconnect(self.cid)
                self.cid = None
                self.p_x.append(event.xdata)
                self.p_y.append(event.ydata)
                self.update_plot()
                self.canvas.draw()

    def on_mousepressed(self, event):
        if self.w_change == 1:
            self.W_1 = [event.xdata, event.ydata]
        elif self.w_change == 2:
            self.W_2 = [event.xdata, event.ydata]
        elif self.w_change == 3:
            self.W_3 = [event.xdata, event.ydata]
        self.update_plot()
        self.canvas.draw()

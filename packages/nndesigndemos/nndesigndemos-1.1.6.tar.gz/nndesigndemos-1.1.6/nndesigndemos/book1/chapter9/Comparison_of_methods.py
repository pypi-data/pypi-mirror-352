import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ComparisonOfMethods(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ComparisonOfMethods, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Comparison of Methods", 9, "Click in either graph\nto start a search point.\n\nThen watch the two\n"
                                                      "algorithms attempt to\nfind the minima.\n\nThe two alrorithms are:\n\n"
                                                      " - Steepest Descent using\n   line search.\n\n"
                                                      " - Conjugate Gradient using\n   line search.",
                          PACKAGE_PATH + "Logo/Logo_Ch_9.svg", None, description_coords=(535, 140, 300, 250))

        x, y = np.linspace(-2, 2, 21), np.linspace(-2, 2, 21)
        X, Y = np.meshgrid(x, y)
        self.a, self.b, c = np.array([[2, 1], [1, 2]]), np.array([0, 0]), 0
        F = (self.a[0, 0] * X ** 2 + (self.a[0, 1] + self.a[1, 0]) * X * Y + self.a[1, 1] * Y ** 2) / 2 \
            + self.b[0] * X + self.b[1] * Y + c

        self.make_plot(1, (115, 100, 290, 290))
        self.make_plot(2, (115, 385, 290, 290))

        self.event, self.ani_1, self.ani_2 = None, None, None
        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Steepest Descent Path", fontdict={'fontsize': 10})
        self.axes_1.contour(X, Y, F, levels=[0.5, 1, 2, 4, 6, 8])
        self.axes_1.set_xlim(-2, 2)
        self.axes_1.set_ylim(-2, 2)
        self.axes_1.set_yticks([-2, -1, 0, 1, 2])
        self.path_1, = self.axes_1.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Gradient Descent Path")
        self.init_point_1, = self.axes_1.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.x_data_1, self.y_data_1 = [], []
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.canvas.draw()

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_title("Conjugate Gradient Path")
        self.axes_2.contour(X, Y, F, levels=[0.5, 1, 2, 4, 6, 8])
        self.axes_2.set_xlim(-2, 2)
        self.axes_2.set_ylim(-2, 2)
        self.axes_2.set_yticks([-2, -1, 0, 1, 2])
        self.path_2, = self.axes_2.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Conjugate Gradient Path")
        self.init_point_2, = self.axes_2.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.x_data_2, self.y_data_2 = [], []
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick)
        self.canvas2.draw()

        self.animation_speed = 500
        # self.make_slider("slider_anim_speed", QtCore.Qt.Orientation.Horizontal, (0, 6), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
        #                  (self.x_chapter_usual, 380, self.w_chapter_slider, 100), self.slide, "label_anim_speed", "Animation Delay: 200 ms")

    # def slide(self):
    #     self.animation_speed = int(self.slider_anim_speed.value()) * 100
    #     self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
    #     if self.x_data_1:
    #         if self.ani_1:
    #             self.ani_1.event_source.stop()
    #             self.ani_2.event_source.stop()
    #         self.path_1.set_data([], [])
    #         self.path_2.set_data([], [])
    #         self.x_data_1, self.y_data_1 = [self.x_data_1[0]], [self.y_data_1[0]]
    #         self.x_data_2, self.y_data_2 = [self.x_data_2[0]], [self.y_data_2[0]]
    #         self.canvas.draw()
    #         self.canvas2.draw()
    #         self.run_animation(self.event)

    def on_mouseclick(self, event):
        self.event = event
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()
        self.path_1.set_data([], [])
        self.path_2.set_data([], [])
        self.x_data_1, self.y_data_1 = [], []
        self.x_data_2, self.y_data_2 = [], []
        self.init_point_1.set_data([event.xdata], [event.ydata])
        self.init_point_2.set_data([event.xdata], [event.ydata])
        self.canvas.draw()
        self.canvas2.draw()
        self.run_animation(event)

    def animate_init_1(self):
        self.path_1, = self.axes_1.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Gradient Descent Path")
        return self.path_1,

    def animate_init_2(self):
        self.path_2, = self.axes_2.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Conjugate Gradient Path")
        return self.path_2,

    def on_animate_1(self, idx):
        gradient = np.dot(self.a, np.array([self.x_1, self.y_1])) + self.b.T
        p_g = -gradient
        hess = self.a
        lr = -np.dot(gradient, p_g.T) / np.dot(p_g.T, np.dot(hess, p_g))
        self.x_1 -= lr * gradient[0]
        self.y_1 -= lr * gradient[1]
        # lr = 0.07
        # gradient = np.dot(a, np.array([self.x_1, self.y_1])) + b.T
        # self.x_1 -= lr * gradient[0]
        # self.y_1 -= lr * gradient[1]
        self.x_data_1.append(self.x_1)
        self.y_data_1.append(self.y_1)
        self.path_1.set_data(self.x_data_1, self.y_data_1)
        return self.path_1,

    def on_animate_2(self, idx):
        if self.i == 0:
            self.gradient = np.dot(self.a, np.array([self.x_2, self.y_2])) + self.b.T
            self.p = -self.gradient
            self.i += 1
        elif self.i == 1:
            gradient_old = self.gradient
            self.gradient = np.dot(self.a, np.array([self.x_2, self.y_2])) + self.b.T
            beta = np.dot(self.gradient.T, self.gradient) / np.dot(gradient_old.T, gradient_old)
            self.p = -self.gradient + np.dot(beta, self.p)
        hess = self.a
        lr = -np.dot(self.gradient, self.p.T) / np.dot(self.p.T, np.dot(hess, self.p))
        self.x_2 += lr * self.p[0]
        self.y_2 += lr * self.p[1]
        self.x_data_2.append(self.x_2)
        self.y_data_2.append(self.y_2)
        self.path_2.set_data(self.x_data_2, self.y_data_2)
        return self.path_2,

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data_1, self.y_data_1 = [event.xdata], [event.ydata]
            self.x_data_2, self.y_data_2 = [event.xdata], [event.ydata]
            self.x_1, self.y_1 = event.xdata, event.ydata
            self.x_2, self.y_2 = event.xdata, event.ydata
            self.ani_1 = FuncAnimation(self.figure, self.on_animate_1, init_func=self.animate_init_1, frames=5,
                                       interval=self.animation_speed, repeat=False, blit=True)
            self.i = 0
            self.ani_2 = FuncAnimation(self.figure2, self.on_animate_2, init_func=self.animate_init_2, frames=2,
                                       interval=self.animation_speed, repeat=False, blit=True)

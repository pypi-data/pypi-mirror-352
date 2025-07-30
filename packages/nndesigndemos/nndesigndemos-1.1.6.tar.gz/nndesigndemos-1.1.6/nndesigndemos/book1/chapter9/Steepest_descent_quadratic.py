from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class SteepestDescentQuadratic(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(SteepestDescentQuadratic, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Steepest Descent for Quadratic", 9, "Click anywhere on the\ngraph to start an initial\nguess."
                                                               "Then the steepest\ndescent trajectory\nwill be shown.\n\n"
                                                               "Modify the learning rate\nby moving the slide bar.\n\n"
                                                               "Experiment with different\ninitial guesses and\nlearning rates.",
                          PACKAGE_PATH + "Logo/Logo_Ch_9.svg", None, description_coords=(535, 120, 300, 250))

        x, y = np.linspace(-4, 4, 41), np.linspace(-2, 2, 32)
        X, Y = np.meshgrid(x, y)
        self.a, self.b, c = np.array([[2, 0], [0, 50]]), np.array([0, 0]), 0
        self.max_epoch = 50
        F = (self.a[0, 0] * X ** 2 + (self.a[0, 1] + self.a[1, 0]) * X * Y + self.a[1, 1] * Y ** 2) / 2\
            + self.b[0] * X + self.b[1] * Y + c

        self.make_plot(1, (0, 230, 520, 260))
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.axes.contour(X, Y, F, levels=[0.1, 0.5, 3, 7, 13, 20, 35, 50, 80])
        self.axes.set_xlim(-4, 4)
        self.axes.set_ylim(-2, 2)
        self.path, = self.axes.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Gradient Descent Path")
        self.init_point, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.x_data, self.y_data = [], []
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.ani, self.event = None, None

        self.lr = 0.03
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 12), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 6,
                         (25, 600, 480, 50), self.slide, "label_lr", "lr: 0.03", (245, 570, 100, 50))
        self.make_label("label_lr1", "0.00", (35, 640, 100, 20))
        self.make_label("label_lr2", "0.06", (470, 640, 100, 20))
        self.slider_lr.sliderPressed.connect(self.slider_disconnect)
        self.slider_lr.sliderReleased.connect(self.slider_reconnect)
        self.slider_lr.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.animation_speed = 100
        # self.make_slider("slider_anim_speed", QtCore.Qt.Orientation.Horizontal, (0, 6), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
        #                  (self.x_chapter_usual, 380, self.w_chapter_slider, 100), self.slide, "label_anim_speed", "Animation Delay: 200 ms")

        self.canvas.draw()

    def slider_update(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.lr = float(self.slider_lr.value() / 200)
        self.label_lr.setText("lr: " + str(self.lr))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.slide)

    def slider_reconnect(self):
        self.do_slide = True
        self.sender().valueChanged.connect(self.slide)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_slide = False

    def slide(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        if not self.do_slide:
            return
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        if self.x_data:
            self.path.set_data([], [])
            self.x_data, self.y_data = [self.x_data[0]], [self.y_data[0]]
            self.init_point.set_data([self.x_data[0]], [self.y_data[0]])
            self.canvas.draw()
            self.run_animation(self.event)

    def animate_init(self):
        self.path, = self.axes.plot([], linestyle='--', marker="o", fillstyle="none", color="k", label="Gradient Descent Path")
        return self.path,

    def on_animate(self, idx):
        gradient = np.dot(self.a, np.array([self.x, self.y])) + self.b.T
        self.x -= self.lr * gradient[0]
        self.y -= self.lr * gradient[1]
        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.path.set_data(self.x_data, self.y_data)
        return self.path,

    def on_mouseclick(self, event):
        self.event = event
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        # self.ani = None
        self.path.set_data([], [])
        self.x_data, self.y_data = [], []
        self.init_point.set_data([event.xdata], [event.ydata])
        self.canvas.draw()
        self.run_animation(event)

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data, self.y_data = [event.xdata], [event.ydata]
            self.x, self.y = event.xdata, event.ydata
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=self.max_epoch,
                                     interval=self.animation_speed, repeat=False, blit=True)

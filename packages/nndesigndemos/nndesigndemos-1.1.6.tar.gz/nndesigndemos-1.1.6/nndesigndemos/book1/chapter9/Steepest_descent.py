from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class SteepestDescent(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(SteepestDescent, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Steepest Descent", 9, "Click anywhere on the\ngraph to start an initial\nguess."
                                                 "\nThen the steepest descent\ntrajectory will be shown.\n\n"
                                                 "Modify the learning rate\nby moving the slide bar.\n\n"
                                                 "Experiment with different\ninitial guesses and\nlearning rates.",
                          PACKAGE_PATH + "Logo/Logo_Ch_9.svg", None, description_coords=(535, 120, 300, 250))

        x = np.array([-2, -1.8, -1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0,
                      0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2])
        y = np.copy(x)
        self.X, self.Y = np.meshgrid(x, y)
        self.max_epoch = 50
        self.F = (self.Y - self.X) ** 4 + 8 * self.X * self.Y - self.X + self.Y + 3
        self.F[self.F < 0] = 0
        self.F[self.F > 12] = 12

        self.make_plot(1, (115, 100, 290, 290))
        self.make_plot(2, (115, 385, 290, 290))

        self.x_data, self.y_data = [], []
        self.ani_1, self.ani_2, self.event, self.x, self.y = None, None, None, None, None

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.contour(self.X, self.Y, self.F)
        self.axes_1.set_title("Function F", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-2, 2)
        self.axes_1.set_ylim(-2, 2)
        self.axes_1.set_yticks([-2, -1, 0, 1, 2])
        self.path_1, = self.axes_1.plot([], linestyle='--', marker="o", fillstyle="none", color="k",
                                        label="Gradient Descent Path")
        self.init_point_1, = self.axes_1.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_title("Approximation Fa", fontdict={'fontsize': 10})
        self.path_2, = self.axes_2.plot([], linestyle='--', marker="o", fillstyle="none", color="k",
                                        label="Gradient Descent Path")
        self.init_point_2, = self.axes_2.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.axes_2.set_xlim(-2, 2)
        self.axes_2.set_ylim(-2, 2)
        self.axes_2.set_yticks([-2, -1, 0, 1, 2])
        self.canvas2.draw()

        self.lr = 0.03
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 6,
                         (self.x_chapter_usual, 390, self.w_chapter_slider, 50), self.slide, "label_lr", "lr: 0.03")
        self.make_label("label_lr1", "0.00", (self.x_chapter_usual + 15, 430, 100, 20))
        self.make_label("label_lr2", "0.20", (self.x_chapter_usual + 145, 430, 100, 20))
        self.slider_lr.sliderPressed.connect(self.slider_disconnect)
        self.slider_lr.sliderReleased.connect(self.slider_reconnect)
        self.slider_lr.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.animation_speed = 100
        # self.make_slider("slider_anim_speed", QtCore.Qt.Orientation.Horizontal, (0, 6), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
        #                  (self.x_chapter_usual, 380, self.w_chapter_slider, 100), self.slide, "label_anim_speed", "Animation Delay: 200 ms")

    def ani_stop(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()

    def slider_update(self):
        self.ani_stop()
        self.lr = float(self.slider_lr.value() / 100)
        self.label_lr.setText("lr: " + str(self.lr))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.slide)

    def slider_reconnect(self):
        self.do_slide = True
        self.sender().valueChanged.connect(self.slide)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_slide = False

    def animate_init_1(self):
        self.path_1, = self.axes_1.plot([], linestyle='--', marker="o", fillstyle="none", color="k",
                                        label="Gradient Descent Path")
        return self.path_1,

    def animate_init_2(self):
        self.path_2, = self.axes_2.plot([], linestyle='--', marker="o", fillstyle="none", color="k",
                                        label="Gradient Descent Path")
        return self.path_2,

    def on_animate_1(self, idx):
        gx = -4 * (self.y - self.x) ** 3 + 8 * self.y - 1
        gy = 4 * (self.y - self.x) ** 3 + 8 * self.x + 1
        self.x -= self.lr * gx
        self.y -= self.lr * gy
        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.path_1.set_data(self.x_data, self.y_data)
        return self.path_1,

    def on_animate_2(self, idx):
        self.path_2.set_data(self.x_data[:2], self.y_data[:2])
        return self.path_2,

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:

            # Checks whether the clicked point is in the contour
            x_event, y_event = event.xdata, event.ydata
            if round(x_event, 1) * 10 % 2 == 1:
                x_event += 0.06
                if round(x_event, 1) * 10 % 2 == 1:
                    x_event = event.xdata - 0.06
            if round(y_event, 1) * 10 % 2 == 1:
                y_event += 0.06
                if round(y_event, 1) * 10 % 2 == 1:
                    y_event = event.ydata - 0.06
            x_event = round(x_event, 1)
            y_event = round(y_event, 1)
            if self.F[np.bitwise_and(self.X == x_event, self.Y == y_event)].item() == 12:
                return

            self.x, self.y = event.xdata, event.ydata
            # Removes contours from second plot
            while self.axes_2.collections:
                for collection in self.axes_2.collections:
                    collection.remove()
            # Draws new contour
            Fo = (self.y - self.x) ** 4 + 8 * self.x * self.y - self.x * self.y + 3
            gx = -4 * (self.y - self.x) ** 3 + 8 * self.y - 1
            gy = 4 * (self.y - self.x) ** 3 + 8 * self.x + 1
            gradient = np.array([[gx], [gy]])
            dX, dY = self.X - self.x, self.Y - self.y
            Fa = gradient[0, 0] * dX + gradient[1, 0] * dY + Fo
            self.axes_2.contour(self.X, self.Y, Fa)

            self.event = event
            self.ani_stop()
            self.path_1.set_data([], [])
            self.path_2.set_data([], [])
            self.x_data, self.y_data = [], []
            self.init_point_1.set_data([event.xdata], [event.ydata])
            self.init_point_2.set_data([event.xdata], [event.ydata])
            self.canvas.draw()
            self.canvas2.draw()
            self.run_animation(event)

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data, self.y_data = [self.x], [self.y]
            self.ani_1 = FuncAnimation(self.figure, self.on_animate_1, init_func=self.animate_init_1, frames=self.max_epoch,
                                       interval=self.animation_speed, repeat=False, blit=True)
            self.ani_2 = FuncAnimation(self.figure, self.on_animate_2, init_func=self.animate_init_2, frames=self.max_epoch,
                                       interval=self.animation_speed, repeat=False, blit=True)

    def slide(self):
        self.ani_stop()
        if not self.do_slide:
            return
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        if self.x_data:
            self.path_1.set_data([], [])
            self.path_2.set_data([], [])
            self.x, self.y = self.x_data[0], self.y_data[0]
            self.x_data, self.y_data = [self.x_data[0]], [self.y_data[0]]
            self.init_point_1.set_data([self.x_data[0]], [self.y_data[0]])
            self.init_point_2.set_data([self.x_data[0]], [self.y_data[0]])
            self.canvas.draw()
            self.canvas2.draw()
            self.run_animation(self.event)

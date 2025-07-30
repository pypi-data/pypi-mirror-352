from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class AdaptiveNoiseCancellation(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(AdaptiveNoiseCancellation, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Adaptive Noise Cancellation", 10, "\n\nClick on the bottom contour\nplot to change\nthe initial weights.\n\n"
                                                             "Use the sliders to alter\nthe learning rate\nand momentum.\n\n"
                                                             "You can choose to display\nthe original and estimated\nsignals"
                                                             " or their difference.",
                          PACKAGE_PATH + "Logo/Logo_Ch_10.svg", None)

        N, f, max_t = 3, 60, 0.5
        s = N * f
        self.ts = s * max_t + 1
        A, theta, k = 0.1, np.pi / 2, 0.2
        self.signal_ = k * (2 * np.random.uniform(0, 1, (1, int(self.ts))) - 1)
        i = np.arange(self.ts).reshape(1, -1)
        noise = 1.2 * np.sin(2 * np.pi * (i - 1) / N + theta)
        filtered_noise = A * 1.20 * np.sin(2 * np.pi * (i - 1) / N + theta)
        delayed_noise = np.array([list(noise.reshape(-1)), [0] + list(noise.reshape(-1))[:-1]])
        noisy_signal = self.signal_ + filtered_noise

        w = np.array([0, -2])
        self.time = np.arange(1, self.ts + 1) / self.ts * max_t

        self.P = delayed_noise
        self.T = noisy_signal[:]
        A = 2 * np.dot(self.P, self.P.T)
        d = -2 * np.dot(self.P, self.T.T)
        c = np.dot(self.T, self.T.T)

        x = np.linspace(-2.1, 2.1, 30)
        y = np.copy(x)
        X, Y = np.meshgrid(x, y)
        F = (A[0, 0] * X ** 2 + (A[0, 1] + A[1, 0]) * X * Y + A[1, 1] * Y ** 2) / 2 + d[0, 0] * X + d[1, 0] * Y + c

        self.x_data, self.y_data = [], []
        self.ani_1, self.ani_2, self.event, self.x, self.y = None, None, None, None, None
        # self.W = None

        self.make_plot(1, (20, 100, 480, 270))
        self.figure.subplots_adjust(left=0.115, bottom=0.2, right=0.95, top=0.9)
        self.make_plot(2, (110, 370, 300, 300))
        self.figure2.subplots_adjust(left=0.2, bottom=0.2, right=0.95, top=0.9)

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Original (blue) and Estimated (red) Signals", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(0, 0.5)
        self.axes_1.set_ylim(-2, 2)
        self.axes_1.set_ylabel("Amplitud")
        self.axes_1.set_xlabel("Time")
        self.axes_1.plot(np.linspace(0, 0.5, 100), [0] * 100, color="gray", linestyle="dashed", linewidth=0.5)
        self.signal, = self.axes_1.plot([], linestyle='--', label="Original Signal", color="blue")
        self.signal.set_data(self.time, self.signal_)
        self.signal_approx, = self.axes_1.plot([], linestyle='-', label="Approx Signal", color="red")
        self.signal_diff, = self.axes_1.plot([], linestyle='-', label="Signal Difference", color="red")
        self.canvas.draw()

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.contour(X, Y, F, levels=[1, 10, 25, 50, 100, 200, 400], colors="blue")
        self.axes_2.set_title("Adaptive Weights", fontdict={'fontsize': 10})
        self.path_2, = self.axes_2.plot([], linestyle='--', marker='*', label="Gradient Descent Path", color="red")
        self.w1_data, self.w2_data = [], []
        self.axes_2.set_xlim(-2, 2)
        self.axes_2.set_ylim(-2, 2)
        self.axes_2.set_yticks([-2, -1, 0, 1, 2])
        self.axes_2.set_xlabel("$W(1,1)$")
        self.axes_2.set_ylabel("$W(1,2)$")
        self.canvas2.draw()

        self.lr = 0.2
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 15), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
                         (self.x_chapter_slider_label - 70, 370, self.w_chapter_slider, 50), self.slide,
                         "label_lr", "lr: 0.2")
        self.slider_lr.sliderPressed.connect(self.slider_disconnect)
        self.slider_lr.sliderReleased.connect(self.slider_reconnect)
        self.slider_lr.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.mc = 0
        """self.mc = 0
        self.make_slider("slider_mc", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (self.x_chapter_slider_label - 70, 440, self.w_chapter_slider, 50), self.slide,
                         "label_mc", "mc: 0")"""

        self.make_combobox(1, ["Signals", "Difference"], (self.x_chapter_slider_label - 60, 420, self.w_chapter_button, 50),
                           self.change_plot_type)
        self.plot_idx = 0

        """self.animation_speed = 100
        self.label_anim_speed = QtWidgets.QLabel(self)
        self.label_anim_speed.setText("Animation Delay: 100 ms")
        self.label_anim_speed.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_anim_speed.setGeometry((self.x_chapter_slider_label - 40) * self.w_ratio, 350 * self.h_ratio,
                                          self.w_chapter_slider * self.w_ratio, 100 * self.h_ratio)
        self.slider_anim_speed = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_anim_speed.setRange(0, 6)
        self.slider_anim_speed.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.slider_anim_speed.setTickInterval(1)
        self.slider_anim_speed.setValue(1)
        self.wid_anim_speed = QtWidgets.QWidget(self)
        self.layout_anim_speed = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        self.wid_anim_speed.setGeometry(self.x_chapter_usual * self.w_ratio, 380 * self.h_ratio,
                                        self.w_chapter_slider * self.w_ratio, 100 * self.h_ratio)
        self.layout_anim_speed.addWidget(self.slider_anim_speed)
        self.wid_anim_speed.setLayout(self.layout_anim_speed)
        self.slider_anim_speed.valueChanged.connect(self.slide)"""

        self.w, self.e = None, None
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick)
        # self.slider_anim_speed.valueChanged.connect(self.slide)

        event = matplotlib.backend_bases.MouseEvent("dummy", self.canvas2, 0, -2)
        event.xdata, event.ydata = 0, -2
        self.on_mouseclick(event)

    def slider_update(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()
        self.lr = float(self.slider_lr.value() / 10)
        self.label_lr.setText("lr: " + str(self.lr))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.slide)

    def slider_reconnect(self):
        self.do_slide = True
        self.sender().valueChanged.connect(self.slide)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_slide = False

    def change_plot_type(self, idx):
        self.plot_idx = idx
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()
        self.path_2.set_data([], [])
        self.w1_data, self.w2_data = [self.w1_data[0]], [self.w2_data[0]]
        self.w = np.array([self.w1_data[0], self.w2_data[0]])
        if idx == 0:
            self.axes_1.set_title("Original (blue) and Estimated (red) Signals", fontdict={'fontsize': 10})
            self.signal.set_data(self.time, self.signal_)
            self.signal_diff.set_data([], [])
            self.canvas.draw()
            self.canvas2.draw()
            self.run_animation()
        elif idx == 1:
            self.axes_1.set_title("Difference between Original and Estimated Signals", fontdict={'fontsize': 10})
            self.signal.set_data([], [])
            self.signal_approx.set_data([], [])
            self.canvas.draw()
            self.canvas2.draw()
            self.run_animation_diff()
        self.canvas.draw()
        self.canvas2.draw()

    def slide(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()
        if not self.do_slide:
            return
        # self.mc = float(self.slider_mc.value() / 10)
        # self.label_mc.setText("mc: " + str(self.mc))
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        if self.w1_data:
            self.path_2.set_data([], [])
            self.signal_approx.set_data([], [])
            self.signal_diff.set_data([], [])
            self.w1_data, self.w2_data = [self.w1_data[0]], [self.w2_data[0]]
            self.w = np.array([self.w1_data[0], self.w2_data[0]])
            # e_temp = self.e[0]
            self.e = np.zeros((int(self.ts),))
            # self.e[0] = e_temp
            self.canvas.draw()
            self.canvas2.draw()
            if self.plot_idx == 0:
                self.run_animation()
            elif self.plot_idx == 1:
                self.run_animation_diff()

    def animate_init_1(self):
        self.signal_approx, = self.axes_1.plot([], linestyle='-', label="Approx Signal", color="red")
        return self.signal_approx,

    def animate_init_2(self):
        self.path_2, = self.axes_2.plot([], linestyle='--', marker='*', label="Gradient Descent Path", color="red")
        return self.path_2,

    def animate_init_3(self):
        self.signal_diff, = self.axes_1.plot([], linestyle='-', label="Signal Difference", color="red")
        return self.signal_diff,

    def on_animate_1(self, idx):
        self.signal_approx.set_data(self.time[:idx + 1], self.e[:idx + 1])
        return self.signal_approx,

    def on_animate_2(self, idx):
        a = np.dot(self.w, self.P[:, idx])
        self.e[idx] = self.T[0, idx] - a
        self.w = self.w + self.mc * self.w + (1 - self.mc) * self.lr * self.e[idx] * self.P[:, idx].T
        self.w1_data.append(self.w[0])
        self.w2_data.append(self.w[1])
        self.path_2.set_data(self.w1_data, self.w2_data)
        return self.path_2,

    def on_animate_3(self, idx):
        self.signal_diff.set_data(self.time[:idx + 1], (self.signal_ - self.e).reshape(-1)[:idx + 1])
        return self.signal_diff,

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            self.w = np.array([event.xdata, event.ydata])
            self.e = np.zeros((int(self.ts),))
            self.event = event
            if self.ani_1 and self.ani_1.event_source:
                self.ani_1.event_source.stop()
            if self.ani_2 and self.ani_2.event_source:
                self.ani_2.event_source.stop()
            self.signal_approx.set_data([], [])
            self.path_2.set_data([], [])
            self.w1_data, self.w2_data = [self.w[0]], [self.w[1]]
            self.canvas.draw()
            self.canvas2.draw()
            if self.plot_idx == 0:
                self.run_animation()
            elif self.plot_idx == 1:
                self.run_animation_diff()
            self.canvas.draw()
            self.canvas2.draw()

    def run_animation(self):
        self.ani_2 = FuncAnimation(self.figure2, self.on_animate_2, init_func=self.animate_init_2, frames=int(self.ts),
                                   interval=20, repeat=False, blit=True)
        self.ani_1 = FuncAnimation(self.figure, self.on_animate_1, init_func=self.animate_init_1, frames=int(self.ts),
                                   interval=20, repeat=False, blit=True)

    def run_animation_diff(self):
        self.ani_2 = FuncAnimation(self.figure2, self.on_animate_2, init_func=self.animate_init_2, frames=int(self.ts),
                                   interval=20, repeat=False, blit=True)
        self.ani_1 = FuncAnimation(self.figure, self.on_animate_3, init_func=self.animate_init_3, frames=int(self.ts),
                                   interval=20, repeat=False, blit=True)

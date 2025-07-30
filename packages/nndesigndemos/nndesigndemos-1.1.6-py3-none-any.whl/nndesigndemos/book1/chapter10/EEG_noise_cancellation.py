from PyQt6 import QtWidgets, QtCore
import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class EEGNoiseCancellation(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(EEGNoiseCancellation, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("EEG Noise Cancellation", 10, "\n\n\nAn EEG signal has been\ncontaminated with noise.\n\nAn adaptive"
                                                        " linear\nnetwork is used to\nremove the noise.\n\nUse the sliders"
                                                        " to set\nthe learning rate and the\nnumber of delays.\n\nYou can"
                                                        " choose to display\nthe original and estimated\nsignals or their"
                                                        " difference.",
                          PACKAGE_PATH + "Logo/Logo_Ch_10.svg", None, description_coords=(535, 100, 450, 300))

        N, f, max_t = 3.33, 60, 0.5
        s = N * f
        self.ts = s * max_t + 1
        A1, A2, theta1, theta2, k = 1, 0.75, np.pi / 2, np.pi / 2.5, 0.00001
        self.signal_ = k * loadmat(PACKAGE_PATH + "Data/eegdata.mat")["eegdata"][:, :int(self.ts) + 1]
        i = np.arange(self.ts).reshape(1, -1)
        noise1, noise2 = 1.2 * np.sin(2 * np.pi * (i - 1) / N), 0.6 * np.sin(4 * np.pi * (i - 1) / N)
        noise = noise1 + noise2
        filtered_noise1 = A1 * 1.20 * np.sin(2 * np.pi * (i - 1) / N + theta1)
        filtered_noise2 = A2 * 0.6 * np.sin(4 * np.pi * (i - 1) / N + theta1)
        filtered_noise = filtered_noise1 + filtered_noise2
        noisy_signal = self.signal_ + filtered_noise

        self.time = np.arange(1, self.ts + 1) / self.ts * max_t

        self.P_ = np.zeros((21, 101))
        for i in range(21):
            self.P_[i, i + 1:] = noise[:, :101 - i - 1]
        self.P_ = np.array(self.P_)
        self.T = noisy_signal[:]

        self.x_data, self.y_data = [], []
        self.ani, self.x, self.y = None, None, None
        self.R, self.P = None, None
        self.a, self.e = None, None

        self.make_plot(1, (20, 100, 480, 270))
        self.figure.subplots_adjust(left=0.115, bottom=0.2, right=0.95, top=0.9)

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Original (blue) and Estimated (red) Signals", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(0, 0.5)
        self.axes_1.set_ylim(-2, 2)
        self.signal, = self.axes_1.plot([], linestyle='--', label="Original Signal", color="blue")
        self.signal.set_data(self.time, self.signal_)
        self.signal_approx, = self.axes_1.plot([], linestyle='-', label="Approx Signal", color="red")
        self.axes_1.plot(np.linspace(0, 0.5, 100), [0] * 100, color="gray", linestyle="dashed", linewidth=0.5)
        self.signal_diff, = self.axes_1.plot([], linestyle='-', label="Signal Difference", color="red")
        self.axes_1.set_ylabel("Amplitud")
        self.axes_1.set_xlabel("Time")
        self.canvas.draw()

        self.lr = 0.02
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
                         (25, 410, 480, 50), self.slide, "label_lr", "lr: 0.02", (245, 380, 100, 50))

        self.delays = 10
        self.make_slider("slider_delays", QtCore.Qt.Orientation.Horizontal, (0, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (25, 500, 480, 50), self.slide, "label_delays", "Delays: 10", (235, 470, 100, 50))

        self.slider_lr.sliderPressed.connect(self.slider_disconnect)
        self.slider_lr.sliderReleased.connect(self.slider_reconnect)
        self.slider_lr.valueChanged.connect(self.slider_update)
        self.slider_delays.sliderPressed.connect(self.slider_disconnect)
        self.slider_delays.sliderReleased.connect(self.slider_reconnect)
        self.slider_delays.valueChanged.connect(self.slider_update)
        self.do_slide = False

        self.animation_speed = 20
        """self.label_anim_speed = QtWidgets.QLabel(self)
        self.label_anim_speed.setText("Animation Delay: 100 ms")
        self.label_anim_speed.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_anim_speed.setGeometry((self.x_chapter_slider_label - 40) * self.w_ratio, 450 * self.h_ratio,
                                          self.w_chapter_slider * self.w_ratio, 100 * self.h_ratio)
        self.slider_anim_speed = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_anim_speed.setRange(0, 6)
        self.slider_anim_speed.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.slider_anim_speed.setTickInterval(1)
        self.slider_anim_speed.setValue(1)
        self.wid_anim_speed = QtWidgets.QWidget(self)
        self.layout_anim_speed = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        self.wid_anim_speed.setGeometry(self.x_chapter_usual * self.w_ratio, 480 * self.h_ratio,
                                        self.w_chapter_slider * self.w_ratio, 100 * self.h_ratio)
        self.layout_anim_speed.addWidget(self.slider_anim_speed)
        self.wid_anim_speed.setLayout(self.layout_anim_speed)"""

        self.w, self.e = None, None

        self.make_combobox(1, ["Signals", "Difference"], (190, 570, self.w_chapter_button, 50), self.change_plot_type)
        self.plot_idx = 0

        # self.make_button("run", "Run", (300, 580, self.w_chapter_button, 25), self.on_run)
        self.on_run()

    def slider_update(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.lr = float(self.slider_lr.value() / 100)
        self.label_lr.setText("lr: " + str(self.lr))
        self.delays = int(self.slider_delays.value())
        self.label_delays.setText("Delays: " + str(self.delays))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.slide)

    def slider_reconnect(self):
        self.do_slide = True
        self.sender().valueChanged.connect(self.slide)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_slide = False

    def change_plot_type(self, idx):
        self.plot_idx = idx
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        if idx == 0:
            self.axes_1.set_title("Original (blue) and Estimated (red) Signals", fontdict={'fontsize': 10})
            self.signal.set_data(self.time, self.signal_)
            self.signal_diff.set_data([], [])
            self.canvas.draw()
            self.run_animation()
        elif idx == 1:
            self.axes_1.set_title("Difference between Original and Estimated Signals", fontdict={'fontsize': 10})
            self.signal.set_data([], [])
            self.signal_approx.set_data([], [])
            self.canvas.draw()
            self.run_animation_diff()
        self.canvas.draw()

    def on_run(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.run_animation()

    def slide(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        if not self.do_slide:
            return
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        if self.plot_idx == 0:
            self.signal.set_data(self.time, self.signal_)
            self.signal_diff.set_data([], [])
            self.canvas.draw()
            self.run_animation()
        elif self.plot_idx == 1:
            self.signal.set_data([], [])
            self.signal_approx.set_data([], [])
            self.canvas.draw()
            self.run_animation_diff()
        self.canvas.draw()

    def animate_init(self):
        self.R = self.delays + 1
        self.P = self.P_[:self.R]
        self.w = np.zeros((1, self.R))
        self.a, self.e = np.zeros((1, 101)), np.zeros((1, 101))
        self.signal_approx, = self.axes_1.plot([], linestyle='-', label="Approx Signal", color="red")
        return self.signal_approx,

    def on_animate(self, idx):
        p = self.P[:, idx]
        self.a[0, idx] = np.dot(self.w, p)
        self.e[0, idx] = self.T[0, idx] - self.a[0, idx]
        self.w += self.lr * self.e[0, idx] * p.T
        self.signal_approx.set_data(self.time[:idx + 1], self.e[0, :idx + 1])
        return self.signal_approx,

    def animate_init_diff(self):
        self.R = self.delays + 1
        self.P = self.P_[:self.R]
        self.w = np.zeros((1, self.R))
        self.a, self.e = np.zeros((1, 101)), np.zeros((1, 101))
        self.signal_diff, = self.axes_1.plot([], linestyle='-', label="Signal Difference", color="red")
        return self.signal_diff,

    def on_animate_diff(self, idx):
        p = self.P[:, idx]
        self.a[0, idx] = np.dot(self.w, p)
        self.e[0, idx] = self.T[0, idx] - self.a[0, idx]
        self.w += self.lr * self.e[0, idx] * p.T
        self.signal_diff.set_data(self.time[:idx + 1], (self.signal_ - self.e)[0, :idx + 1])
        return self.signal_diff,

    def run_animation(self):
        self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=int(self.ts),
                                 interval=self.animation_speed, repeat=False, blit=True)

    def run_animation_diff(self):
        self.ani = FuncAnimation(self.figure, self.on_animate_diff, init_func=self.animate_init_diff, frames=int(self.ts),
                                 interval=self.animation_speed, repeat=False, blit=True)

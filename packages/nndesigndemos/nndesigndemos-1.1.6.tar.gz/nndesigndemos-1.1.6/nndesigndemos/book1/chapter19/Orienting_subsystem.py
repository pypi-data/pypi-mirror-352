from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class OrientingSubsystem(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(OrientingSubsystem, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Orienting Subsystem", 19, "Adjust the inputs\nand constants.\nThen click [Update] to\n"
                                                     "see the system respond.\n\nClick [Clear] to\nremove old responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_19.svg", None, description_coords=(535, 90, 450, 250))

        self.t = np.arange(0, 0.201, 0.001)

        self.make_plot(1, (20, 90, 480, 460))
        self.figure.subplots_adjust(left=0.175, right=0.95, bottom=0.125, top=0.9)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 0.201)
        self.axis.set_ylim(-1, 1)
        self.axis.plot(np.linspace(0, 0.201, 10), [0] * 10, color="black", linestyle="--", linewidth=0.5)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Reset a0")
        self.axis.set_title("Response")
        self.axis.set_xticks([0, 0.05, 0.1, 0.15, 0.2])
        self.lines = []

        self.make_slider("slider_input_pos", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1,
                         (self.x_chapter_usual, 330, self.w_chapter_slider, 50), self.slide,
                         "label_input_pos", "Input p(1): 1", (self.x_chapter_usual + 60, 330 - 25, 150, 50))
        self.make_slider("slider_input_neg", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1,
                         (self.x_chapter_usual, 390, self.w_chapter_slider, 50), self.slide,
                         "label_input_neg", "Input p(2): 1", (self.x_chapter_usual + 60, 390 - 25, 150, 50))
        self.make_slider("slider_bias_pos", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1,
                         (self.x_chapter_usual, 450, self.w_chapter_slider, 50), self.slide,
                         "label_bias_pos", "Input a1(1): 1", (self.x_chapter_usual + 50, 450 - 25, 150, 50))
        self.make_slider("slider_bias_neg", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 510, self.w_chapter_slider, 50), self.slide,
                         "label_bias_neg", "Input a1(2): 0", (self.x_chapter_usual + 50, 510 - 25, 150, 50))

        self.make_slider("slider_tcte", QtCore.Qt.Orientation.Horizontal, (1, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 30,
                         (20, 560, 480, 50), self.slide, "label_tcte", "+W0 Elements: 3.00", (200, 535, 170, 50))
        self.make_slider("slider_tcte1", QtCore.Qt.Orientation.Horizontal, (1, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 40,
                         (20, 630, 480, 50), self.slide, "label_tcte1", "-W0 Elements: 4.00", (200, 605, 170, 50))

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 575, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Update", (self.x_chapter_button, 605, self.w_chapter_button, self.h_chapter_button), self.graph)

        self.graph()

    def slide(self):
        self.pp = self.slider_input_pos.value()
        self.pn = self.slider_input_neg.value()
        self.label_input_pos.setText("Input p(1): " + str(self.pp))
        self.label_input_neg.setText("Input p(2): " + str(self.pn))
        self.bp = self.slider_bias_pos.value()
        self.bn = self.slider_bias_neg.value()
        self.label_bias_pos.setText("Input a1(1): " + str(round(self.bp, 2)))
        self.label_bias_neg.setText("Input a1(2): " + str(round(self.bn, 2)))
        self.A = self.slider_tcte.value() / 10
        self.B = self.slider_tcte1.value() / 10
        self.label_tcte.setText("+W0 Elements: " + str(round(self.A, 2)))
        self.label_tcte1.setText("-W0 Elements: " + str(round(self.B, 2)))

    def shunt(self, t, y):
        return (-y + (1 - y) * self.A * (self.p[0, 0] + self.p[1, 0]) - (y + 1) * self.B * (self.a[0, 0] + self.a[1, 0])) / 0.1

    def graph(self):
        self.pp = self.slider_input_pos.value()
        self.pn = self.slider_input_neg.value()
        self.bp = self.slider_bias_pos.value()
        self.bn = self.slider_bias_neg.value()
        self.A = self.slider_tcte.value() / 10
        self.B = self.slider_tcte1.value() / 10
        self.label_input_pos.setText("Input p(1): " + str(self.pp))
        self.label_input_neg.setText("Input p(2): " + str(self.pn))
        self.label_bias_pos.setText("Input a1(1): " + str(self.bp))
        self.label_bias_neg.setText("Input a1(2): " + str(self.bn))
        self.label_tcte.setText("+W0 Elements: " + str(round(self.A, 2)))
        self.label_tcte1.setText("-W0 Elements: " + str(round(self.B, 2)))
        self.p = np.array([[self.pp], [self.pn]])
        self.a = np.array([[self.bp], [self.bn]])
        r = ode(self.shunt).set_integrator("zvode")
        r.set_initial_value(np.array([0, 0]), 0)
        t1 = 0.201
        dt = 0.001
        out = []
        while r.successful() and r.t < t1:
            out.append(r.integrate(r.t + dt)[0].item())
        out[0] = 0
        while len(self.lines) > 3:
            self.lines.pop(0).remove()
        for line in self.lines:
            line.set_color("gray")
            line.set_alpha(0.5)
        self.lines.append(self.axis.plot(self.t, out, color="red")[0])
        self.canvas.draw()

    def on_clear(self):
        while len(self.lines) > 1:
            self.lines.pop(0).remove()
        self.canvas.draw()

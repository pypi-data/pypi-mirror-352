from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ART1Layer1(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ART1Layer1, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("ART1 Layer 1", 19, "Adjust the inputs,\nbiases and weights.\nThen click [Update] to\n"
                                              "see the layer respond.\n\nn1(1) is red,\nn1(2) is green.\n\n"
                                              "Click [Clear] to\nremove old responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_19.svg", None)

        self.t = np.arange(0, 0.2, 0.001)

        self.bp, self.bn, self.e = 1, 0, 0.1

        self.make_plot(1, (10, 90, 500, 450))
        self.figure.subplots_adjust(left=0.15, right=0.95, bottom=0.125, top=0.9)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 0.2)
        self.axis.set_ylim(-0.5, 0.5)
        self.axis.plot([0] * 10, np.linspace(-0.5, 0.5, 10), color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Net inputs n1(1), n1(2)")
        self.axis.set_title("Response")
        self.axis.set_xticks([0, 0.05, 0.1, 0.15, 0.2])
        self.axis.plot(np.linspace(0, 0.2, 100), [0] * 100, linestyle="dashed", linewidth=0.5, color="gray")
        self.lines1, self.lines2 = [], []

        self.make_slider("slider_input_pos", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 335, self.w_chapter_slider, 50), self.slide,
                         "label_input_pos", "Input p(1): 0", (self.x_chapter_usual + 60, 335 - 25, 150, 50))
        self.make_slider("slider_input_neg", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1,
                         (self.x_chapter_usual, 395, self.w_chapter_slider, 50), self.slide,
                         "label_input_neg", "Input p(2): 1", (self.x_chapter_usual + 60, 395 - 25, 150, 50))
        self.make_slider("slider_bias_pos", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 460, self.w_chapter_slider, 50), self.slide,
                         "label_bias_pos", "Bias b+: 1.00", (self.x_chapter_usual + 70, 460 - 25, 150, 50))
        self.make_slider("slider_bias_neg", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 15,
                         (self.x_chapter_usual, 520, self.w_chapter_slider, 50), self.slide,
                         "label_bias_neg", "Bias b-: 1.50", (self.x_chapter_usual + 70, 520 - 25, 150, 50))

        # self.paint_latex_string("latex_W21", "$W2:1 =$", 16, (30, 510, 250, 200))
        # self.paint_latex_string("latex_W22", "$[$", 45, (215, 510, 250, 200))
        # self.paint_latex_string("latex_W23", "$]$", 45, (335, 510, 250, 200))
        self.make_label("label_a", "W2:1 =", (145, 503, 200, 200), font_size=25)
        # self.make_label("label_a1", "[   ]", (226, 494, 500, 200), font_size=100)
        self.label_a.setStyleSheet("color:black")
        # self.label_a1.setStyleSheet("color:black")
        self.make_input_box("w_11", "1", (239, 530, 60, 100))
        self.make_input_box("w_12", "1", (295, 530, 60, 100))
        self.make_input_box("w_21", "0", (239, 580, 60, 100))
        self.make_input_box("w_22", "1", (295, 580, 60, 100))

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 575, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Update", (self.x_chapter_button, 605, self.w_chapter_button, self.h_chapter_button), self.graph)

        self.graph()

    def paintEvent(self, event):
        super(ART1Layer1, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        self.paint_bracket(painter, 238, 558, 650, 118)
        painter.end()

    def layer1(self, t, y):
        return [(-y[0] + (self.bp - y[0]) * (self.p[0, 0] + self.W2[0, 1]) - (y[0] + self.bn)) / 0.1,
                (-y[1] + (self.bp - y[1]) * (self.p[1, 0] + self.W2[1, 1]) - (y[1] + self.bn)) / 0.1]

    def slide(self):
        self.pp = self.slider_input_pos.value()
        self.pn = self.slider_input_neg.value()
        self.label_input_pos.setText("Input p(1): " + str(self.pp))
        self.label_input_neg.setText("Input p(2): " + str(self.pn))
        self.bp = self.slider_bias_pos.value() / 10
        self.bn = self.slider_bias_neg.value() / 10
        self.label_bias_pos.setText("Bias b+: " + str(round(self.bp, 2)))
        self.label_bias_neg.setText("Bias b-: " + str(round(self.bn, 2)))

    def graph(self):
        self.pp = self.slider_input_pos.value()
        self.pn = self.slider_input_neg.value()
        self.label_input_pos.setText("Input p(1): " + str(self.pp))
        self.label_input_neg.setText("Input p(2): " + str(self.pn))
        self.bp = self.slider_bias_pos.value() / 10
        self.bn = self.slider_bias_neg.value() / 10
        self.label_bias_pos.setText("Bias b+: " + str(round(self.bp, 2)))
        self.label_bias_neg.setText("Bias b-: " + str(round(self.bn, 2)))
        w11, w12 = float(self.w_11.text()), float(self.w_12.text())
        w21, w22 = float(self.w_21.text()), float(self.w_22.text())
        for idx, param in enumerate([w11, w12, w21, w22]):
            if param not in [0, 1]:
                if idx == 0:
                    w11 = 0
                    self.w_11.setText("0")
                elif idx == 1:
                    w12 = 0
                    self.w_12.setText("0")
                elif idx == 2:
                    w21 = 0
                    self.w_21.setText("0")
                else:
                    w22 = 0
                    self.w_22.setText("0")
        self.W2 = np.array([[w11, w12], [w21, w22]])
        self.p = np.array([[self.pp], [self.pn]])
        r1 = ode(self.layer1).set_integrator("vode")
        r1.set_initial_value(np.array([0, 0]), 0)
        t1 = 0.2
        dt = 0.001
        out_1, out_2 = [], []
        while r1.successful() and r1.t < t1:
            out = r1.integrate(r1.t + dt)
            out_1.append(out[0].item())
            out_2.append(out[1].item())
        out_1[0], out_2[0] = 0, 0
        while len(self.lines1) > 1:
            self.lines1.pop(0).remove()
        while len(self.lines2) > 1:
            self.lines2.pop(0).remove()
        for line in self.lines1:
            # line.set_color("gray")
            line.set_alpha(0.2)
        for line in self.lines2:
            # line.set_color("gray")
            line.set_alpha(0.2)
        self.lines1.append(self.axis.plot(self.t, out_1, color="red")[0])
        self.lines2.append(self.axis.plot(self.t, out_2, color="green")[0])
        self.canvas.draw()

    def on_clear(self):
        while len(self.lines1) > 1:
            self.lines1.pop(0).remove()
        while len(self.lines2) > 1:
            self.lines2.pop(0).remove()
        self.canvas.draw()

from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ART1Layer2(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ART1Layer2, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("ART1 Layer 2", 19, "Adjust the inputs,\nbiases and gain.\nThen click [Update] to\n"
                                              "see the layer respond.\n\nn2(1) is red,\nn2(2) is green.\n\n"
                                              "Click [Clear] to\nremove old responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_19.svg", None)

        self.t = np.arange(0, 0.21, 0.001)

        self.make_plot(1, (20, 90, 480, 480))
        self.figure.subplots_adjust(left=0.175, right=0.95, bottom=0.125, top=0.9)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 0.2)
        self.axis.set_ylim(-1, 1)
        self.axis.plot([0] * 20, np.linspace(-1, 1, 20), color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Outputs n2(1), n2(2)")
        self.axis.set_title("Response")
        self.axis.set_xticks([0, 0.05, 0.1, 0.15, 0.2])
        self.axis.plot(np.linspace(0, 0.2, 100), [0] * 100, linestyle="dashed", linewidth=0.5, color="gray")
        self.lines1, self.lines2 = [], []

        self.make_slider("slider_input_pos", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 330, self.w_chapter_slider, 50), self.slide,
                         "label_input_pos", "Input a(1): 0", (self.x_chapter_usual + 60, 330 - 25, 150, 50))
        self.make_slider("slider_input_neg", QtCore.Qt.Orientation.Horizontal, (0, 1), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1,
                         (self.x_chapter_usual, 390, self.w_chapter_slider, 50), self.slide,
                         "label_input_neg", "Input a(2): 1", (self.x_chapter_usual + 60, 390 - 25, 150, 50))
        self.make_slider("slider_bias_pos", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 450, self.w_chapter_slider, 50), self.slide,
                         "label_bias_pos", "Bias b+: 1.00", (self.x_chapter_usual + 70, 450 - 25, 150, 50))
        self.make_slider("slider_bias_neg", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 510, self.w_chapter_slider, 50), self.slide,
                         "label_bias_neg", "Bias b-: 1.00", (self.x_chapter_usual + 70, 510 - 25, 150, 50))
        self.make_slider("slider_tcte", QtCore.Qt.Orientation.Horizontal, (1, 200), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 100,
                         (20, 600, 480, 50), self.slide, "label_tcte", "Time Constant: 10.00", (200, 575, 170, 50))

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 575, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Update", (self.x_chapter_button, 605, self.w_chapter_button, self.h_chapter_button), self.graph)

        self.do_graph = True

        self.graph()

    def slide(self):
        self.pp = self.slider_input_pos.value()
        self.pn = self.slider_input_neg.value()
        self.label_input_pos.setText("Input a(1): " + str(self.pp))
        self.label_input_neg.setText("Input a(2): " + str(self.pn))
        self.bp = self.slider_bias_pos.value() / 10
        self.bn = self.slider_bias_neg.value() / 10
        self.label_bias_pos.setText("Bias b+: " + str(round(self.bp, 2)))
        self.label_bias_neg.setText("Bias b-: " + str(round(self.bn, 2)))
        self.e = self.slider_tcte.value() / 10
        self.label_tcte.setText("Transfer Function Gain: " + str(round(self.e, 2)))

    def layer1(self, t, y):
        i1 = np.dot(np.array([[0.5, 0.5]]), self.p).item()
        i2 = np.dot(np.array([[1, 0]]), self.p).item()
        a1, a2 = 0, 0
        if y[0] > 0:
            a1 = (self.e * y[0] ** 2)
        if y[1] > 0:
            a2 = (self.e * y[1] ** 2)
        return [(-y[0] + (self.bp - y[0]) * (a1 + i1) - (y[0] + self.bn) * a2) / 0.1,
                (-y[1] + (self.bp - y[1]) * (a2 + i2) - (y[1] + self.bn) * a1) / 0.1]

    def graph(self):
        if self.do_graph:
            self.pp = self.slider_input_pos.value()
            self.pn = self.slider_input_neg.value()
            self.bp = self.slider_bias_pos.value() / 10
            self.bn = self.slider_bias_neg.value() / 10
            self.e = self.slider_tcte.value() / 10
            self.label_input_pos.setText("Input a1(1): " + str(self.pp))
            self.label_input_neg.setText("Input a1(2): " + str(self.pn))
            self.label_bias_pos.setText("Bias b+: " + str(round(self.bp, 2)))
            self.label_bias_neg.setText("Bias b-: " + str(round(self.bn, 2)))
            self.label_tcte.setText("Transfer Function Gain: " + str(round(self.e, 2)))
            self.p = np.array([[self.pp], [self.pn]])
            r = ode(self.layer1).set_integrator("zvode")
            r.set_initial_value([0, 0], 0)
            t1 = 0.21
            dt = 0.001
            out_1, out_2 = [], []
            while r.successful() and r.t < t1:
                out = r.integrate(r.t + dt)
                out_1.append(out[0].item())
                out_2.append(out[1].item())
            out_1[0], out_2[0] = 0, 0
            while len(self.lines1) > 1:
                self.lines1.pop(0).remove()
            while len(self.lines2) > 1:
                self.lines2.pop(0).remove()
            for line in self.lines1:
                # line.set_color("gray")
                line.set_alpha(0.5)
            for line in self.lines2:
                # line.set_color("gray")
                line.set_alpha(0.5)
            self.lines1.append(self.axis.plot(self.t, out_1, color="red")[0])
            self.lines2.append(self.axis.plot(self.t, out_2, color="green")[0])
            self.canvas.draw()

    def on_clear(self):
        while len(self.lines1) > 1:
            self.lines1.pop(0).remove()
        while len(self.lines2) > 1:
            self.lines2.pop(0).remove()
        self.canvas.draw()

    def on_random(self):
        self.do_graph = False
        self.slider_input_pos.setValue(np.random.uniform(0, 1) * 100)
        self.slider_input_neg.setValue(np.random.uniform(0, 1) * 100)
        self.slider_bias_pos.setValue(np.random.uniform(0, 1) * 50)
        self.slider_bias_neg.setValue(np.random.uniform(0, 1) * 50)
        self.do_graph = True
        self.slider_tcte.setValue(np.random.uniform(0, 1) * 50)

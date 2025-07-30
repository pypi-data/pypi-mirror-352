from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class GrossbergLayer1(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(GrossbergLayer1, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Grossberg Layer 1", 18, "Use the slide bars\nto adjust the inputs, biases\nand the time constant (eps).\n\n"
                                                   "Output n1(1) is red,\noutput n1(2) is green.\n\nClick [Clear] to remove\nold responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_18.svg", None)

        self.t = np.arange(0, 5.01, 0.01)

        self.make_plot(1, (20, 90, 480, 480))
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 5)
        self.axis.set_ylim(-5, 5)
        self.axis.plot([0] * 20, np.linspace(-5, 5, 20), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot(np.linspace(0, 5, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Net inputs n(1), n(2)")
        self.axis.set_title("Response")
        self.lines1, self.lines2 = [], []

        self.make_slider("slider_input_pos", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 320, self.w_chapter_slider, 50), self.graph,
                         "label_input_pos", "Input p(1): 1.00", (self.x_chapter_usual + 60, 320 - 25, 150, 50))
        self.slider_input_pos.sliderPressed.connect(self.slider_disconnect)
        self.slider_input_pos.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_input_neg", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 380, self.w_chapter_slider, 50), self.graph,
                         "label_input_neg", "Input p(2): 0.00", (self.x_chapter_usual + 60, 380 - 25, 150, 50))
        self.slider_input_neg.sliderPressed.connect(self.slider_disconnect)
        self.slider_input_neg.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_bias_pos", QtCore.Qt.Orientation.Horizontal, (0, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 440, self.w_chapter_slider, 50), self.graph,
                         "label_bias_pos", "Bias b+: 1.00", (self.x_chapter_usual + 70, 440 - 25, 150, 50))
        self.slider_bias_pos.sliderPressed.connect(self.slider_disconnect)
        self.slider_bias_pos.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_bias_neg", QtCore.Qt.Orientation.Horizontal, (0, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 500, self.w_chapter_slider, 50), self.graph,
                         "label_bias_neg", "Bias b-: 0.00", (self.x_chapter_usual + 70, 500 - 25, 150, 50))
        self.slider_bias_neg.sliderPressed.connect(self.slider_disconnect)
        self.slider_bias_neg.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_tcte", QtCore.Qt.Orientation.Horizontal, (1, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (20, 600, 480, 50), self.graph, "label_tcte", "Time Constant: 1.00", (210, 575, 150, 50))
        self.slider_tcte.sliderPressed.connect(self.slider_disconnect)
        self.slider_tcte.sliderReleased.connect(self.slider_reconnect)

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 560, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Random", (self.x_chapter_button, 590, self.w_chapter_button, self.h_chapter_button), self.on_random)

        self.do_graph = True

        self.graph()

    def layer1(self, t, y):
        return [(-y[0] + (self.bp - y[0]) * self.pp - (y[0] + self.bn) * self.pn) / self.e,
                (-y[1] + (self.bp - y[1]) * self.pn - (y[1] + self.bn) * self.pp) / self.e]

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect()

    def slider_reconnect(self):
        self.sender().valueChanged.connect(self.graph)
        self.sender().valueChanged.emit(self.sender().value())

    def graph(self):
        if self.do_graph:
            self.pp = self.slider_input_pos.value() / 10
            self.pn = self.slider_input_neg.value() / 10
            self.bp = self.slider_bias_pos.value() / 10
            self.bn = self.slider_bias_neg.value() / 10
            self.e = self.slider_tcte.value() / 10
            self.label_input_pos.setText("Input p(1): " + str(round(self.pp, 2)))
            self.label_input_neg.setText("Input p(2): " + str(round(self.pn, 2)))
            self.label_bias_pos.setText("Bias b+: " + str(round(self.bp, 2)))
            self.label_bias_neg.setText("Bias b- " + str(round(self.bn, 2)))
            self.label_tcte.setText("Time Constant: " + str(round(self.e, 2)))
            r = ode(self.layer1).set_integrator("zvode")
            r.set_initial_value([0, 0], 0)
            t1 = 5
            dt = 0.01
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
        self.slider_input_pos.setValue(round(np.random.uniform(0, 1) * 100))
        self.slider_input_neg.setValue(round(np.random.uniform(0, 1) * 100))
        self.slider_bias_pos.setValue(round(np.random.uniform(0, 1) * 50))
        self.slider_bias_neg.setValue(round(np.random.uniform(0, 1) * 50))
        self.do_graph = True
        self.slider_tcte.setValue(round(np.random.uniform(0, 1) * 50))

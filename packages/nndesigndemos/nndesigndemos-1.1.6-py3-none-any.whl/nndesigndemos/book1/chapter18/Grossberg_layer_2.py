from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class GrossbergLayer2(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(GrossbergLayer2, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Grossberg Layer 2", 18, "Use the slide bars\nto adjust the inputs, biases\nand the time constant (eps).\n\n"
                                                   "Output n2(1) is red,\noutput n2(2) is green.\n\nClick [Clear] to remove\nold responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_18.svg", None)

        self.t = np.arange(0, 0.51, 0.01)

        self.make_plot(1, (25, 90, 450, 450))

        self.bp, self.bn, self.e = 1, 0, 0.1

        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 0.51)
        self.axis.set_ylim(0, 1)
        self.axis.plot([0] * 10, np.linspace(0, 1, 10), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot([0.25] * 10, np.linspace(0, 1, 10), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot(np.linspace(0, 0.5, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Net inputs n2(1), n2(2)")
        self.axis.set_title("Response")
        self.lines1, self.lines2 = [], []

        self.make_slider("slider_input_pos", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (self.x_chapter_usual, 330, self.w_chapter_slider, 50), self.graph,
                         "label_input_pos", "Input p(1): 1.00", (self.x_chapter_usual + 60, 330 - 25, 150, 50))
        self.slider_input_pos.sliderPressed.connect(self.slider_disconnect)
        self.slider_input_pos.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_input_neg", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 0,
                         (self.x_chapter_usual, 390, self.w_chapter_slider, 50), self.graph,
                         "label_input_neg", "Input p(2): 0.00", (self.x_chapter_usual + 60, 390 - 25, 150, 50))
        self.slider_input_neg.sliderPressed.connect(self.slider_disconnect)
        self.slider_input_neg.sliderReleased.connect(self.slider_reconnect)

        # self.paint_latex_string("latex_W21", "$W =$", 16, (80, 510, 500, 200))
        # self.paint_latex_string("latex_W22", "$[$", 45, (170, 510, 500, 200))
        # self.paint_latex_string("latex_W23", "$]$", 45, (320, 510, 500, 200))
        self.make_label("label_a", "W =", (140, 503, 500, 200), font_size=25)
        # self.make_label("label_a1", "[   ]", (190, 494, 500, 200), font_size=100)
        self.label_a.setStyleSheet("color:black")
        # self.label_a1.setStyleSheet("color:black")
        self.make_input_box("w_11", "0.9", (202, 530, 60, 100))
        self.make_input_box("w_12", "0.45", (260, 530, 60, 100))
        self.make_input_box("w_21", "0.45", (202, 580, 60, 100))
        self.make_input_box("w_22", "0.9", (260, 580, 60, 100))

        self.comboBox1_functions = [self.f2, self.purelin, self.f3, self.f4]
        self.comboBox1_functions_str = ['(10n^2)/(1 + n^2)', "purelin", '10n^2', '1 - exp(-n)']
        self.make_combobox(1, self.comboBox1_functions_str, (self.x_chapter_usual, 460, self.w_chapter_slider, 50),
                           self.change_transfer_function, "combobox1_label", "Transfer function", (self.x_chapter_usual + 20, 460 - 20, 100, 50))
        self.func1 = self.f2

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 560, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Random", (self.x_chapter_button, 590, self.w_chapter_button, self.h_chapter_button), self.on_random)
        self.make_button("run_button", "Update", (self.x_chapter_button, 530, self.w_chapter_button, self.h_chapter_button), self.graph)

        self.do_graph = True

        self.graph()

    def paintEvent(self, event):
        super(GrossbergLayer2, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        self.paint_bracket(painter, 203, 560, 650, 115)
        painter.end()

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect()

    def slider_reconnect(self):
        self.sender().valueChanged.connect(self.graph)
        self.sender().valueChanged.emit(self.sender().value())

    @staticmethod
    def f2(n):
        return 10 * n ** 2 / (1 + n ** 2)

    @staticmethod
    def f3(n):
        return 10 * n ** 2

    @staticmethod
    def f4(n):
        return 1 - np.exp(-n)

    def change_transfer_function(self, idx):
        self.func1 = self.comboBox1_functions[idx]
        self.graph()

    def layer2(self, t, y):
        i1 = np.dot(self.W2[0, :], self.p).item()
        i2 = np.dot(self.W2[1, :], self.p).item()
        y = np.array([[y[0]], [y[1]]])
        a = self.func1(y)
        y_out = np.zeros(y.shape)
        y_out[0, 0] = (-y[0, 0] + (self.bp - y[0, 0]) * (a[0, 0] + i1) - (y[0, 0] + self.bn) * a[1, 0]) / self.e
        y_out[1, 0] = (-y[1, 0] + (self.bp - y[1, 0]) * (a[1, 0] + i2) - (y[1, 0] + self.bn) * a[0, 0]) / self.e
        return y_out

    def graph(self):
        if self.do_graph:
            self.pp = self.slider_input_pos.value() / 10
            self.pn = self.slider_input_neg.value() / 10
            self.label_input_pos.setText("Input a1(1): " + str(round(self.pp, 2)))
            self.label_input_neg.setText("Input a1(2): " + str(round(self.pn, 2)))
            w11, w12 = float(self.w_11.text()), float(self.w_12.text())
            w21, w22 = float(self.w_21.text()), float(self.w_22.text())
            self.W2 = np.array([[w11, w12], [w21, w22]])
            self.p = np.array([[self.pp], [self.pn]])
            r1 = ode(self.layer2).set_integrator("zvode")
            r1.set_initial_value(np.array([[0], [0]]), 0)
            t1 = 0.26
            dt = 0.01
            out_11, out_21 = [], []
            while r1.successful() and r1.t < t1:
                out = r1.integrate(r1.t + dt)
                out_11.append(out[0, 0].item())
                out_21.append(out[1, 0].item())
            self.p = np.array([[0], [0]])
            r2 = ode(self.layer2).set_integrator("zvode")
            r2.set_initial_value(np.array([[out_11[-1]], [out_21[-1]]]), 0.26)
            t2 = 0.51
            out_12, out_22 = [], []
            while r2.successful() and r2.t < t2:
                out = r2.integrate(r2.t + dt)
                out_12.append(out[0, 0].item())
                out_22.append(out[1, 0].item())
            out_1, out_2 = out_11 + out_12, out_21 + out_22
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

    def on_random(self):
        self.do_graph = False
        self.slider_input_pos.setValue(round(np.random.uniform(0, 1) * 100))
        self.do_graph = True
        self.slider_input_neg.setValue(round(np.random.uniform(0, 1) * 100))

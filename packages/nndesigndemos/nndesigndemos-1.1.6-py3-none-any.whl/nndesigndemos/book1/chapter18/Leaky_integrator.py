from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class LeakyIntegrator(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LeakyIntegrator, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Leaky Integrator", 18, "\nUse the slide bars\nto adjust the input and\nthe time constant (eps)\n"
                                                  "to the leaky integrator.\n\nClick [Clear] to remove\nold responses.\n\n"
                                                  "Click [Random] for\nrandom patterns.",
                          PACKAGE_PATH + "Logo/Logo_Ch_18.svg", None)

        self.t = np.arange(0, 5.1, 0.1)

        self.make_plot(1, (20, 90, 480, 480))
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 5)
        self.axis.set_ylim(0, 10)
        self.axis.plot([0] * 30, np.linspace(0, 30, 30), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot(np.linspace(0, 10, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Output n")
        self.axis.set_title("Response")
        self.lines = []

        self.make_slider("slider_input", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (20, 575, 480, 50), self.graph, "label_input", "Input p: 1.00", (230, 550, 150, 50))
        self.slider_input.sliderPressed.connect(self.slider_disconnect)
        self.slider_input.sliderReleased.connect(self.slider_reconnect)
        self.make_slider("slider_tcte", QtCore.Qt.Orientation.Horizontal, (1, 50), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 10,
                         (20, 635, 480, 50), self.graph, "label_tcte", "Time Constant: 1.00", (210, 610, 150, 50))
        self.slider_tcte.sliderPressed.connect(self.slider_disconnect)
        self.slider_tcte.sliderReleased.connect(self.slider_reconnect)

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 330, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Random", (self.x_chapter_button, 360, self.w_chapter_button, self.h_chapter_button), self.on_random)

        self.do_graph = True

        self.graph()

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect()

    def slider_reconnect(self):
        self.sender().valueChanged.connect(self.graph)
        self.sender().valueChanged.emit(self.sender().value())

    def graph(self):
        if self.do_graph:
            p = self.slider_input.value() / 10
            tcte = self.slider_tcte.value() / 10
            self.label_input.setText("Input p: " + str(round(p, 2)))
            self.label_tcte.setText("Time Constant: " + str(round(tcte, 2)))
            y = p * (1 - np.exp(-self.t / tcte))
            while len(self.lines) > 3:
                self.lines.pop(0).remove()
            for line in self.lines:
                line.set_color("gray")
                line.set_alpha(0.5)
            self.lines.append(self.axis.plot(self.t, y, color="red")[0])
            self.canvas.draw()

    def on_clear(self):
        while len(self.lines) > 1:
            self.lines.pop(0).remove()
        self.canvas.draw()

    def on_random(self):
        self.do_graph = False
        self.slider_input.setValue(round(np.random.uniform(0, 1) * 100))
        self.do_graph = True
        self.slider_tcte.setValue(round(np.random.uniform(0, 1) * 50))

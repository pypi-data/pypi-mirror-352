from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class OneInputNeuron(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(OneInputNeuron, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("One-Input Neuron", 2, "Alter the weight, bias and\ninput by dragging the\ntriangular"
                                                 " shaped indicators.<p>Pick the transfer function\nwith the f menu."
                                                 "<p>Watch the change to the\nneuron function and its\noutput.",
                          PACKAGE_PATH + "Chapters/2/Logo_Ch_2.svg", PACKAGE_PATH + "Chapters/2/nn2d1.svg")

        self.make_plot(1)

        self.make_label("label_eq", "a = purelin(w * p + b)", (self.x_chapter_slider_label - 40, 340, 150, 100))

        self.make_slider("slider_w", QtCore.Qt.Orientation.Horizontal, (-30, 30), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (self.x_chapter_usual, 430, self.w_chapter_slider, 50), self.graph, "label_w", "w: 1.0")
        self.make_slider("slider_b", QtCore.Qt.Orientation.Horizontal, (-30, 30), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (self.x_chapter_usual, 500, self.w_chapter_slider, 50), self.graph, "label_b", "b: 0.0")

        self.comboBox1_functions_str = ["purelin", "poslin", 'hardlim', 'hardlims', 'satlin', 'satlins', 'logsig', 'tansig']
        self.make_combobox(1, self.comboBox1_functions_str, (self.x_chapter_usual, 580, self.w_chapter_slider, 50),
                           self.change_transfer_function, "label_f", "f", label_italics=True)
        self.comboBox1_functions = [self.purelin, self.poslin, self.hardlim, self.hardlims, self.satlin, self.satlins, self.logsig, self.tansig]
        self.func1 = self.purelin

        self.graph()

    def graph(self):

        a = self.figure.add_subplot(1, 1, 1)
        a.clear()  # Clear the plot
        a.set_xlim(-2, 2)
        a.set_ylim(-2, 2)
        # a.set_xticks([0], minor=True)
        # a.set_yticks([0], minor=True)
        # a.set_xticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.set_yticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.grid(which="minor")
        a.set_xticks([-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5])
        a.set_yticks([-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5])
        a.plot([0] * 10, np.linspace(-2, 2, 10), color="black", linestyle="--", linewidth=0.2)
        a.plot(np.linspace(-2, 2, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        a.set_xlabel("$p$")
        a.xaxis.set_label_coords(1, -0.025)
        a.set_ylabel("$a$")
        a.yaxis.set_label_coords(-0.025, 1)

        weight = self.slider_w.value() / 10
        bias = self.slider_b.value() / 10
        self.label_w.setText("w: " + str(weight))
        self.label_b.setText("b: " + str(bias))
        p = np.arange(-4, 4, 0.1)
        func = np.vectorize(self.func1)
        out = func(np.dot(weight, p) + bias)

        a.plot(p, out, markersize=3, color="red")
        # Setting limits so that the point moves instead of the plot.
        # a.set_xlim(-4, 4)
        # a.set_ylim(-2, 2)
        # add grid and axes
        # a.grid(True, which='both')
        # a.axhline(y=0, color='k')
        # a.axvline(x=0, color='k')
        self.canvas.draw()

    def change_transfer_function(self, idx):
        self.func1 = self.comboBox1_functions[idx]
        self.label_eq.setText("a = {}(w * p + b)".format(self.comboBox1_functions_str[idx]))
        self.graph()

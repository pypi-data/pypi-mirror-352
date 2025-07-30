from PyQt6 import QtWidgets, QtGui, QtCore
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout

from nndesigndemos.get_package_path import PACKAGE_PATH


class TwoInputNeuron(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(TwoInputNeuron, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Two input neuron", 2, "\n\nAlter the input values by\nmoving the sliders."
                                                 "\n\nAlter the weight and bias\nin the same way."
                                                 " Use the\nmenu to pick a transfer\nfunction.\n\nThe net input and"
                                                 " the\noutput will respond to\neach change.",
                          PACKAGE_PATH + "Chapters/2/Logo_Ch_2.svg")

        self.comboBox1_functions_str = ["purelin", "poslin", 'hardlim', 'hardlims', 'satlin', 'satlins', 'logsig',
                                        'tansig']
        self.make_combobox(1, self.comboBox1_functions_str, (300, 150, self.w_chapter_slider, 50),
                           self.change_transfer_function, "label_f", "f", label_italics=True)
        self.comboBox1_functions = [self.purelin, self.poslin, self.hardlim, self.hardlims, self.satlin, self.satlins,
                                    self.logsig, self.tansig]
        self.func = self.purelin

        self.make_slider("slider_p1", QtCore.Qt.Orientation.Vertical, (-10, 10), QtWidgets.QSlider.TickPosition.TicksLeft, 1, 0,
                         (30, 220, 50, 100), self.slide, "label_p1", "p1",
                         (25, 220, 30, 100))
        self.make_slider("slider_w1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksLeft, 1, 10,
                         (90, 150, 150, 50), self.slide, "label_w1", "w1")
        self.make_label("label_w1_", "w1", (120, 230, 30, 100))
        self.make_slider("slider_p2", QtCore.Qt.Orientation.Vertical, (-10, 10), QtWidgets.QSlider.TickPosition.TicksLeft, 1, 0,
                         (30, 335, 50, 100), self.slide, "label_p2", "p2",
                         (25, 335, 30, 100))
        self.make_slider("slider_w2", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksLeft, 1, 10,
                         (90, 500, 150, 50), self.slide, "label_w2", "w2")
        self.make_label("label_w2_", "w2", (120, 335, 30, 100))
        self.make_slider("slider_b", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksLeft, 1, 0,
                         (240, 500, 150, 50), self.slide, "label_b", "b")
        self.make_label("label_b_", "b", (200, 320, 30, 100))
        self.make_slider("slider_n", QtCore.Qt.Orientation.Vertical, (-60, 60), QtWidgets.QSlider.TickPosition.NoTicks, 1, 0,
                         (261, 280, 150, 100), None, "label_n", "n: 0.0",
                         (271, 230, 50, 100))
        self.make_slider("slider_a", QtCore.Qt.Orientation.Vertical, (-60, 60), QtWidgets.QSlider.TickPosition.NoTicks, 1, 0,
                         (470, 230, 150, 200), None, "label_a", "a: 0.0",
                         (470, 125, 50, 200))

        self.icon3 = QtWidgets.QLabel(self)
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nn2d2.svg").pixmap(400 * self.w_ratio, 300 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon3.setGeometry(75 * self.w_ratio, 200 * self.h_ratio, 400 * self.w_ratio, 300 * self.h_ratio)

    def slide(self):
        p_1 = float(self.slider_p1.value() / 10)
        w_1 = float(self.slider_w1.value() / 10)
        p_2 = float(self.slider_p2.value() / 10)
        w_2 = float(self.slider_w2.value() / 10)
        b = float(self.slider_b.value() / 10)
        n = w_1 * p_1 + w_2 * p_2 + b
        self.slider_n.setValue(round(n * 10))
        self.label_n.setText("n: {}".format(round(n, 2)))
        a = self.func(n)
        self.slider_a.setValue(round(a * 10))
        self.label_a.setText("a: {}".format(round(a, 2)))

    def change_transfer_function(self, idx):
        self.func = self.comboBox1_functions[idx]
        self.slide()

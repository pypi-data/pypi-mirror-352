from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.signal import lfilter

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class DynamicDerivatives(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(DynamicDerivatives, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Dynamic Derivatives", 14, "\n\nOriginal responses - black\ndots.\n"
                                                     "Incremental responses - blue\ncrosses.\n"
                                                     "Total derivatives - blue\ndiamonds.\nStatic derivatives"
                                                     " - black\nsquares.\n\nSelect the input and"
                                                     "\nfrequency to the IIR\nnetwork.\n\nUse the sliders to alter\n"
                                                     "the network weights.",  # \n\n"
                                             # "Click on [Random] to set\neach parameter to\a random value.\n\n"
                                             # "Click on [Reset] to\ninitialize the parameters",
                          PACKAGE_PATH + "Logo/Logo_Ch_14.svg", PACKAGE_PATH + "Figures/nnd14_2.svg",
                          icon_move_left=70, icon_coords=(130, 100, 500, 200), description_coords=(535, 100, 450, 300),
                          icon_rescale=True)

        self.make_plot(1, (15, 300, 250, 200))
        self.figure.subplots_adjust(left=0.15, bottom=0.2)
        self.make_plot(2, (250, 300, 250, 200))
        self.figure2.subplots_adjust(left=0.15, bottom=0.2)
        self.make_plot(3, (15, 480, 250, 200))
        self.figure3.subplots_adjust(left=0.15, bottom=0.2)
        self.make_plot(4, (250, 480, 250, 200))
        self.figure4.subplots_adjust(left=0.15, bottom=0.2)

        self.comboBox1_functions_str = ["square", 'sine']
        self.make_combobox(1, self.comboBox1_functions_str, (self.x_chapter_usual, 520, self.w_chapter_slider, 100),
                           self.change_transfer_function,
                           "label_f", "f", (self.x_chapter_slider_label + 20, 500, 150, 100))
        self.func1 = "square"

        self.comboBox2_divs = ["1/16", '1/14', '1/12', '1/10', '1/8']
        self.make_combobox(2, self.comboBox2_divs, (self.x_chapter_usual, 600, self.w_chapter_slider, 50),
                           self.change_freq,
                           "label_div", "frequency", (self.x_chapter_slider_label, 580, 150, 50))
        self.freq = 1 / 12

        self.make_slider("slider_w0", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
                         (self.x_chapter_usual, 420, self.w_chapter_slider, 50), self.graph, "label_w0", "iW(0): 0.5")

        self.make_slider("slider_w1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, -5,
                         (self.x_chapter_usual, 490, self.w_chapter_slider, 50), self.graph, "label_w1", "lW(1): -0.5")

        self.comboBox2.setCurrentIndex(2)

    def graph(self):

        self.figure.clf()
        self.figure2.clf()
        self.figure3.clf()
        self.figure4.clf()

        a = self.figure.add_subplot(1, 1, 1)
        a4 = self.figure2.add_subplot(1, 1, 1)
        a2 = self.figure3.add_subplot(1, 1, 1)
        a3 = self.figure4.add_subplot(1, 1, 1)

        a.set_xlim(0, 25)
        a2.set_xlim(0, 25)
        a3.set_xlim(0, 25)
        a4.set_xlim(0, 25)
        a4.set_title("Incremental Response iw + 0.1", fontsize=10)
        a.set_title("Incremental Response lw + 0.1", fontsize=10)
        a3.set_title("Derivative with respect to lw", fontsize=10)
        a2.set_title("Derivative with respect to iw", fontsize=10)
        # if not self.autoscale:
        #     a.set_xlim(0, 25)
        #     a.set_ylim(-6, 6)

        # a.set_xticks([0], minor=True)
        # a.set_yticks([0], minor=True)
        # a.set_xticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.set_yticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.grid(which="minor")
        # a.set_xticks([-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5])
        # a.set_yticks([-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5])
        a.plot(np.linspace(0, 26, 50), [0] * 50, color="red", linestyle="dashed", linewidth=0.5)
        a2.plot(np.linspace(0, 26, 50), [0] * 50, color="red", linestyle="dashed", linewidth=0.5)
        a3.plot(np.linspace(0, 26, 50), [0] * 50, color="red", linestyle="dashed", linewidth=0.5)
        a4.plot(np.linspace(0, 26, 50), [0] * 50, color="red", linestyle="dashed", linewidth=0.5)
        # a.plot(np.linspace(-2, 2, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        # a.set_xlabel("$p$")
        # a.xaxis.set_label_coords(1, -0.025)
        # a.set_ylabel("$a$")
        # a.yaxis.set_label_coords(-0.025, 1)

        if self.func1 == "square":
            if self.freq == 1 / 16:
                p = [1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1]
            elif self.freq == 1 / 14:
                p = [1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1]
            elif self.freq == 1 / 12:
                p = [1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1]
            elif self.freq == 1 / 10:
                p = [1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1]
            elif self.freq == 1 / 8:
                p = [1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1]
        else:
            p = np.sin(np.arange(0, 24, 1) * 2 * np.pi * self.freq)

        weight_0 = self.slider_w0.value() / 10
        weight_1 = self.slider_w1.value() / 10
        self.label_w0.setText("iW(0): " + str(weight_0))
        self.label_w1.setText("lW(1): " + str(weight_1))

        a0, a_1, t, t1 = 0, 0, list(range(1, len(p) + 1)), list(range(len(p) + 1))
        num = np.array([weight_0])
        den = np.array([1, weight_1])
        zi = np.array([a0])
        A = lfilter(num, den, p, zi=zi)
        # a.scatter(t, p, color="white", marker="o", edgecolor="red")
        a.scatter(t1, [a0] + list(A[0]), color="black", marker=".", s=[1] * len(t1))
        lw111 = weight_1
        iw11 = weight_0 + 0.1
        num = np.array([iw11])
        den = np.array([1, lw111])
        a1 = lfilter(num, den, p, zi=zi)
        a.scatter(t1, [a0] + list(a1[0]), color="blue", marker="x")
        da_diw_0 = 0
        da_diw = lfilter(np.array([1]), den, p, zi=np.array([da_diw_0]))
        a2.scatter(t1, [da_diw_0] + list(da_diw[0]), color="white", marker="D", edgecolor="blue")
        a2.scatter(t, p, color="white", marker="s", edgecolor="black", s=[8]*len(t))

        da_dlw_0 = 0
        ad = np.array([a0] + list(A[0])[:-1])
        da_dlw = lfilter(np.array([1]), den, ad, zi=np.array([da_dlw_0]))
        a3.scatter(t1, [da_dlw_0] + list(da_dlw[0]), color="white", marker="D", edgecolor="blue")
        a3.scatter(t, ad, color="white", marker="s", edgecolor="black", s=[8]*len(t))

        a4.scatter(t1, [a0] + list(A[0]), color="black", marker=".", s=[1] * len(t1))
        lw111 = weight_1 + .1
        iw11 = weight_0
        num = np.array([iw11])
        den = np.array([1, lw111])
        a1 = lfilter(num, den, p, zi=zi)
        a4.scatter(t1, [a0] + list(a1[0]), color="blue", marker="x")

        # Setting limits so that the point moves instead of the plot.
        # a.set_xlim(-4, 4)
        # a.set_ylim(-2, 2)
        # add grid and axes
        # a.grid(True, which='both')
        # a.axhline(y=0, color='k')
        # a.axvline(x=0, color='k')
        self.canvas.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        self.canvas4.draw()

    def change_transfer_function(self, idx):
        self.func1 = self.comboBox1_functions_str[idx]
        self.graph()

    def change_freq(self, idx):
        self.freq = eval(self.comboBox2_divs[idx])
        self.graph()

    # def change_autoscale(self, idx):
    #     self.autoscale = True if idx == 1 else False
    #     self.graph()

from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class LinearLeastSquares(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LinearLeastSquares, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Linear Least Squares", 17, "\n\nBasis functions are\nspaced evenly.\n\nYou can change the first\n"
                                                      "center location and\nthe bias. The automatic\nbias will produce\n"
                                                      "overlap at 0.5.\n\nThe function is shown in\nblue and the network\n"
                                                      "response in red.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", None)

        self.randseq = [-0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754,
                        -0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754]

        self.make_plot(1, (20, 100, 450, 300))
        self.make_plot(2, (20, 390, 450, 140))
        self.figure2.set_tight_layout(True)

        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(-2, 2)
        self.axis.set_ylim(-2, 4)
        self.axis.set_xticks([-2, -1, 0, 1])
        self.axis.set_yticks([-2, -1, 0, 1, 2, 3])
        self.axis.plot(np.linspace(-2, 2, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("$p$")
        self.axis.xaxis.set_label_coords(1, -0.025)
        self.axis.set_ylabel("$a^2$")
        self.axis.yaxis.set_label_coords(-0.025, 1)

        self.axis2 = self.figure2.add_subplot(1, 1, 1)
        self.axis2.set_xlim(-2, 2)
        self.axis2.set_ylim(0, 1)
        self.axis2.set_xticks([-2, -1, 0, 1])
        self.axis2.set_yticks([0, 0.5])
        self.axis2.set_xlabel("$p$")
        self.axis2.xaxis.set_label_coords(1, -0.025)
        self.axis2.set_ylabel("$a^1$")
        self.axis2.yaxis.set_label_coords(-0.025, 1)

        self.make_combobox(1, ["Yes", "No"], (self.x_chapter_usual, 515, self.w_chapter_slider, 50), self.change_auto_bias,
                           "label_f", "Auto Bias", (self.x_chapter_usual + 60, 515 - 20, 100, 50))
        self.auto_bias = True

        self.make_slider("slider_w1_1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, -20,
                         (self.x_chapter_usual, 375, self.w_chapter_slider, 50), self.graph,
                         "label_w1_1", "W1(1,1): -2", (self.x_chapter_usual + 55, 375 - 30, 100, 50))
        self.make_slider("slider_b", QtCore.Qt.Orientation.Horizontal, (10, 1000), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 167,
                         (self.x_chapter_usual, 450, self.w_chapter_slider, 50), self.graph, "label_b", "b: 1.67")

        self.make_slider("slider_w1_2", QtCore.Qt.Orientation.Horizontal, (2, 9), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
                         (20, 560, 150, 50), self.graph, "label_w1_2", "Hidden Neurons: 5", (45, 530, 150, 50))
        self.make_slider("slider_b1_2", QtCore.Qt.Orientation.Horizontal, (2, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (170, 560, 150, 50), self.graph, "label_b1_2", "Number of Points: 10", (180, 530, 150, 50))
        self.make_slider("slider_w2_1", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (320, 560, 150, 50), self.graph, "label_w2_1", "Regularization: 0.0", (340, 530, 150, 50))

        self.make_slider("slider_w2_2", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (20, 630, 150, 50), self.graph, "label_w2_2", "Stdev Noise: 0.0", (50, 600, 150, 50))
        self.make_slider("slider_b2", QtCore.Qt.Orientation.Horizontal, (25, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 50,
                         (170, 630, 150, 50), self.graph, "label_b2", "Function Frequency: 0.50", (175, 600, 150, 50))
        self.make_slider("slider_fp", QtCore.Qt.Orientation.Horizontal, (0, 360), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 90,
                         (320, 630, 150, 50), self.graph, "label_fp", "Function Phase: 90", (340, 600, 150, 50))

        self.graph()

    def graph(self):

        w1_1 = self.slider_w1_1.value() / 10
        bias = self.slider_b.value() / 100
        S1 = self.slider_w1_2.value()
        n_points = self.slider_b1_2.value()
        ro = self.slider_w2_1.value() / 10
        sigma = self.slider_w2_2.value() / 10
        freq = self.slider_b2.value() / 100
        phase = self.slider_fp.value()

        self.label_w1_1.setText("W1(1,1): " + str(w1_1))
        self.label_b.setText("b: " + str(round(bias, 2)))
        self.label_w1_2.setText("Hidden Neurons: " + str(S1))
        self.label_b1_2.setText("Number of Points: " + str(n_points))
        self.label_w2_1.setText("Regularization: " + str(ro))
        self.label_w2_2.setText("Stdev Noise: " + str(sigma))
        self.label_b2.setText("Function Frequency: " + str(freq))
        self.label_fp.setText("Function Phase: " + str(phase))

        d1 = (2 - -2) / (n_points - 1)
        p = np.arange(-2, 2 + 0.0001, d1)
        t = np.sin(2 * np.pi * (freq * p + phase / 360)) + 1 + sigma * np.array(self.randseq[:len(p)])
        delta = (2 - -2) / (S1 - 1)
        if self.auto_bias:
            bias = 1.6652 / delta
            self.slider_b.setValue(round(bias * 100))
            self.label_b.setText("b: " + str(round(bias, 2)))
        total = 2 - -2
        W1 = (np.arange(-2, 2 + 0.0001, delta) + w1_1 - -2).T.reshape(-1, 1)
        b1 = bias * np.ones(W1.shape)
        Q = len(p)
        pp = np.repeat(p.reshape(1, -1), S1, 0)
        n1 = np.abs(pp - np.dot(W1, np.ones((1, Q)))) * np.dot(b1, np.ones((1, Q)))
        a1 = np.exp(-n1 ** 2)
        Z = np.vstack((a1, np.ones((1, Q))))
        x = np.dot(np.linalg.pinv(np.dot(Z, Z.T) + ro * np.eye(S1 + 1)), np.dot(Z, t.T))
        W2, b2 = x[:-1].T, x[-1]
        a2 = np.dot(W2, a1) + b2
        p2 = np.arange(-2, 2 + total / 100, total / 100)
        Q2 = len(p2)
        pp2 = np.repeat(p2.reshape(1, -1), S1, 0)
        n12 = np.abs(pp2 - np.dot(W1, np.ones((1, Q2)))) * np.dot(b1, np.ones((1, Q2)))
        a12 = np.exp(-n12 ** 2)
        a22 = np.dot(W2, a12) + b2
        t_exact = np.sin(2 * np.pi * (freq * p2 + phase / 360)) + 1
        temp = np.vstack((np.dot(W2.T, np.ones((1, Q2)) * a12), b2 * np.ones((1, Q2))))

        while len(self.axis.lines) > 1:
            self.axis.lines[-1].remove()
        if self.axis.collections:
            self.axis.collections[0].remove()
        self.axis.scatter(p, t, color="white", edgecolor="black")
        for i in range(len(temp)):
            self.axis.plot(p2, temp[i], linestyle="--", color="black", linewidth=0.5)
        self.axis.plot(p2, t_exact, color="blue", linewidth=2)
        self.axis.plot(p2, a22, color="red", linewidth=1)

        while self.axis2.lines:
            self.axis2.lines[-1].remove()
        for i in range(len(a12)):
            self.axis2.plot(p2, a12[i], color="black")

        self.canvas.draw()
        self.canvas2.draw()

    def change_auto_bias(self, idx):
        self.auto_bias = idx == 0
        self.graph()

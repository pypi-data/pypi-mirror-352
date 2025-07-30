from PyQt6 import QtGui, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class AdaptiveWeights(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(AdaptiveWeights, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Adaptive Weights", 18, "\n\n\nEdit the two input\nvectors and click\n[Update] to see the\nnetwork "
                                                  "learn them.\n\nW2(1,1) - solid red\nW2(1,2) - broken red\nW2(2,1) -"
                                                  " solid green\nW2(2,2) - broken green\n\nClick [Clear] to remove\n"
                                                  "old responses.",
                          PACKAGE_PATH + "Logo/Logo_Ch_18.svg", None)
        self.t = np.arange(0, 2, 0.01)

        self.make_plot(1, (10, 90, 500, 450))
        self.figure.subplots_adjust(left=0.15, right=0.95, bottom=0.125, top=0.9)

        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(-0.1, 2.1)
        self.axis.set_ylim(-0.1, 1.1)
        for i in [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]:
            self.axis.plot([i] * 10, np.linspace(-0.1, 1.1, 10), color="black", linestyle="--", linewidth=0.5)
            if i in [0, 0.4, 0.8, 1.2, 1.6, 2]:
                if i != 2:
                    self.axis.text(i + 0.0175, -0.075, "1st")
            else:
                self.axis.text(i + 0.015, -0.075, "2nd")
        self.axis.set_yticks([0, 0.25, 0.5, 0.75, 1])
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Weights W2")
        self.axis.set_title("Learning")
        self.axis.set_xticks([0, 0.5, 1, 1.5, 2])
        self.lines1, self.lines2, self.lines3, self.lines4 = [], [], [], []

        # self.paint_latex_string("latex_n11", "$1st$", 10, (20, 510, 500, 200))
        # self.paint_latex_string("latex_n12", "$n1 =$", 10, (75, 510, 500, 200))
        # self.paint_latex_string("latex_n13", "$[$", 40, (140, 510, 500, 200))
        # self.paint_latex_string("latex_n14", "$]$", 40, (200, 510, 500, 200))
        self.make_label("label_a", "1st n1 =", (60, 503, 500, 200), font_size=25)
        # self.make_label("label_a1", "[ ]", (145, 494, 500, 200), font_size=100)
        self.label_a.setStyleSheet("color:black")
        # self.label_a1.setStyleSheet("color:black")
        self.make_input_box("n_11", "0.9", (161, 530, 60, 100))
        self.make_input_box("n_12", "0.45", (161, 577, 60, 100))

        # self.paint_latex_string("latex_n21", "$2nd$", 10, (270, 510, 500, 200))
        # self.paint_latex_string("latex_n22", "$n1 =$", 10, (335, 510, 500, 200))
        # self.paint_latex_string("latex_n23", "$[$", 40, (400, 510, 500, 200))
        # self.paint_latex_string("latex_n24", "$]$", 40, (460, 510, 500, 200))
        self.make_label("label_aa", "2nd n1 =", (320, 503, 500, 200), font_size=25)
        # self.make_label("label_aa1", "[ ]", (410, 494, 500, 200), font_size=100)
        self.label_aa.setStyleSheet("color:black")
        # self.label_aa1.setStyleSheet("color:black")
        self.make_input_box("n_21", "0.45", (426, 530, 60, 100))
        self.make_input_box("n_22", "0.90", (426, 577, 60, 100))

        self.comboBox1_functions_str = ['Instar', 'Hebb']
        self.make_combobox(1, self.comboBox1_functions_str, (self.x_chapter_usual, 380, self.w_chapter_slider, 50),
                           self.change_learning_rule, "combobox1_label", "Learning rule",
                           (self.x_chapter_usual + 20, 380 - 20, 100, 50))
        self.rule = 1

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 440, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("run_button", "Update", (self.x_chapter_button, 470, self.w_chapter_button, self.h_chapter_button), self.graph)

        self.graph()

    def paintEvent(self, event):
        super(AdaptiveWeights, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        self.paint_bracket(painter, 161, 559, 646, 60)
        self.paint_bracket(painter, 426, 559, 646, 60)
        painter.end()

    def change_learning_rule(self, idx):
        self.rule = idx + 1
        # self.graph()

    def adapt(self, t, w):
        if np.fix(t / 0.2) % 2 == 0:
            n1 = self.n1
            n2 = np.array([[1], [0]])
        else:
            n1 = self.n2
            n2 = np.array([[0], [1]])
        w = w.reshape((2, 2))
        if self.rule == 1:
            wprime = (4 * np.dot(n2, np.ones((1, 2)))) * (np.dot(np.ones((2, 1)), n1.T) - w)
        else:
            wprime = 4 * np.dot(n2, n1.T) - 2 * w
        return wprime.reshape(-1)

    def graph(self):
        n11, n12 = float(self.n_11.text()), float(self.n_12.text())
        n21, n22 = float(self.n_21.text()), float(self.n_22.text())
        self.n1, self.n2 = np.array([[n11], [n12]]), np.array([[n21], [n22]])
        r1 = ode(self.adapt).set_integrator("zvode")
        r1.set_initial_value(np.zeros((4,)), 0)
        t1 = 2
        dt = 0.01
        out_11, out_21, out_12, out_22 = [], [], [], []
        while r1.successful() and r1.t < t1:
            out = r1.integrate(r1.t + dt)
            out_11.append(out[0].item())
            out_12.append(out[1].item())
            out_21.append(out[2].item())
            out_22.append(out[3].item())
        out_11[0], out_12[0], out_21[0], out_22[0] = 0, 0, 0, 0
        while len(self.lines1) > 1:
            self.lines1.pop(0).remove()
        while len(self.lines2) > 1:
            self.lines2.pop(0).remove()
        while len(self.lines3) > 1:
            self.lines3.pop(0).remove()
        while len(self.lines4) > 1:
            self.lines4.pop(0).remove()
        for line in self.lines1:
            line.set_alpha(0.2)
        for line in self.lines2:
            line.set_alpha(0.2)
        for line in self.lines3:
            line.set_alpha(0.2)
        for line in self.lines4:
            line.set_alpha(0.2)
        self.lines1.append(self.axis.plot(self.t, out_11, color="red")[0])
        self.lines2.append(self.axis.plot(self.t, out_12, color="red", linestyle="dashed")[0])
        self.lines3.append(self.axis.plot(self.t, out_21, color="green")[0])
        self.lines4.append(self.axis.plot(self.t, out_22, color="green", linestyle="dashed")[0])
        self.canvas.draw()

    def on_clear(self):
        while len(self.lines1) > 1:
            self.lines1.pop(0).remove()
        while len(self.lines2) > 1:
            self.lines2.pop(0).remove()
        while len(self.lines3) > 1:
            self.lines3.pop(0).remove()
        while len(self.lines4) > 1:
            self.lines4.pop(0).remove()
        self.canvas.draw()

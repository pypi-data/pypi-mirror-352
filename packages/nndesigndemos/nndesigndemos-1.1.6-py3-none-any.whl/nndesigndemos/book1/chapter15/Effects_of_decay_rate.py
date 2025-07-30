from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class EffectsOfDecayRate(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(EffectsOfDecayRate, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Effects off Decay Rate", 15, "Use the slider bars to\nadjust learning and\ndecay rates.\n\n"
                                                        "Click [Clear] to remove\nold responses.\n\nClick [Random] to get\n"
                                                        "random parameters.",
                          PACKAGE_PATH + "Logo/Logo_Ch_15.svg", None)

        self.make_plot(1, (20, 100, 470, 470))
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(0, 30)
        self.axis.set_ylim(0, 10)
        self.axis.plot([0] * 30, np.linspace(0, 30, 30), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot(np.linspace(0, 10, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_xlabel("Time")
        self.axis.set_ylabel("Weight")
        self.axis.set_title("Hebb Learning")
        self.lines = []

        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (20, 580, 470, 50), self.graph, "label_lr", "Learning Rate: 1.00", (210, 555, 200, 50))
        self.make_slider("slider_dr", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (20, 640, 470, 50), self.graph, "label_dr", "Decay Rate: 1.00", (220, 615, 200, 50))

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 320, self.w_chapter_button, self.h_chapter_button), self.on_clear)
        self.make_button("random_button", "Random", (self.x_chapter_button, 350, self.w_chapter_button, self.h_chapter_button), self.on_random)

        self.do_graph = True

        self.graph()

    def graph(self):
        if self.do_graph:
            lr = self.slider_lr.value() / 10
            dr = self.slider_dr.value() / 10
            # print(lr, dr, self.slider_lr, self.slider_dr)
            self.label_lr.setText("Learning Rate: " + str(round(lr, 2)))
            self.label_dr.setText("Decay Rate: " + str(round(dr, 2)))
            w = 0
            wtot = []
            for i in range(1, 31):
                a = self.hardlim(1 * (i % 2 == 0) + w * 1 - 0.5)
                w = w + lr * a * 1 - dr * w
                wtot.append(w)
            ind = [i for i in range(len(wtot)) if wtot[i] > 10]
            if ind:
                ind = ind[0]
                wtot = wtot[:ind - 1]
            while len(self.lines) > 3:
                self.lines.pop(0).remove()
            for line in self.lines:
                line.set_color("gray")
                line.set_alpha(0.5)
            self.lines.append(self.axis.plot(range(len(wtot)), wtot, "o", color="red")[0])
            self.canvas.draw()

    def on_clear(self):
        while len(self.lines) > 1:
            self.lines.pop(0).remove()
        self.canvas.draw()

    def on_random(self):
        self.do_graph = False
        self.slider_lr.setValue(round(np.random.uniform(0, 1) * 100))
        # print('aaaaaa')
        self.do_graph = True
        self.slider_dr.setValue(round(np.random.uniform(0, 1) * 100))
        # print('bbbbbb')

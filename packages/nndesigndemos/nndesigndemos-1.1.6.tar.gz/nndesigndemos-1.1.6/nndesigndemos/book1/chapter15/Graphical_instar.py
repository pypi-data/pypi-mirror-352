from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class GraphicalInstar(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(GraphicalInstar, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Graphical Instar", 15, "Click on the top graph\nto change the green\nweight vector.\n\n"
                                                  "Click on the bottom graph\nto change the red\ninput vector.\n\n"
                                                  "Use the slider to\nchange the learning rate.\n\n"
                                                  "The change in the weight\nvector is shown with\na black arrow.\n\n"
                                                  "Click [Update] to\nmake the change.",
                          PACKAGE_PATH + "Logo/Logo_Ch_15.svg", None, description_coords=(535, 140, 450, 300))

        self.make_plot(1, (115, 100, 290, 290))
        self.make_plot(2, (115, 385, 290, 290))

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Click to change weight")
        self.axes_1.set_xlim(-1.1, 1.1)
        self.axes_1.set_ylim(-1.1, 1.1)
        self.w = np.array([[1, 0.5]])
        self.axes1_w = self.axes_1.quiver([0], [0], [self.w[0, 0]], [self.w[0, 1]], units="xy", scale=1, color="green")
        self.axes_1.plot([0] * 6, np.linspace(-1.1, 1.1, 6), color="black", linestyle="--", linewidth=0.2)
        self.axes_1.plot(np.linspace(-1.1, 1.1, 6), [0] * 6, color="black", linestyle="--", linewidth=0.2)
        self.axes_1.set_xticks([], [])
        self.axes_1.set_yticks([], [])
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick1)

        self.lr = 0.5
        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
                         (self.x_chapter_usual, 470, self.w_chapter_slider, 50), self.slide,
                         "label_lr", "Learning Rate: 0.5", (self.x_chapter_slider_label - 30, 440, 150, 50))

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_title("Click to change input")
        self.axes_2.set_xlim(-1.1, 1.1)
        self.axes_2.set_ylim(-1.1, 1.1)
        self.axes2_w = self.axes_2.quiver([0], [0], [self.w[0, 0]], [self.w[0, 1]], units="xy", scale=1, color="green")
        self.input = np.array([[0.5], [1]])
        self.axes2_input = self.axes_2.quiver([0], [0], [self.input[0, 0]], [self.input[1, 0]], units="xy", scale=1, color="red")
        self.axes2_v, self.v = None, None
        self.axes2_line, = self.axes_2.plot([], color="black", linewidth=0.5)
        self.axes_2.plot([0] * 6, np.linspace(-1.1, 1.1, 6), color="black", linestyle="--", linewidth=0.2)
        self.axes_2.plot(np.linspace(-1.1, 1.1, 6), [0] * 6, color="black", linestyle="--", linewidth=0.2)
        self.axes_2.set_xticks([], [])
        self.axes_2.set_yticks([], [])
        self.compute()
        self.canvas2.draw()
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick2)

        self.make_button("button", "Update", (self.x_chapter_button, 520, self.w_chapter_button, self.h_chapter_button), self.update)

    def slide(self):
        self.lr = self.slider_lr.value() / 10
        self.label_lr.setText("Learning rate: " + str(self.lr))
        self.compute()
        self.canvas.draw()
        self.canvas2.draw()

    def on_mouseclick1(self, event):
        if event.xdata != None and event.xdata != None:
            self.w = np.array([[event.xdata, event.ydata]])
            self.axes1_w.set_UVC(event.xdata, event.ydata)
            self.axes2_w.set_UVC(event.xdata, event.ydata)
            self.canvas.draw()
            self.compute()
            self.canvas2.draw()

    def on_mouseclick2(self, event):
        if event.xdata != None and event.xdata != None:
            self.input = np.array([[event.xdata], [event.ydata]])
            self.axes2_input.set_UVC(event.xdata, event.ydata)
            self.compute()
            self.canvas2.draw()

    def compute(self):
        if len(self.axes_2.collections) == 3:
            self.axes_2.collections[-1].remove()
        self.v = self.w + self.lr * (self.input.T - self.w)
        self.axes2_line.set_data([self.w[0, 0], self.input[0, 0]], [self.w[0, 1], self.input[1, 0]])
        self.axes2_v = self.axes_2.quiver([self.w[0, 0]], [self.w[0, 1]], [self.v[0, 0] - self.w[0, 0]], [self.v[0, 1] - self.w[0, 1]], units="xy", scale=1, color="black")

    def update(self):
        self.w = self.v
        self.axes1_w.set_UVC(self.w[0, 0], self.w[0, 1])
        self.axes2_w.set_UVC(self.w[0, 0], self.w[0, 1])
        self.compute()
        self.canvas.draw()
        self.canvas2.draw()

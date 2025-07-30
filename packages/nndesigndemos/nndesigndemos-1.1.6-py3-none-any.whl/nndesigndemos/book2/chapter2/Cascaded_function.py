from PyQt6 import QtWidgets, QtGui, QtCore
import math
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class CascadedFunction(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(CascadedFunction, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Cascaded Function", 2, "\nExperiment with the hidden\nfunction and number\nof layers "
                                                  "using\nthe dropdown menus below.\n\nSet the input value\n"
                                                  "to 0 in order to start\nthe animation, or control it\nmanually by moving"
                                                  "\nthe slider.",
                          PACKAGE_PATH + "Chapters/2_D/Logo_Ch_2.svg", PACKAGE_PATH + "Chapters/2_D/2f_1_1.svg", 2, icon_move_left=120)

        self.make_plot(1, (90, 300, 370, 370))

        self.comboBox1_functions = [self.Poslin, self.LogSig]
        self.make_combobox(1, ["ReLU", 'LogSig'], (self.x_chapter_usual, 330, self.w_chapter_slider, 50),
                           self.change_transfer_function, "label_f", "f")
        self.func = self.Poslin

        self.make_combobox(2, ["Two", 'Three', "Four"], (self.x_chapter_usual, 390, self.w_chapter_slider, 50),
                           self.combo_bbox2, "label_iter", "Number of layers",
                           (self.x_chapter_slider_label - 40, 370, self.w_chapter_slider, 50))
        self.func1 = self.two

        self.make_slider("sliderval", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (self.x_chapter_usual, 460, self.w_chapter_slider, 50), self.slide, "label_iter",
                         "Input value: 0", (self.x_chapter_usual + 40, 460 - 25, 150, 50))
        self.last_idx = 0
        self.do_graph = True
        self.ani = None

        self.graph()

    def combo_bbox2(self, idx):
        if idx == 0:
            self.func1 = self.two
            self.icon2.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Chapters/2_D/2f_1.svg").pixmap(500 * self.w_ratio, 200 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.graph()
        elif idx == 1:
            self.func1 = self.three
            self.icon2.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Chapters/2_D/3f_1.svg").pixmap(500 * self.w_ratio, 200 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.graph()
        if idx == 2:
            self.func1 = self.four
            self.icon2.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Chapters/2_D/4f_1.svg").pixmap(500 * self.w_ratio, 200 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.graph()

    def slide(self):
        # print('self.do_graph', self.do_graph, self.last_idx)
        if self.do_graph and self.ani:
        #     print('self.do_graph and self.ani')
            if self.ani.event_source:
                self.ani.event_source.stop()
            self.do_graph = True
        self.last_idx = self.sliderval.value()
        self.label_iter.setText("Input value: {}".format(self.last_idx))
        if self.do_graph:
            self.graph()

    def graph(self):
        self.figure.clf()  # clear the old figure, and prepare for new one

        a = self.figure.add_subplot(1, 1, 1)

        p1 = np.arange(0, 1, 0.01)
        a2 = self.net1(p1)

        a.plot(p1, p1, 'g', linewidth=2)
        a.plot(p1, a2, 'b', linewidth=2)

        if self.func1() == 2:
            self.aaa = np.linspace(0.01, 0.99, 100)
        elif self.func1() == 3:
            self.aaa = np.linspace(0.01, 0.99, 200)
        else:
            self.aaa = np.linspace(0.01, 0.99, 300)

        markersize = 4
        self.plot_1, = a.plot([], 'ko-', markersize=markersize)

        a.axhline(y=0, color='k')
        a.axvline(x=0, color='k')
        if self.last_idx == 0:
            self.ani = FuncAnimation(self.figure, self.on_animate, frames=len(self.aaa), interval=50, repeat=False)
            self.canvas.draw()
        else:

            for i in range(len(self.aaa)):
                xx, yy = self.getxx(self.aaa[i], self.func1())
                a.plot(xx[-1], yy[-1], 'ro', markersize=markersize)

            xx, yy = self.getxx((self.last_idx / 100), self.func1())
            a.plot(xx, yy, 'ko-', markersize=markersize)

            if self.do_graph:
                self.canvas.draw()

    def on_animate(self, idx):  # This idx is needed, even if it's not being used explicitly!
        # print(idx)
        if self.last_idx < 100:
            xx, yy = self.getxx(self.aaa[self.last_idx], self.func1())
            self.last_idx += 1
            self.plot_1.set_data(xx, yy)

            self.label_iter.setText("Number of iterations: {}".format(self.last_idx))
            self.do_graph = False
            self.graph()
            self.sliderval.setValue(self.last_idx)
            self.do_graph = True
            # self.canvas.draw()

    def getxx(self, p, nr):
        xx = np.array([])
        yy = np.array([])
        x = p
        x1 = p
        # print('p, nr', p, nr)
        for i in range(int(nr)):
            out1 = self.net1(x)
            out1 = float(out1)
            # print('xx, yy, x, out1', xx, yy, x, out1)
            xx = np.concatenate((xx, [x, x, x, out1]))
            yy = np.concatenate((yy, [x, out1, out1, out1]))
            # print('xx, yy', xx, yy)
            x = out1
        yy[0] = np.array([0])
        xx[-1] = x1
        return xx, yy

    def net1(self, x):
        if hasattr(self, 'func'):
            if self.func.__str__().split()[2].split('.')[1] == 'LogSig':
                w1 = np.array([[15, 15]]).reshape(-1, 1)
                b1 = np.array([[-0.25*15, -(1-0.25)*15]]).reshape(-1, 1)
                w2 = np.array([[1, -1]])
                b2 = np.array([0])
                func3 = np.vectorize(self.func, otypes=[float])
                a1 = func3(w1 * x + b1 * np.ones((1, 1)))
                y = np.dot(w2, a1) + b2*np.ones((1, 1))
                y1 = y.flatten()
            else:
                w1 = np.array([[1, 1]]).reshape(-1, 1)
                b1 = np.array([[0, -0.5]]).reshape(-1, 1)
                w2 = np.array([[2, -4]])
                b2 = np.array([0])
                func = np.vectorize(self.func, otypes=[float])
                a1 = func(w1 * x + b1 * np.ones((1, 1)))
                y = np.dot(w2, a1) + b2 * np.ones((1, 1))
                y1 = y.flatten()
        else:
            w1 = np.array([[1, 1]]).reshape(-1, 1)
            b1 = np.array([[0, -0.5]]).reshape(-1, 1)
            w2 = np.array([[2, -4]])
            b2 = np.array([0])
            func = np.vectorize(self.Poslin, otypes=[float])
            a1 = func(w1 * x + b1 * np.ones((1, 1)))
            y = np.dot(w2, a1) + b2*np.ones((1, 1))
            y1 = y.flatten()
        return y1

    def change_transfer_function(self, idx):
        self.func = self.comboBox1_functions[idx]
        self.graph()

    @staticmethod
    def two():
        return np.array([2])

    @staticmethod
    def three():
        return np.array([3])

    @staticmethod
    def four():
        return np.array([4])

    def Poslin(self, x):
        if (x < 0):
            return 0
        else:
            return x

    def LogSig(self, x):
        return 1 / (1 + math.e ** (-x))

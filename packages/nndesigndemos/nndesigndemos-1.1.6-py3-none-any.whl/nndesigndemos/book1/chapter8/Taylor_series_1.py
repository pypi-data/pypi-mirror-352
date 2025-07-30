from PyQt6 import QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class TaylorSeries1(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(TaylorSeries1, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Taylor Series #1", 8, "Click on the top graph to\ncreate a Taylor series\napproximation"
                                                 " of the\ncosine function.\n\nClick on the checkboxes\nto turn various orders\n"
                                                 "of approximation\non and off.",
                          PACKAGE_PATH + "Logo/Logo_Ch_8.svg", None)

        self.make_plot(1, (115, 100, 290, 290))
        self.make_plot(2, (115, 385, 290, 290))

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("cos(x)", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-6, 6)
        self.axes_1.set_ylim(-2, 2)
        self.axes_1.set_xticks([-6, -4, -2, 0, 2, 4])
        self.axes_1.set_yticks([-2, -1, 0, 1])
        self.axes_1.set_xlabel("$x$")
        self.axes_1.xaxis.set_label_coords(1, -0.025)
        self.axes_1.set_ylabel("$y$")
        self.axes_1.yaxis.set_label_coords(-0.025, 1)
        self.x_points = np.linspace(-6, 6)
        self.axes_1.plot(self.x_points, np.cos(self.x_points), "-")
        self.axes1_point_draw, = self.axes_1.plot([], 'mo')
        self.axes_1.text(-3.5, 1.5, "<CLICK ON ME>")
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_title("Approximation", fontdict={'fontsize': 10})
        self.f0, self.f1, self.f2, self.f3, self.f4 = None, None, None, None, None
        self.axes2_point_draw, = self.axes_2.plot([], 'mo')
        self.axes2_function, = self.axes_2.plot([], '-')
        self.axes2_approx_0, = self.axes_2.plot([], 'r-')
        self.axes2_approx_1, = self.axes_2.plot([], 'b-')
        self.axes2_approx_2, = self.axes_2.plot([], 'g-')
        self.axes2_approx_3, = self.axes_2.plot([], 'y-')
        self.axes2_approx_4, = self.axes_2.plot([], 'c-')
        self.axes_2.set_xlim(-6, 6)
        self.axes_2.set_ylim(-2, 2)
        self.axes_2.set_xlim(-6, 6)
        self.axes_2.set_ylim(-2, 2)
        self.axes_2.set_xticks([-6, -4, -2, 0, 2, 4])
        self.axes_2.set_yticks([-2, -1, 0, 1])
        self.axes_2.set_xlabel("$x$")
        self.axes_2.xaxis.set_label_coords(1, -0.025)
        self.axes_2.set_ylabel("$y$")
        self.axes_2.yaxis.set_label_coords(-0.025, 1)
        self.canvas2.draw()

        self.make_checkbox("function_cbx", "Function", (self.x_chapter_slider_label - 20, 310, 100, 50),
                           self.function_checked, True)
        self.make_checkbox("order0_cbx", "Order 0", (self.x_chapter_slider_label - 20, 350, 100, 50),
                           self.order0_checked, False)
        self.make_checkbox("order1_cbx", "Order 1", (self.x_chapter_slider_label - 20, 400, 100, 50),
                           self.order1_checked, True)
        self.make_checkbox("order2_cbx", "Order 2", (self.x_chapter_slider_label - 20, 450, 100, 50),
                           self.order2_checked, False)
        self.make_checkbox("order3_cbx", "Order 3", (self.x_chapter_slider_label - 20, 500, 100, 50),
                           self.order3_checked, False)
        self.make_checkbox("order4_cbx", "Order 4", (self.x_chapter_slider_label - 20, 550, 100, 50),
                           self.order4_checked, False)

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            self.axes1_point_draw.set_data([event.xdata], [np.cos(event.xdata)])
            self.axes2_point_draw.set_data([event.xdata], [np.cos(event.xdata)])
            self.canvas.draw()
            self.f0 = np.cos(event.xdata) + np.zeros(self.x_points.shape)
            self.f1 = self.f0 - np.sin(event.xdata) * (self.x_points - event.xdata)
            self.f2 = self.f1 - np.cos(event.xdata) * (self.x_points - event.xdata) ** 2 / 2
            self.f3 = self.f2 + np.sin(event.xdata) * (self.x_points - event.xdata) ** 3 / 6
            self.f4 = self.f3 + np.cos(event.xdata) * (self.x_points - event.xdata) ** 4 / 24
            self.draw_taylor()

    def draw_taylor(self):
        if self.function_cbx.checkState().value:
            self.axes2_function.set_data(self.x_points, np.cos(self.x_points))
        if self.order0_cbx.checkState().value:
            self.axes2_approx_0.set_data(self.x_points, self.f0)
        if self.order1_cbx.checkState().value:
            self.axes2_approx_1.set_data(self.x_points, self.f1)
        if self.order2_cbx.checkState().value:
            self.axes2_approx_2.set_data(self.x_points, self.f2)
        if self.order3_cbx.checkState().value:
            self.axes2_approx_3.set_data(self.x_points, self.f3)
        if self.order4_cbx.checkState().value:
            self.axes2_approx_4.set_data(self.x_points, self.f4)
        self.canvas2.draw()

    def function_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            self.axes2_function.set_data(self.x_points, np.cos(self.x_points))
        else:
            self.axes2_function.set_data([], [])
        self.canvas2.draw()

    def order0_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            if self.f0 is not None:
                self.axes2_approx_0.set_data(self.x_points, self.f0)
        else:
            self.axes2_approx_0.set_data([], [])
        self.canvas2.draw()

    def order1_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            if self.f1 is not None:
                self.axes2_approx_1.set_data(self.x_points, self.f1)
        else:
            self.axes2_approx_1.set_data([], [])
        self.canvas2.draw()

    def order2_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            if self.f2 is not None:
                self.axes2_approx_2.set_data(self.x_points, self.f2)
        else:
            self.axes2_approx_2.set_data([], [])
        self.canvas2.draw()

    def order3_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            if self.f3 is not None:
                self.axes2_approx_3.set_data(self.x_points, self.f3)
        else:
            self.axes2_approx_3.set_data([], [])
        self.canvas2.draw()

    def order4_checked(self, state):
        if state == QtCore.Qt.CheckState.Checked.value:
            if self.f4 is not None:
                self.axes2_approx_4.set_data(self.x_points, self.f4)
        else:
            self.axes2_approx_4.set_data([], [])
        self.canvas2.draw()

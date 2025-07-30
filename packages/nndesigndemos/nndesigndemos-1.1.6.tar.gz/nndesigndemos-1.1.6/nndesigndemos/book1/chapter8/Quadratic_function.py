from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class QuadraticFunction(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(QuadraticFunction, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Quadratic Function", 8, "\n\nChange the values of the\nHessian matrix A, the\nvector d, and the constant c.\n"
                                                   "Then click [Update] to see\nthe new function.\n\nNote that the Hessian matrix\n"
                                                   "will always be symmetric.\n\nYou can rotate the 3D plots\nby clicking and dragging\n"
                                                   "in the plot window.",
                          PACKAGE_PATH + "Logo/Logo_Ch_8.svg", None)

        self.x = np.array([-2, -1.8, -1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0,
                           0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2])
        self.y = np.copy(self.x)

        self.make_plot(1, (20, 120, 230, 230))
        self.make_plot(2, (270, 120, 230, 230))

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Function F", fontdict={'fontsize': 10})
        # self.axes_1.set_xlim(-2, 2)
        # self.axes_1.set_ylim(-2, 2)
        # self.axes1_point, = self.axes_1.plot([], "*")

        self.axes_2 = self.figure2.add_subplot(projection='3d')
        self.axes_2.set_title("Function F", fontdict={'fontsize': 10}, pad=2)
        # self.axes_2.set_xlim(-2, 2)
        # self.axes_2.set_ylim(-2, 2)
        self.axes_2.view_init(30, -30)
        # self.canvas2.mpl_connect("motion_notify_event", self.print_view)

        # self.make_label("label_eq", "F(x) = 1/2 x.T A x + d x.T + c", (50, 310, 440, 200))

        self.eq = QtWidgets.QLabel(self)
        pixmap = QtGui.QIcon(PACKAGE_PATH + "Figures/equation1.svg").pixmap(350 * self.w_ratio, 200 * self.h_ratio, QtGui.QIcon.Mode.Normal,
                                               QtGui.QIcon.State.On)
        self.eq.setPixmap(pixmap)
        self.eq.setGeometry(100 * self.w_ratio, 320 * self.h_ratio,
                            440 * self.w_ratio, 200 * self.h_ratio)

        # if self.running_on_windows:
        #     self.paint_latex_string("latex_eq", "$F(x) = 1/2 \cdot x^T \cdot A \cdot x + d \cdot x^T + c$", 10, (50, 320, 500, 200))
        # if self.running_on_linux:
        #     self.paint_latex_string("latex_eq", "$F(x) = 1/2 \cdot x^T \cdot A \cdot x + d \cdot x^T + c$", 10, (50, 320, 500, 200))
        # else:
        #     self.paint_latex_string("latex_eq", "$F(x) = 1/2 \cdot x^T \cdot A \cdot x + d \cdot x^T + c$",
        #                             10 * (self.w_ratio + self.h_ratio) / 2, (50, 320, 500, 200))

        # self.paint_latex_string("latex_A1", "$A =$", 16, (10, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_A2", "$[$", 45, (80, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_A3", "$]$", 45, (175, 415 + 30, 500, 200))
        self.make_label("label_a", "A =", (53, 445, 500, 200), font_size=25)
        # self.make_label("label_a1", "[   ]", (94, 435, 500, 200), font_size=100)
        self.label_a.setStyleSheet("color:black")
        # self.label_a1.setStyleSheet("color:black")

        self.make_input_box("a_11", "1.5", (100, 440 + 30, 55, 100))
        self.make_input_box("a_12", "-0.7", (165, 440 + 30, 55, 100))
        self.make_input_box("a_21", "-0.7", (100, 490 + 30, 55, 100))
        self.make_input_box("a_22", "1.0", (165, 490 + 30, 55, 100))
        # self.matrix = QtWidgets.QLabel(self)
        # pixmap = QtGui.QIcon(PACKAGE_PATH + "Figures/matrix.svg").pixmap(300 * self.w_ratio, 100 * self.h_ratio,
        #                                                                     QtGui.QIcon.Mode.Normal,
        #                                                                     QtGui.QIcon.State.On)
        # self.matrix.setPixmap(pixmap)
        # self.matrix.setGeometry(43 * self.w_ratio, 445 * self.h_ratio, 440 * self.w_ratio, 200 * self.h_ratio)
        # self.paint_latex_string("latex_d1", "$d =$", 16, (230, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_d2", "$[$", 45, (300, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_d3", "$]$", 45, (350, 415 + 30, 500, 200))
        self.make_label("label_d", "d =", (265, 445, 500, 200), font_size=25)
        # self.make_label("label_d1", "[ ]", (305, 435, 500, 200), font_size=100)
        self.label_d.setStyleSheet("color:black")
        # self.label_d1.setStyleSheet("color:black")
        self.make_input_box("d_1", "0.35", (324, 440 + 30, 55, 100))
        self.make_input_box("d_2", "0.25", (324, 490 + 30, 55, 100))

        # self.paint_latex_string("latex_c1", "$c =$", 12, (405 - 5, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_c2", "$[$", 16, (460 - 5, 415 + 30, 500, 200))
        # self.paint_latex_string("latex_c3", "$]$", 16, (500 - 5, 415 + 30, 500, 200))
        self.make_label("label_c", "c =", (415, 445, 500, 200), font_size=25)
        # self.make_label("label_c1", "[    ]", (455, 442, 500, 200), font_size=30)
        self.label_c.setStyleSheet("color:black")
        # self.label_c1.setStyleSheet("color:black")
        self.make_input_box("c", "1.0", (452, 465 + 30, 55, 100))

        self.make_button("run_button", "Update", (self.x_chapter_button, 355, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.on_run()

    # def print_view(self, event):
    #     print(self.axes_2.elev, self.axes_2.azim)

    def paintEvent(self, event):
        super(QuadraticFunction, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        self.paint_bracket(painter, 100, 500, 590, 118)
        self.paint_bracket(painter, 320, 500, 590, 65)
        self.paint_bracket(painter, 452, 530, 560, 56, 5)
        painter.end()

    def on_run(self):
        if self.a_12.text() != self.a_21.text():
            self.a_21.setText(self.a_12.text())
        A = np.array([[float(self.a_11.text()), float(self.a_12.text())], [float(self.a_21.text()), float(self.a_22.text())]])
        d = np.array([[float(self.d_1.text())], [float(self.d_2.text())]])
        c = float(self.c.text())
        self.update(A, d, c)

    def update(self, A, d, c):

        minima = -np.dot(np.linalg.pinv(A), d)
        x0, y0 = minima[0, 0], minima[1, 0]
        xx = self.x + x0
        yy = self.y + y0
        XX, YY = np.meshgrid(xx, yy)
        F = (A[0, 0] * XX ** 2 + (A[0, 1] + A[1, 0]) * XX * YY + A[1, 1] * YY ** 2) / 2 + d[0, 0] * XX + d[
            1, 0] * YY + c
        e, v = np.linalg.eig(A)

        # Removes stuff
        while self.axes_1.collections:
            for collection in self.axes_1.collections:
                collection.remove()
        for line in self.axes_1.lines:
            line.remove()
        while self.axes_2.collections:
            for collection in self.axes_2.collections:
                collection.remove()

        # Draws new stuff
        self.axes_1.set_xlim(np.min(xx), np.max(xx))
        self.axes_1.set_ylim(np.min(yy), np.max(yy))
        self.axes_1.plot([x0] * 20, np.linspace(np.min(yy), np.max(yy), 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_1.plot(np.linspace(np.min(xx), np.max(xx), 20), [y0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_1.contour(XX, YY, F)
        self.axes_1.quiver([x0], [y0], [-v[0, 0]], [-v[1, 0]], units="xy", scale=1, label="Eigenvector 1")
        self.axes_1.quiver([x0], [y0], [-v[0, 1]], [-v[1, 1]], units="xy", scale=1, label="Eigenvector 2")
        self.axes_2.plot_surface(XX, YY, F, color="cyan")
        self.canvas.draw()
        self.canvas2.draw()

from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class EarlyStoppingRegularization(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(EarlyStoppingRegularization, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Early Stopping/Regularization", 13, "Click on the epoch slider\nto see the steepest\ndescent trajectory.\n\n"
                                                               "Click on the ro slider\nto see the minimum of\nthe regularized"
                                                               "\nperformance index.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, description_coords=(535, 110, 450, 200))

        p1, p2 = np.array([[1], [1]]), np.array([[-1], [1]])
        t1, t2 = 1, -1
        prob1, prob2 = 0.75, 0.25
        R = prob1 * p1.dot(p1.T) + prob2 * p2.dot(p2.T)
        h = prob1 * t1 * p1 + prob2 * t2 * p2
        c = prob1 * t1 ** 2 + prob2 * t2 ** 2
        a, b = 2 * R, -2 * h
        a1, b1, c1 = np.array([[2, 0], [0, 2]]), np.zeros((2, 1)), 0

        x1, y1 = np.linspace(-0.5, 1.5, 50), np.linspace(-1, 1, 50)
        X, Y = np.meshgrid(x1, y1)

        max_epoch = 100

        self.make_plot(1, (100, 90, 300, 300))
        self.figure.subplots_adjust(left=0.175, bottom=0.175, right=0.95)
        self.make_plot(2, (100, 380, 300, 300))
        self.figure2.subplots_adjust(left=0.175, bottom=0.175, right=0.95)

        F = (a[0, 0] * X ** 2 + (a[0, 1] + a[1, 0]) * X * Y + a[1, 1] * Y ** 2) / 2 + b[0] * X + b[1] * Y + c
        F = np.clip(F, np.min(F), 3)
        sol = -np.linalg.pinv(a).dot(b)

        F1 = (a1[0, 0] * X ** 2 + (a1[0, 1] + a1[1, 0]) * X * Y + a1[1, 1] * Y ** 2) / 2 + b1[0] * X + b1[1] * Y + c1
        sol1 = -np.linalg.pinv(a1).dot(b1)
        F1 = np.clip(F1, np.min(F1), 3)

        x1, x2 = 0, 0
        self.lr_path_x, self.lr_path_y = [x1], [x2]
        lr = 0.05
        for epoch in range(max_epoch):
            grad = a.dot(np.array([[x1], [x2]])) + b
            x1 -= lr * grad[0, 0]
            x2 -= lr * grad[1, 0]
            self.lr_path_x.append(x1)
            self.lr_path_y.append(x2)

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_xticks([0])
        self.axes_1.set_yticks([0])
        self.axes_1.set_title("Early Stopping")
        self.axes_1.set_xlabel("$x(1)$")
        self.axes_1.set_ylabel("$x(2)$")
        self.axes_1.contour(X, Y, F, levels=[0.02, 0.07, 0.15], colors="red")
        self.axes_1.contour(X, Y, F1, levels=[0.025, 0.08, 0.15], colors="red")
        self.axes_1_lr_pos, = self.axes_1.plot([], [], "o", fillstyle="none",
                                               markersize=int(6 * (self.w_ratio + self.h_ratio) / 2), color="k")
        self.axes_1_lr_pos.set_data([sol1[0]], [sol1[1]])
        self.axes_1.plot(sol[0], sol[1], ".", color="blue")
        self.axes_1.plot(sol1[0], sol1[1], ".", color="blue")
        self.axes_1.plot(self.lr_path_x, self.lr_path_y, color="blue")
        self.canvas.draw()

        x1, x2 = sol[0], sol[1]
        self.ro_path_x, self.ro_path_y = [x1], [x2]
        self.ro_list = []
        for alpha in np.linspace(0, 1, 101):
            beta = 1 - alpha
            x = -np.linalg.inv(beta * a + alpha * a1).dot((beta * b))
            if beta == 0:
                self.ro_list.append("inf")
            else:
                self.ro_list.append(alpha / beta)
            x1 = x[0, 0]
            x2 = x[1, 0]
            self.ro_path_x.append(x1)
            self.ro_path_y.append(x2)

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_xticks([0])
        self.axes_2.set_yticks([0])
        self.axes_2.set_title("Regularization")
        self.axes_2.set_xlabel("$x(1)$")
        self.axes_2.set_ylabel("$x(2)$")
        self.axes_2.contour(X, Y, F, levels=[0.02, 0.07, 0.15], colors="red")
        self.axes_2.contour(X, Y, F1, levels=[0.025, 0.08, 0.15], colors="red")
        self.axes_2_ro_pos, = self.axes_2.plot([], [], "o", fillstyle="none",
                                               markersize=int(6 * (self.w_ratio + self.h_ratio) / 2), color="k")
        self.axes_2_ro_pos.set_data([sol[0]], [sol[1]])
        self.axes_2.plot(sol[0], sol[1], ".", color="blue")
        self.axes_2.plot(sol1[0], sol1[1], ".", color="blue")

        self.ro_path_x = [(x[0] if isinstance(x, np.ndarray) else x) for x in self.ro_path_x]
        self.ro_path_y = [(y[0] if isinstance(y, np.ndarray) else y) for y in self.ro_path_y]

        self.axes_2.plot(self.ro_path_x, self.ro_path_y, color="blue")
        self.canvas2.draw()

        self.make_slider("slider_epoch", QtCore.Qt.Orientation.Horizontal, (0, max_epoch), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 1,
                         (self.x_chapter_usual, 320, self.w_chapter_slider, 50), self.slide, "label_epoch", "Epoch: 1")

        self.make_slider("slider_ro", QtCore.Qt.Orientation.Horizontal, (0, max_epoch), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (self.x_chapter_usual, 390, self.w_chapter_slider, 50), self.slide, "label_ro", "ro: 0.00")

    def slide(self):
        epoch = self.slider_epoch.value()
        self.label_epoch.setText("Epoch: " + str(epoch))
        ro_epoch = self.slider_ro.value()
        if type(self.ro_list[ro_epoch]) == str:
            self.label_ro.setText("ro: " + self.ro_list[ro_epoch])
        else:
            self.label_ro.setText("ro: " + str(round(self.ro_list[ro_epoch], 2)))
        self.axes_1_lr_pos.set_data([self.lr_path_x[epoch]], [self.lr_path_y[epoch]])
        self.canvas.draw()
        self.axes_2_ro_pos.set_data([self.ro_path_x[ro_epoch]], [self.ro_path_y[ro_epoch]])
        self.canvas2.draw()

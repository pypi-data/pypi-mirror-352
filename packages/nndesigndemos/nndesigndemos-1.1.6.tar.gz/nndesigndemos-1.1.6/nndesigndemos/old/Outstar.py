from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class OutStar(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(OutStar, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Outstar", 15, "\n\n\nClick [Fruit] to send a fruit\ndown the belt to be\nrecognized.\n\n"
                                         "Click [Update] to\napply the Hebb rule.\n\nOnce the network has\n"
                                         "seen several pineapples\nwith both scanners, it\nwill recall their\nmeasurements"
                                         " with the\nfirst scanner off.",
                          PACKAGE_PATH + "Logo/Logo_Ch_15.svg", None)

        self.p, self.a, self.label, self.fruit = None, None, None, None
        self.n_temp, self.banana_temp = None, None
        self.timer = None

        self.figure2_w, self.figure2_h = 475, 350
        self.icon4 = QtWidgets.QLabel(self)
        self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon4.setGeometry(28 * self.w_ratio, 100 * self.h_ratio, self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio)

        self.figure_w, self.figure_h = 575, 190
        self.icon3 = QtWidgets.QLabel(self)
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon3.setGeometry(28 * self.w_ratio, 420 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)

        self.W2, self.W1 = np.zeros((3, 1)), np.eye(3)
        self.p1 = None
        self.shape, self.texture, self.weight = "?", "?", "?"
        self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
        self.pineapple = "?"

        self.first_scanner_on = True
        self.make_checkbox("checkbox_scanner", "First Scanner", (self.x_chapter_button, 370, self.w_chapter_button, self.h_chapter_button),
                           self.checkbox_checked,  self.first_scanner_on)

        self.update = False
        self.make_button("run_button", "Fruit", (self.x_chapter_button, 410, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def checkbox_checked(self):
        if self.timer:
            self.timer.stop()
        self.first_scanner_on = self.checkbox_scanner.isChecked()
        self.shape, self.texture, self.weight = "?", "?", "?"
        self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
        self.pineapple = "?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))

    def paintEvent(self, event):
        super(OutStar, self).paintEvent(event)

        painter = QtGui.QPainter(self.icon3.pixmap())
        pen = QtGui.QPen(QtCore.Qt.white if self.first_scanner_on else QtCore.Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(170 * self.w_ratio, 80 * self.h_ratio, 185 * self.w_ratio, 95 * self.h_ratio)
        painter.drawLine(170 * self.w_ratio, 95 * self.h_ratio, 185 * self.w_ratio, 80 * self.h_ratio)
        pen = QtGui.QPen(QtGui.QColor("black"), 1)
        painter.setPen(pen)
        painter.setFont(QtGui.QFont("times", 12 * (self.w_ratio + self.h_ratio) / 2))
        painter.drawText(QtCore.QPoint(100 * self.w_ratio, 28 * self.h_ratio), "Active" if self.first_scanner_on else "Inactive")

        painter = QtGui.QPainter(self.icon4.pixmap())
        painter.setFont(QtGui.QFont("times", 11 * (self.w_ratio + self.h_ratio) / 2))
        painter.drawText(QtCore.QPoint(120 * self.w_ratio, 30 * self.h_ratio), "1")
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 30 * self.h_ratio), str(self.shape))
        painter.drawText(QtCore.QPoint(120 * self.w_ratio, 60 * self.h_ratio), "1")
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 60 * self.h_ratio), str(self.texture))
        painter.drawText(QtCore.QPoint(120 * self.w_ratio, 90 * self.h_ratio), "1")
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 90 * self.h_ratio), str(self.weight))
        painter.drawText(QtCore.QPoint(115 * self.w_ratio, 120 * self.h_ratio), str(round(self.W2[0, 0], 1)))
        painter.drawText(QtCore.QPoint(115 * self.w_ratio, 150 * self.h_ratio), str(round(self.W2[1, 0], 1)))
        painter.drawText(QtCore.QPoint(115 * self.w_ratio, 175 * self.h_ratio), str(round(self.W2[2, 0], 1)))
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 150 * self.h_ratio), str(self.pineapple))
        if type(self.texture_out) == str:
            painter.drawText(QtCore.QPoint(405 * self.w_ratio, 30 * self.h_ratio), self.texture_out)
        else:
            painter.drawText(QtCore.QPoint(400 * self.w_ratio, 30 * self.h_ratio), str(round(self.shape_out, 2)))
        if type(self.texture_out) == str:
            painter.drawText(QtCore.QPoint(405 * self.w_ratio, 98 * self.h_ratio), self.texture_out)
        else:
            painter.drawText(QtCore.QPoint(400 * self.w_ratio, 98 * self.h_ratio), str(round(self.texture_out, 2)))
        if type(self.texture_out) == str:
            painter.drawText(QtCore.QPoint(405 * self.w_ratio, 170 * self.h_ratio), self.texture_out)
        else:
            painter.drawText(QtCore.QPoint(400 * self.w_ratio, 170 * self.h_ratio), str(round(self.weight_out, 2)))

    def on_run(self):
        if self.update:
            try:
                self.W2 = self.W2 + (0.2 * self.pineapple) * (self.a - self.W2)
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.update = False
                self.run_button.setText("Fruit")
            except Exception as e:
                if str(e) == "can't multiply sequence by non-int of type 'float'":
                    pass
                else:
                    raise e
        else:
            self.timer = QtCore.QTimer()
            self.idx = 0
            self.shape, self.texture, self.weight = "?", "?", "?"
            self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
            self.pineapple = "?"
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.timer.timeout.connect(self.update_label)
            self.timer.start(1000)

    def update_label(self):
        if self.idx == 0:
            if np.random.uniform() > 0.25:
                self.p1, p2, self.fruit = np.array([[-1], [-1], [1]]), 1, "pineapple"
            elif np.random.uniform() > 0.66:
                self.p1, p2, self.fruit = np.array([[-1], [1], [-1]]), 0, "banana"
            elif np.random.uniform() > 0.5:
                self.p1, p2, self.fruit = np.array([[1], [-1], [-1]]), 0, "orange"
            else:
                self.p1, p2, self.fruit = np.array([[1], [1], [-1]]), 0, "apple"
            n = self.W2 * p2
            if self.first_scanner_on:
                n += self.p1
            self.a = np.logical_not(np.logical_or(n < -1, n > 1)) * n + (n > 1) * 1 - (n < -1) * 1
        if self.idx == 1:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_2.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_14.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_20.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 2:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_15.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_21.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 3:
            if self.first_scanner_on:
                self.shape, self.texture, self.weight = self.p1[0, 0], self.p1[1, 0], self.p1[2, 0]
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_15.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_21.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 4:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_16.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_22.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 5:
            self.pineapple = (self.fruit == "pineapple") * 1
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_16.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_22.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 6:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_17.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_23.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 7:
            self.shape_out, self.texture_out, self.weight_out = self.a[0, 0], self.a[1, 0], self.a[2, 0]
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_17.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_23.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 8:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_6.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_12.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_18.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_24.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig2.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 9:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_7.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_13.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_19.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_25.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.run_button.setText("Update")
            self.update = True
        else:
            pass
        self.idx += 1

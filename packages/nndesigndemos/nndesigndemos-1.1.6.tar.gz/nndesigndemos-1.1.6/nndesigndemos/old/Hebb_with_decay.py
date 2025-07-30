from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class HebbWithDecay(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(HebbWithDecay, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Hebb with Decay", 15, "\n\nClick [Fruit] to send a fruit\ndown the belt to be\nrecognized.\n\n"
                                                 "Click [Update] to\napply the Hebb rule.\n\nBecause of weight\n"
                                                 "decay, the weight will\nnever exceed a\nvalue of 2.0.",
                          PACKAGE_PATH + "Logo/Logo_Ch_15.svg", None)

        self.p, self.a, self.label, self.fruit = None, None, None, None
        self.n_temp, self.banana_temp = None, None
        self.timer = None

        self.figure2_w, self.figure2_h = 475, 350
        self.icon4 = QtWidgets.QLabel(self)
        self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon4.setGeometry(28 * self.w_ratio, 100 * self.h_ratio, self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio)

        self.figure_w, self.figure_h = 575, 190
        self.icon3 = QtWidgets.QLabel(self)
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon3.setGeometry(28 * self.w_ratio, 420 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)

        self.W2, self.W1, self.b, self.n = 0.0, 1, -0.5, "  ?"
        self.banana_shape, self.banana_smell, self.banana = "?", "?", "?"

        self.first_scanner_on = True
        self.make_checkbox("checkbox_scanner", "First Scanner", (self.x_chapter_button, 360, self.w_chapter_button, self.h_chapter_button),
                           self.checkbox_checked,  self.first_scanner_on)

        self.update = False
        self.make_button("run_button", "Fruit", (self.x_chapter_button, 400, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def checkbox_checked(self):
        if self.timer:
            self.timer.stop()
        self.first_scanner_on = self.checkbox_scanner.isChecked()
        self.banana_shape, self.banana_smell, self.banana, self.n = "?", "?", "?", "  ?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))

    def paintEvent(self, event):
        super(HebbWithDecay, self).paintEvent(event)

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
        painter.drawText(QtCore.QPoint(120 * self.w_ratio, 58 * self.h_ratio), "1")
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 58 * self.h_ratio), str(self.banana_shape))
        painter.drawText(QtCore.QPoint(115 * self.w_ratio, 155 * self.h_ratio), str(round(self.W2, 1)))
        painter.drawText(QtCore.QPoint(47 * self.w_ratio, 155 * self.h_ratio), str(self.banana_smell))
        painter.drawText(QtCore.QPoint(212 * self.w_ratio, 140 * self.h_ratio), "-0.5")
        painter.drawText(QtCore.QPoint(219 * self.w_ratio, 180 * self.h_ratio), "1")
        try:
            painter.drawText(QtCore.QPoint(268 * self.w_ratio, 100 * self.h_ratio), str(round(self.n, 1)))
        except Exception as e:
            if str(e) == "type str doesn't define __round__ method":
                painter.drawText(QtCore.QPoint(268 * self.w_ratio, 100 * self.h_ratio), str(self.n))
            else:
                raise e
        painter.drawText(QtCore.QPoint(405 * self.w_ratio, 100 * self.h_ratio), str(self.banana))

    def on_run(self):
        if self.update:
            try:
                self.W2 = self.W2 + 0.2 * self.banana - 0.1 * self.W2
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
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
            self.banana_shape, self.banana_smell, self.banana, self.n = "?", "?", "?", "  ?"
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.timer.timeout.connect(self.update_label)
            self.timer.start(900)

    def update_label(self):
        if self.idx == 0:
            if np.random.uniform() > 0.35:
                p1, p2, self.fruit = 1, 1, "banana"
            elif np.random.uniform() > 0.5:
                p1, p2, self.fruit = 0, 0, "orange"
            else:
                p1, p2, self.fruit = 0, 0, "apple"
            self.n_temp = self.W2 * p2 + self.b
            if self.first_scanner_on:
                self.n_temp += self.W1 * p1
            self.banana_temp = self.hardlim(self.n_temp)
            self.label = 1 if self.banana_temp == 1 else -1
        if self.idx == 1:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_2.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 2:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_7.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_6.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 3:
            if self.first_scanner_on:
                self.banana_shape = 1 if self.fruit == "banana" else 0
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_7.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_6.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 4:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 5:
            self.banana_smell = 1 if self.fruit == "banana" else 0
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 6:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_13.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_12.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 7:
            self.n = self.n_temp
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_13.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_12.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 8:
            self.banana = self.banana_temp
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_16.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_15.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_14.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.icon4.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15dfig.svg").pixmap(self.figure2_w * self.w_ratio, self.figure2_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 9:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_19.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                if self.fruit == "orange":
                    self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_18.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                else:
                    self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_17.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.run_button.setText("Update")
            self.update = True
        else:
            pass
        self.idx += 1

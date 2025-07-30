from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
import matplotlib.pyplot as plt
from time import sleep

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class UnsupervisedHebb(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(UnsupervisedHebb, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Unsupervised Hebb", 15, "\n\nClick [Fruit] to send a fruit\ndown the belt to be\nrecognized.\n\n"
                                                   "Click [Update] to\napply the Hebb rule.\n\nWhen the lower weight is\n"
                                                   ">0.5, the network will\nrecognize bananas with\nthe first scanner off.",
                          PACKAGE_PATH + "Logo/Logo_Ch_15.svg", None)

        if self.play_sound:
            self.initial_sound('start_sound1', "Sound/blip.wav")
            self.initial_sound('start_sound2', "Sound/bloop.wav")
            self.initial_sound('wind_sound', "Sound/wind.wav")
            self.initial_sound('knock_sound', "Sound/knock.wav")
            self.initial_sound('blp_sound', "Sound/blp.wav")
            self.initial_sound('scan_sound', "Sound/buzz.wav")

        self.p, self.a, self.label, self.fruit = None, None, None, None
        self.n_temp, self.banana_temp = None, None
        self.timer = None

        self.W2, self.W1, self.b, self.n = 0.0, 1, -0.5, "?"
        self.banana_shape, self.banana_smell, self.banana = "?", "?", "?"

        self.figure2_w, self.figure2_h = 475, 220
        self.make_plot(1, (20, 170, self.figure2_w, self.figure2_h))
        self.figure.subplots_adjust(top=1, bottom=0, left=0, right=1)
        self.axis1 = self.figure.add_subplot(1, 1, 1)
        self.axis1.set_axis_off()

        # Upper left
        rectangle = plt.Rectangle((12, 65), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(12, 85, "Inputs", fontsize=int(8*(self.w_ratio + self.h_ratio) / 2))
        self.axis1.text(0, 67, "Banana\nShape?", fontsize=int(8*(self.w_ratio + self.h_ratio) / 2))
        self.banana_shape_text = self.axis1.text(15, 70, "", fontsize=int(8*(self.w_ratio + self.h_ratio) / 2))

        # Lower left
        rectangle = plt.Rectangle((12, 10), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(0, 12, "Banana\nSmell?", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.banana_smell_text = self.axis1.text(15, 15, "", fontsize=int(8*(self.w_ratio + self.h_ratio) / 2))

        # Upper mid 1
        rectangle = plt.Rectangle((30, 65), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(28, 85, "Weights", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.w1_text = self.axis1.text(33, 70, str(self.W1), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        # Lower mid 1
        rectangle = plt.Rectangle((30, 10), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.w2_text = self.axis1.text(33, 15, str(self.W2), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        # Horizontal connecting lines
        self.axis1.plot(np.arange(20.5, 30, 0.1), [73] * len(np.arange(20.5, 30, 0.1)), color="k")
        self.axis1.plot(np.arange(20.5, 30, 0.1), [18] * len(np.arange(20.5, 30, 0.1)), color="k")

        # Mid 2
        rectangle = plt.Rectangle((48, 37.5), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(51, 37.5 + 5, "$\sum$", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([38.2, 48], [73, 45], color="k")
        self.axis1.plot([38.2, 48], [18, 45], color="k")
        self.axis1.plot([52, 52], [36.5, 28], color="k")
        rectangle = plt.Rectangle((48, 12), 8, 16, fill=False)
        self.axis1.plot([52, 52], [11.9, 7], color="k")
        self.axis1.add_patch(rectangle)
        self.b_text = self.axis1.text(49, 18, str(self.b), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.text(51.2, 0, "1", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([56.1, 61], [45, 45], color="k")

        # Mid 3
        rectangle = plt.Rectangle((61, 37.5), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.plot([69.2, 73.5], [45, 45], color="k")
        self.n_text = self.axis1.text(62, 37.5 + 5, "", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        # Mid 4
        rectangle = plt.Rectangle((73.5, 37.5), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.quiver(81.6, 45.5, 11.8, 0, width=0.005, scale=1, scale_units='xy')
        self.axis1.plot([75.5, 77.5], [40, 40], color="black")
        self.axis1.plot([77.5, 79.5], [40, 40], color="gray", linestyle="dashed", linewidth=0.1)
        self.axis1.plot([77.5, 79.5], [49, 49], color="black")
        self.axis1.plot([77.5, 77.5], [40, 49], color="black")

        # Right
        rectangle = plt.Rectangle((93, 37.5), 8, 16, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(91, 56, "Banana?", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.a_text = self.axis1.text(96, 37.5 + 5, "", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        # In order to set the scale (100, 100)
        line, = self.axis1.plot([0] * 100, range(100))
        line.remove()
        line, = self.axis1.plot(range(100), [0] * 100)
        line.remove()
        self.canvas.draw()

        if self.dpi > 113.5:
            self.figure_w, self.figure_h = round(575 / (self.dpi / 113.5)), round(190 / (self.dpi / 113.5))
        else:
            self.figure_w, self.figure_h = 575, 190
        self.icon3 = QtWidgets.QLabel(self)
        if self.running_on_windows:
            self.icon3.setPixmap(
                QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.h_ratio,
                                                                           self.figure_h * self.h_ratio,
                                                                           QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.dpi > 113.5:
                self.icon3.setGeometry(round(28 * self.h_ratio * (self.dpi / 113.5)), 420 * self.h_ratio,self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setGeometry(round(28 * self.h_ratio * (self.dpi / 113.5)), 420 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)

        else:
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.dpi > 113.5:
                self.icon3.setGeometry(round(28 * self.w_ratio * (self.dpi / 113.5)), 420 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setGeometry(28 * self.w_ratio, 420 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)

        self.first_scanner_on = True
        self.start_demo = True
        self.make_checkbox("checkbox_scanner", "First Scanner", (self.x_chapter_button, 360, self.w_chapter_button, self.h_chapter_button),
                           self.checkbox_checked,  self.first_scanner_on)

        self.update = False
        self.make_button("run_button", "Fruit", (self.x_chapter_button, 400, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def checkbox_checked(self):
        if self.timer:
            self.timer.stop()
        self.first_scanner_on = self.checkbox_scanner.isChecked()
        str_end = "" if self.first_scanner_on else "_x"
        self.banana_shape, self.banana_smell, self.banana, self.n = "?", "?", "?", "  ?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        if not self.start_demo:
            if self.first_scanner_on:
                if self.play_sound:
                    self.start_sound1.play()
            else:
                if self.play_sound:
                    self.start_sound2.play()
        self.start_demo = False

    def paintEvent(self, event):
        super(UnsupervisedHebb, self).paintEvent(event)

        """painter = QtGui.QPainter(self.icon3.pixmap())
        pen = QtGui.QPen(QtCore.Qt.white if self.first_scanner_on else QtCore.Qt.red, 2)
        painter.setPen(pen)
        if self.running_on_windows:
            painter.drawLine(170 * self.h_ratio, 80 * self.h_ratio, 185 * self.h_ratio, 95 * self.h_ratio)
            painter.drawLine(170 * self.h_ratio, 95 * self.h_ratio, 185 * self.h_ratio, 80 * self.h_ratio)
        else:
            painter.drawLine(170 * self.w_ratio, 80 * self.h_ratio, 185 * self.w_ratio, 95 * self.h_ratio)
            painter.drawLine(170 * self.w_ratio, 95 * self.h_ratio, 185 * self.w_ratio, 80 * self.h_ratio)
        pen = QtGui.QPen(QtGui.QColor("black"), 1)
        painter.setPen(pen)
        if self.running_on_windows:
            painter.setFont(QtGui.QFont("times", 12 * (self.h_ratio + self.h_ratio) / 2))
            painter.drawText(QtCore.QPoint(100 * self.h_ratio, 28 * self.h_ratio), "Active" if self.first_scanner_on else "Inactive")
        else:
            painter.setFont(QtGui.QFont("times", 12 * (self.w_ratio + self.h_ratio) / 2))
            painter.drawText(QtCore.QPoint(100 * self.w_ratio, 28 * self.h_ratio), "Active" if self.first_scanner_on else "Inactive")"""

        self.banana_shape_text.remove()
        self.banana_shape_text = self.axis1.text(15, 70, str(self.banana_shape), fontsize=int(8*(self.w_ratio + self.h_ratio) / 2))

        self.banana_smell_text.remove()
        self.banana_smell_text = self.axis1.text(15, 15, str(self.banana_smell), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.w1_text.remove()
        self.w1_text = self.axis1.text(33, 70, str(round(self.W1, 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.w2_text.remove()
        self.w2_text = self.axis1.text(31.5, 15, str(round(self.W2, 2)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.b_text.remove()
        self.b_text = self.axis1.text(49, 18, str(round(self.b, 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.n_text.remove()
        if type(self.n) == str:
            self.n_text = self.axis1.text(63, 37.5 + 5, self.n, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        else:
            self.n_text = self.axis1.text(62 if self.n < 0 else 62.5, 37.5 + 5, str(round(self.n, 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.a_text.remove()
        self.a_text = self.axis1.text(96, 37.5 + 5, str(self.banana), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.canvas.draw()

    def on_run(self):
        str_end = "" if self.first_scanner_on else "_x"
        if self.update:
            try:
                W2_prev = self.W2
                self.W2 += 0.2 * self.banana
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.update = False
                self.run_button.setText("Fruit")
                self.checkbox_scanner.setEnabled(True)
                if W2_prev != self.W2:
                    if self.play_sound:
                        self.knock_sound.play()
                        sleep(0.5)
                        self.blp_sound.play()
            except Exception as e:
                if str(e) == "can't multiply sequence by non-int of type 'float'":
                    pass
                else:
                    raise e
        else:
            self.timer = QtCore.QTimer()
            self.idx = 0
            self.banana_shape, self.banana_smell, self.banana, self.n = "?", "?", "?", "  ?"
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.checkbox_scanner.setEnabled(False)
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
            self.timer.timeout.connect(self.update_label)
            self.timer.start(900)

    def update_label(self):
        str_end = "" if self.first_scanner_on else "_x"
        if self.idx == 0:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        if self.idx == 1:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_4{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_3{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_2{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 2:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_7{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_6{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_5{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 3:
            if self.first_scanner_on:
                self.banana_shape = 1 if self.fruit == "banana" else 0
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_7{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_6{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_5{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.first_scanner_on:
                if self.play_sound:
                    self.scan_sound.play()
        elif self.idx == 4:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_10{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_9{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_8{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 5:
            self.banana_smell = 1 if self.fruit == "banana" else 0
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_10{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_9{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_8{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.scan_sound.play()
        elif self.idx == 6:
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_13{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_12{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_11{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 7:
            self.n = self.n_temp
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_13{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_12{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_11{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 8:
            self.banana = self.banana_temp
            if self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_16{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_15{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_14{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 9:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_19{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                if self.fruit == "orange":
                    self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_18{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                else:
                    self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d1_17{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.run_button.setText("Update")
            self.update = True
            if self.play_sound:
                self.knock_sound.play()
                sleep(0.5)
                self.knock_sound.play()
        else:
            pass
        self.idx += 1

from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
import matplotlib.pyplot as plt
from time import sleep

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

        self.W2, self.W1 = np.zeros((3, 1)), np.eye(3)
        self.p1 = None
        self.shape, self.texture, self.weight = "?", "?", "?"
        self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
        self.pineapple = "?"

        self.figure2_w, self.figure2_h = 495, 370
        self.make_plot(1, (17, 90, self.figure2_w, self.figure2_h))
        self.figure.subplots_adjust(top=1, bottom=0, left=0, right=1)
        self.axis1 = self.figure.add_subplot(1, 1, 1)
        self.axis1.set_axis_off()

        # Left
        # Up
        rectangle = plt.Rectangle((12, 82), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(12, 95, "Inputs", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.text(2, 85, "Shape", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.shape_text = self.axis1.text(15, 86, self.shape, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        # Up Mid
        rectangle = plt.Rectangle((12, 82 - 15), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(0, 85 - 15, "Texture", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.texture_text = self.axis1.text(15, 86 - 15, self.texture, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        # Mid
        rectangle = plt.Rectangle((12, 82 - 15 * 2), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(0, 85 - 15 * 2, "Weight", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.weight_text = self.axis1.text(15, 86 - 15 * 2, self.weight, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        # Down
        rectangle = plt.Rectangle((12, 15), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(2, 27 - 10, " Pine\napple?", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.pineapple_text = self.axis1.text(15, 13 + 15 - 10, self.pineapple, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        # Left Mid
        # Up
        rectangle = plt.Rectangle((30, 82), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(29, 95, "Weights", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.text(33, 86, "1", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot(np.arange(20.3, 30, 0.1), [87] * len(np.arange(20.3, 30, 0.1)), color="k")
        # Up Mid
        rectangle = plt.Rectangle((30, 82 - 15), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(33, 86 - 15, "1", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot(np.arange(20.3, 30, 0.1), [87 - 15] * len(np.arange(20.3, 30, 0.1)), color="k")
        # Up Down
        rectangle = plt.Rectangle((30, 82 - 15 * 2), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(33, 86 - 15 * 2, "1", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot(np.arange(20.3, 30, 0.1), [87 - 15 * 2] * len(np.arange(20.3, 30, 0.1)), color="k")
        # Down Up
        rectangle = plt.Rectangle((30, 30), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.w20_text = self.axis1.text(32, 33, str(round(self.W2[0, 0], 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([20.3, 30], [20, 35], color="k")
        # Down Mid
        rectangle = plt.Rectangle((30, 15), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.w21_text = self.axis1.text(32, 18, str(round(self.W2[1, 0], 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([20.3, 30], [20, 20], color="k")
        # Down Down
        rectangle = plt.Rectangle((30, 0), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.w22_text = self.axis1.text(32, 3, str(round(self.W2[2, 0], 1)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([20.3, 30], [20, 5], color="k")

        # Mid
        # Mid Up
        rectangle = plt.Rectangle((52 + 3, 82), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(54.5 + 3, 86, "$\sum$", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([38.3, 52 + 3], [87, 87], color="k")
        self.axis1.plot([38.3, 52 + 3], [35, 87], color="k")
        # Mid Mid
        rectangle = plt.Rectangle((52 + 3, 40), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(54.5 + 3, 43, "$\sum$", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([38.3, 52 + 3], [82 - 10, 45], color="k")
        self.axis1.plot([38.3, 52 + 3], [20, 45], color="k")
        # Mid Down
        rectangle = plt.Rectangle((52 + 3, 0), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(54.5 + 3, 3, "$\sum$", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.plot([38.3, 52 + 3], [82 - 15 * 2 + 5, 5], color="k")
        self.axis1.plot([38.3, 52 + 3], [5, 5], color="k")

        # Right Mid
        # Up
        rectangle = plt.Rectangle((73.5, 40 + 42), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.plot([75.5, 77], [42 + 42, 42 + 42], color="black")
        self.axis1.plot([78, 79.5], [48 + 42, 48 + 42], color="black")
        self.axis1.plot([77, 78], [42 + 42, 48 + 42], color="black")
        self.axis1.plot([75.5, 79.5], [45 + 42, 45 + 42], color="black", linestyle="dashed", linewidth=0.5)
        self.axis1.plot([63.3, 73.5], [45 + 42, 45 + 42], color="black")
        # Mid
        rectangle = plt.Rectangle((73.5, 40), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.plot([75.5, 77], [42, 42], color="black")
        self.axis1.plot([78, 79.5], [48, 48], color="black")
        self.axis1.plot([77, 78], [42, 48], color="black")
        self.axis1.plot([75.5, 79.5], [45, 45], color="black", linestyle="dashed", linewidth=0.5)
        self.axis1.plot([63.3, 73.5], [45, 45], color="black")
        # Down
        rectangle = plt.Rectangle((73.5, 40 - 40), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.plot([75.5, 77], [42 - 40, 42 - 40], color="black")
        self.axis1.plot([78, 79.5], [48 - 40, 48 - 40], color="black")
        self.axis1.plot([77, 78], [42 - 40, 48 - 40], color="black")
        self.axis1.plot([75.5, 79.5], [45 - 40, 45 - 40], color="black", linestyle="dashed", linewidth=0.5)
        self.axis1.plot([63.3, 73.5], [45 - 40, 45 - 40], color="black")

        # Right
        # Up
        rectangle = plt.Rectangle((93, 40 + 42), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(92, 52 + 42, "Shape", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.shape_out_text = self.axis1.text(96, 37.5 + 6 + 42, self.shape_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.quiver(81.6, 45 + 42, 11.8, 0, width=0.005, scale=1, scale_units='xy')
        # Mid
        rectangle = plt.Rectangle((93, 40), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(92, 52, "Texture", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.texture_out_text = self.axis1.text(96, 37.5 + 6, self.texture_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.quiver(81.6, 45, 11.8, 0, width=0.005, scale=1, scale_units='xy')
        # Down
        rectangle = plt.Rectangle((93, 40 - 40), 8, 10, fill=False)
        self.axis1.add_patch(rectangle)
        self.axis1.text(92, 52 - 40, "Weight", fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.weight_out_text = self.axis1.text(96, 37.5 + 6 - 40, self.weight_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.axis1.quiver(81.6, 45 - 40, 11.8, 0, width=0.005, scale=1, scale_units='xy')

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
                QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.h_ratio,
                                                                           self.figure_h * self.h_ratio,
                                                                           QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.dpi > 113.5:
                self.icon3.setGeometry(round(28 * self.h_ratio * (self.dpi / 113.5)), 470 * self.h_ratio,self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setGeometry(round(28 * self.h_ratio * (self.dpi / 113.5)), 470 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)

        else:
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.dpi > 113.5:
                self.icon3.setGeometry(round(28 * self.w_ratio * (self.dpi / 113.5)), 470 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setGeometry(28 * self.w_ratio, 470 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)

        self.first_scanner_on = True
        self.start_demo = True
        self.make_checkbox("checkbox_scanner", "First Scanner", (self.x_chapter_button, 370, self.w_chapter_button, self.h_chapter_button),
                           self.checkbox_checked,  self.first_scanner_on)

        self.update = False
        self.make_button("run_button", "Fruit", (self.x_chapter_button, 410, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def checkbox_checked(self):
        if self.timer:
            self.timer.stop()
        self.first_scanner_on = self.checkbox_scanner.isChecked()
        str_end = "" if self.first_scanner_on else "_x"
        self.shape, self.texture, self.weight = "?", "?", "?"
        self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
        self.pineapple = "?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        if not self.start_demo:
            if self.first_scanner_on:
                if self.play_sound:
                    self.start_sound1.play()
            else:
                if self.play_sound:
                    self.start_sound2.play()
        self.start_demo = False

    def paintEvent(self, event):
        super(OutStar, self).paintEvent(event)

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

        self.shape_text.remove()
        self.shape_text = self.axis1.text(15, 86, self.shape, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.texture_text.remove()
        self.texture_text = self.axis1.text(15, 86 - 15, self.texture, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.weight_text.remove()
        self.weight_text = self.axis1.text(15, 86 - 15 * 2, self.weight, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.pineapple_text.remove()
        self.pineapple_text = self.axis1.text(15, 13 + 15 - 10, self.pineapple, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.w20_text.remove()
        self.w20_text = self.axis1.text(31.5 if self.W2[0, 0] > 0 else 31, 33, str(round(self.W2[0, 0], 2)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.w21_text.remove()
        self.w21_text = self.axis1.text(31.5 if self.W2[1, 0] > 0 else 31, 18, str(round(self.W2[1, 0], 2)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.w22_text.remove()
        self.w22_text = self.axis1.text(31.5 if self.W2[2, 0] > 0 else 31, 3, str(round(self.W2[2, 0], 2)), fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.shape_out_text.remove()
        if type(self.shape_out) == str:
            self.shape_out_text = self.axis1.text(96, 37.5 + 6 + 42, self.shape_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        else:
            self.shape_out_text = self.axis1.text(95 if self.shape_out >= 0 else 94.5, 37.5 + 6 + 42, self.shape_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.texture_out_text.remove()
        if type(self.texture_out) == str:
            self.texture_out_text = self.axis1.text(96, 37.5 + 6, self.texture_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        else:
            self.texture_out_text = self.axis1.text(95 if self.texture_out >= 0 else 94.5, 37.5 + 6, self.texture_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        self.weight_out_text.remove()
        if type(self.weight_out) == str:
            self.weight_out_text = self.axis1.text(96, 37.5 + 6 - 40, self.weight_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))
        else:
            self.weight_out_text = self.axis1.text(95 if self.weight_out >= 0 else 94.5, 37.5 + 6 - 40, self.weight_out, fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2))

        self.canvas.draw()

    def on_run(self):
        str_end = "" if self.first_scanner_on else "_x"
        if self.update:
            try:
                W2_prev = np.copy(self.W2)
                self.W2 = self.W2 + (0.2 * self.pineapple) * (self.a - self.W2)
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.update = False
                self.run_button.setText("Fruit")
                self.checkbox_scanner.setEnabled(True)
                if W2_prev[0, 0] != self.W2[0, 0] or W2_prev[1, 0] != self.W2[1, 0] or W2_prev[2, 0] != self.W2[2, 0]:
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
            self.shape, self.texture, self.weight = "?", "?", "?"
            self.shape_out, self.texture_out, self.weight_out = "?", "?", "?"
            self.pineapple = "?"
            self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_1{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.checkbox_scanner.setEnabled(False)
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
            self.timer.timeout.connect(self.update_label)
            self.timer.start(1000)

    def update_label(self):
        str_end = "" if self.first_scanner_on else "_x"
        if self.idx == 0:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        if self.idx == 1:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_2{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_8{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_14{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_20{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 2:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_3{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_9{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_15{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_21{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 3:
            if self.first_scanner_on:
                self.shape, self.texture, self.weight = self.p1[0, 0], self.p1[1, 0], self.p1[2, 0]
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_3{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_9{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_15{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_21{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.first_scanner_on:
                if self.play_sound:
                    self.scan_sound.play()
        elif self.idx == 4:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_4{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_10{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_16{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_22{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 5:
            self.pineapple = (self.fruit == "pineapple") * 1
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_4{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_10{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_16{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_22{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.scan_sound.play()
        elif self.idx == 6:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_5{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_11{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_17{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_23{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 7:
            self.shape_out, self.texture_out, self.weight_out = self.a[0, 0], self.a[1, 0], self.a[2, 0]
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_5{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_11{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_17{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_23{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 8:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_6{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_12{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_18{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_24{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 9:
            if self.fruit == "apple":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_7{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "banana":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_13{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            elif self.fruit == "orange":
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_19{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd15d2_25{}.svg".format(str_end)).pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.run_button.setText("Update")
            self.update = True
            if self.play_sound:
                self.knock_sound.play()
                sleep(0.5)
                self.knock_sound.play()
        else:
            pass
        self.idx += 1

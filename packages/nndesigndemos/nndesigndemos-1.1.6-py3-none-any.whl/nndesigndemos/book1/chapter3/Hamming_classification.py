from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
from time import sleep

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class HammingClassification(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(HammingClassification, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Hamming Classification", 3, "Click [Go] to send a fruit\ndown the belt to be\nclassified"
                          " by a Hamming\nnetwork.\n\nThe calculations for the\nHamming network will\nappear below.",
                          PACKAGE_PATH + "Logo/Logo_Ch_3.svg", None)

        if self.play_sound:
            self.initial_sound('start_sound1', "Sound/blip.wav")
            self.initial_sound('start_sound2', "Sound/bloop.wav")
            self.initial_sound('wind_sound', "Sound/wind.wav")
            self.initial_sound('knock_sound', "Sound/knock.wav")
            self.initial_sound('scan_sound', "Sound/buzz.wav")
            self.initial_sound('classify_sound', "Sound/classify.wav")

        self.make_plot(1, (15, 100, 500, 390))
        self.axis = self.figure.add_subplot(projection='3d')
        ys = np.linspace(-1, 1, 100)
        zs = np.linspace(-1, 1, 100)
        Y, Z = np.meshgrid(ys, zs)
        X = 0
        apple = np.array([-1, 1, -1])
        orange = np.array([1, 1, -1])
        self.axis.set_title("Input Space")
        self.axis.plot_surface(X, Y, Z, alpha=0.5)
        self.axis.set_xlabel("texture")
        self.axis.set_xticks([-1, 1])
        self.axis.set_ylabel("shape")
        self.axis.set_yticks([-1, 1])
        self.axis.set_zlabel("weight")
        self.axis.zaxis._axinfo['label']['space_factor'] = 0.1
        self.axis.set_zticks([-1, 1])
        self.axis.scatter(orange[0], orange[1], orange[2], color='green')
        self.axis.scatter(apple[0], apple[1], apple[2], color='orange')
        self.line1, self.line2, self.line3 = None, None, None
        self.axis.view_init(10, 110)
        self.canvas.draw()

        self.p, self.a1, self.a2, self.fruit, self.label = None, None, None, None, None

        self.make_label("label_w1", "W1 = [1 -1 -1; 1, 1, -1]", (550, 310, 150, 25))
        self.make_label("label_b", "b = [3; 3]", (550, 340, 150, 25))
        self.make_label("label_w2", "W2 = [1 -0.5; -0.5, 1]", (550, 370, 150, 25))
        self.make_label("label_p", "", (550, 400, 150, 25))
        self.make_label("label_a_11", "", (550, 430, 150, 25))
        self.make_label("label_a_12", "", (550, 460, 150, 25))
        self.make_label("label_a_21", "", (550, 490, 150, 25))
        self.make_label("label_a_22", "", (550, 520, 150, 25))
        self.make_label("label_fruit", "", (550, 550, 150, 25))

        if self.dpi > 113.5:
            self.figure_w, self.figure_h = round(575 / (self.dpi / 113.5)), round(190 / (self.dpi / 113.5))
        else:
            self.figure_w, self.figure_h = 575, 190
        self.icon3 = QtWidgets.QLabel(self)
        if self.running_on_windows:
            if self.dpi > 113.5:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.h_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon3.setGeometry(round(28 * self.h_ratio * (self.dpi / 113.5)), 485 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.h_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon3.setGeometry(28 * self.h_ratio, 485 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
        else:
            if self.dpi > 113.5:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(round(self.figure_w * self.w_ratio / (self.dpi / 113.5)), round(self.figure_h * self.h_ratio / (self.dpi / 113.5)), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon3.setGeometry(round(28 * self.w_ratio * (self.dpi / 113.5)), 485 * self.h_ratio, round(self.figure_w * self.w_ratio / (self.dpi / 113.5)), round(self.figure_h * self.h_ratio / (self.dpi / 113.5)))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
                self.icon3.setGeometry(28 * self.w_ratio, 485 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)
        self.text_shape, self.text_texture, self.text_weight = "?", "?", "?"

        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.make_button("run_button", "Go", (self.x_chapter_button, 577, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def paintEvent(self, event):
        super(HammingClassification, self).paintEvent(event)
        pixmap = self.icon3.pixmap()
        painter = QtGui.QPainter(pixmap)
        if self.running_on_windows:
            w_ratio, h_ratio = self.h_ratio, self.h_ratio
        else:
            w_ratio, h_ratio = self.w_ratio, self.h_ratio
        if self.dpi > 113.5:
            w_ratio = round(w_ratio / (self.dpi / 113.5))
            h_ratio = round(h_ratio / (self.dpi / 113.5))
        painter.setFont(QtGui.QFont("times", 12 * (w_ratio + h_ratio) // 2))
        painter.drawText(QtCore.QPoint(100 * w_ratio, 26 * h_ratio), self.text_shape)
        painter.drawText(QtCore.QPoint(230 * w_ratio, 26 * h_ratio), self.text_texture)
        painter.drawText(QtCore.QPoint(360 * w_ratio, 26 * h_ratio), self.text_weight)
        painter.end()
        self.icon3.setPixmap(pixmap)

    def on_run(self):
        self.timer = QtCore.QTimer()
        self.idx = 0
        self.text_shape, self.text_texture, self.text_weight = "?", "?", "?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.label_p.setText("")
        self.label_a_11.setText("")
        self.label_a_12.setText("")
        self.label_a_21.setText("")
        self.label_a_22.setText("")
        self.label_fruit.setText("")
        self.p = np.round(np.random.uniform(-1, 1, (1, 3)), 2)
        w1, w2 = np.array([[1, -1, -1], [1, 1, -1]]), np.array([[1, -0.5], [-0.5, 1]])
        self.a1 = np.round(np.dot(w1, self.p.T), 2)
        self.a2 = np.round(np.dot(w2, self.a1), 2)
        self.a2 = np.round(np.array([[self.poslin(self.a2[0, 0])], [self.poslin(self.a2[1, 0])]]), 2)
        self.fruit = "Orange" if self.a2[0, 0] > 0 else "Apple"
        self.label = 1 if self.fruit == "Apple" else 0
        if self.line1:
            self.line1.pop().remove()
            self.line2.pop().remove()
            self.line3.pop().remove()
            self.canvas.draw()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1100)

    def update_label(self):
        if self.idx == 0:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        if self.idx == 1:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 2:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_2.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_7.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 3:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        elif self.idx == 4:
            self.text_shape, self.text_texture, self.text_weight = str(self.p[0, 0]), str(self.p[0, 1]), str(self.p[0, 2])
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.scan_sound.play()
        elif self.idx == 5:
            self.line1 = self.axis.plot3D([self.p[0, 0]] * 10, np.linspace(-1, 1, 10), [self.p[0, 2]] * 10, color="g")
            self.line2 = self.axis.plot3D([self.p[0, 0]] * 10, [self.p[0, 1]] * 10, np.linspace(-1, 1, 10), color="g")
            self.line3 = self.axis.plot3D(np.linspace(-1, 1, 10), [self.p[0, 1]] * 10, [self.p[0, 2]] * 10, color="g")
            self.canvas.draw()
            if self.play_sound:
                self.classify_sound.play()
        elif self.idx == 6:
            self.label_p.setText("p = [{} {} {}]".format(self.p[0, 0], self.p[0, 1], self.p[0, 2]))
        elif self.idx == 7:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            self.label_a_11.setText("a1 = purelin(W1 * p + b)")
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 8:
            self.label_a_12.setText("a1 = [{} {}]".format(self.a1[0, 0], self.a1[1, 0]))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 9:
            self.label_a_21.setText("a2 = poslin(W2 * a1)")
        elif self.idx == 10:
            self.label_a_22.setText("a2 = [{} {}]".format(self.a2[0, 0], self.a2[1, 0]))
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 11:
            self.label_fruit.setText("Fruit = {}".format(self.fruit))
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_6.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.knock_sound.play()
                sleep(0.5)
                self.knock_sound.play()
        else:
            pass
        self.idx += 1

    @staticmethod
    def poslin(x):
        return x if x >= 0 else 0

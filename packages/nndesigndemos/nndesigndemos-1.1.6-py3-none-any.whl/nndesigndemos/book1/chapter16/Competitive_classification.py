from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
from time import sleep

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class CompetitiveClassification(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(CompetitiveClassification, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Competitive Classification", 16, "Click [Go] to send a fruit\ndown the belt to be\nclassified"
                          " by the\ncompetitive layer.\n\nThe calculations for the\nlayer will appear\nbelow.",
                          PACKAGE_PATH + "Logo/Logo_Ch_16.svg", None, description_coords=(535, 90, 450, 250))

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

        self.p, self.n, self.a, self.label = None, None, None, None
        self.W = np.array([[1, -1, -1], [1, 1, -1]])

        self.make_label("label_w", "W = [1 -1 -1; 1 1 -1]", (550, 300, 150, 25))
        self.make_label("label_p", "", (550, 330, 150, 25))
        self.make_label("label_n_1", "", (550, 360, 150, 25))
        self.make_label("label_n_2", "", (550, 390, 150, 25))
        self.make_label("label_a_1", "", (550, 420, 150, 25))
        self.make_label("label_a_2", "", (550, 450, 150, 25))
        self.make_label("label_fruit", "", (550, 480, 150, 25))

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

        self.run_button = QtWidgets.QPushButton("Go", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 520 * self.h_ratio, self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.on_run)

    def paintEvent(self, event):
        super(CompetitiveClassification, self).paintEvent(event)
        pixmap = self.icon3.pixmap()
        painter = QtGui.QPainter(pixmap)
        if self.running_on_windows:
            w_ratio, h_ratio = self.h_ratio, self.h_ratio
        else:
            w_ratio, h_ratio = self.w_ratio, self.h_ratio
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
        self.label_n_1.setText("");
        self.label_n_2.setText("")
        self.label_a_1.setText("");
        self.label_a_2.setText("")
        self.label_fruit.setText("")
        self.p = np.round(np.random.uniform(-1, 1, (3, 1)), 2)
        self.n = np.dot(self.W, self.p)
        self.a = self.compet(self.n)
        self.label = 1 if self.a[0] == 0 else 0
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
        if self.idx == 2:
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
            self.text_shape, self.text_texture, self.text_weight = str(self.p[0, 0]), str(self.p[1, 0]), str(self.p[2, 0])
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.scan_sound.play()
        elif self.idx == 5:
            self.line1 = self.axis.plot3D([self.p[1, 0]] * 10, np.linspace(-1, 1, 10), [self.p[2, 0]] * 10, color="g")
            self.line2 = self.axis.plot3D([self.p[1, 0]] * 10, [self.p[0, 0]] * 10, np.linspace(-1, 1, 10), color="g")
            self.line3 = self.axis.plot3D(np.linspace(-1, 1, 10), [self.p[0, 0]] * 10, [self.p[2, 0]] * 10, color="g")
            self.canvas.draw()
            if self.play_sound:
                self.classify_sound.play()
        elif self.idx == 6:
            self.label_p.setText("p = [{}; {}; {}]".format(self.p[0, 0], self.p[1, 0], self.p[2, 0]))
        elif self.idx == 7:
            self.label_n_1.setText("n = W * p")
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 8:
            self.label_n_2.setText("n = [{}; {}]".format(round(self.n[0, 0], 2), round(self.n[1, 0], 2)))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 9:
            self.label_a_1.setText("a = compet(n)")
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 10:
            self.label_a_2.setText("a = [{}; {}]".format(round(self.a[0, 0], 1), round(self.a[1, 0], 1)))
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 11:
            self.label_fruit.setText("Fruit = {}".format("Apple" if self.label == 1 else "Orange"))
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

from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class BackpropagationCalculation(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(BackpropagationCalculation, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Backpropagation Calculation", 11, " TODO",
                          PACKAGE_PATH + "Chapters/2/Logo_Ch_2.svg", PACKAGE_PATH + "Chapters/2/nn2d1.svg", show_pic=False)

        self.random_state = 42
        self.p, self.t, self.a1, self.a2, self.e, self.s2, self.s1 = 1, None, None, None, None, None, None
        self.W1, self.b1, self.W2, self.b2 = None, None, None, None

        # TODO: Figure and parameter values

        self.label_p = QtWidgets.QLabel(self)  # TODO: Input box
        self.label_p.setText("p =")
        self.label_p.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_p.setGeometry(300 * self.w_ratio, 300 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.p_box = QtWidgets.QLineEdit()
        self.p_box.setText("1")
        self.p_box.setGeometry(315 * self.w_ratio, 260 * self.h_ratio, 50 * self.w_ratio, 100 * self.h_ratio)
        self.wid3 = QtWidgets.QWidget(self)
        self.layout3 = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        self.wid3.setGeometry(315 * self.w_ratio, 260 * self.h_ratio, 50 * self.w_ratio, 100 * self.h_ratio)
        self.layout3.addWidget(self.p_box)
        self.wid3.setLayout(self.layout3)

        self.label_t = QtWidgets.QLabel(self)
        self.label_t.setText("")
        self.label_t.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_t.setGeometry(300 * self.w_ratio, 330 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_a1 = QtWidgets.QLabel(self)
        self.label_a1.setText("")
        self.label_a1.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_a1.setGeometry(300 * self.w_ratio, 360 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_a2 = QtWidgets.QLabel(self)
        self.label_a2.setText("")
        self.label_a2.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_a2.setGeometry(300 * self.w_ratio, 390 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_e = QtWidgets.QLabel(self)
        self.label_e.setText("")
        self.label_e.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_e.setGeometry(300 * self.w_ratio, 420 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_s2 = QtWidgets.QLabel(self)
        self.label_s2.setText("")
        self.label_s2.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_s2.setGeometry(300 * self.w_ratio, 450 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_s1 = QtWidgets.QLabel(self)
        self.label_s1.setText("")
        self.label_s1.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_s1.setGeometry(250 * self.w_ratio, 480 * self.h_ratio, 250 * self.w_ratio, 25 * self.h_ratio)

        self.label_W1 = QtWidgets.QLabel(self)
        self.label_W1.setText("")
        self.label_W1.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_W1.setGeometry(300 * self.w_ratio, 510 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_b1 = QtWidgets.QLabel(self)
        self.label_b1.setText("")
        self.label_b1.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_b1.setGeometry(300 * self.w_ratio, 540 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_W2 = QtWidgets.QLabel(self)
        self.label_W2.setText("")
        self.label_W2.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_W2.setGeometry(300 * self.w_ratio, 570 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.label_b2 = QtWidgets.QLabel(self)
        self.label_b2.setText("")
        self.label_b2.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        self.label_b2.setGeometry(300 * self.w_ratio, 600 * self.h_ratio, 200 * self.w_ratio, 25 * self.h_ratio)

        self.run_button = QtWidgets.QPushButton("Go", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 420 * self.h_ratio, self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.on_run)

        self.run_button = QtWidgets.QPushButton("Reset", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 450 * self.h_ratio,
                                    self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.reset)

        self.run_button = QtWidgets.QPushButton("Random", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 500 * self.h_ratio,
                                    self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.init_params)

        self.reset()

    def on_run(self):
        self.timer = QtCore.QTimer()
        self.idx = 0
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)

    def reset(self):
        self.W1, self.b1 = np.array([[-0.27], [-0.41]]), np.array([[-0.48], [-0.13]])
        self.W2, self.b2 = np.array([[0.09, -0.17]]), np.array([[0.48]])

        # self.label_p.setText("p = 1");
        self.p_box.setText("1")
        self.label_t.setText("t = ?");
        self.label_a1.setText("a1 = ?");
        self.label_a2.setText("a2 = ?")
        self.label_e.setText("e = ?");
        self.label_s2.setText("s2 = ?");
        self.label_s1.setText("s1 = ?")
        self.label_W1.setText("W1 = ?");
        self.label_b1.setText("b1 = ?");
        self.label_W2.setText("W2 = ?");
        self.label_b2.setText("b2 = ?")

    def init_params(self):
        np.random.seed(self.random_state)
        self.W1 = np.random.uniform(-0.5, 0.5, (2, 1))
        self.b1 = np.random.uniform(-0.5, 0.5, (2, 1))
        self.W2 = np.random.uniform(-0.5, 0.5, (1, 2))
        self.b2 = np.random.uniform(-0.5, 0.5, (1, 1))

    def update_label(self):
        alpha = 0.1
        if self.idx == 0:
            self.label_t.setText("t = ?")
            self.label_a1.setText("a1 = ?"); self.label_a2.setText("a2 = ?")
            self.label_e.setText("e = ?"); self.label_s2.setText("s2 = ?"); self.label_s1.setText("s1 = ?")
            self.label_W1.setText("W1 = ?"); self.label_b1.setText("b1 = ?")
            self.label_W2.setText("W2 = ?"); self.label_b2.setText("b2 = ?")
            self.p = float(self.p_box.text())
            self.t = 1 + np.sin(self.p * np.pi / 4)
            n1 = np.dot(self.W1, self.p) + self.b1
            self.a1 = self.logsigmoid(n1)
            n2 = np.dot(self.W2, self.a1) + self.b2
            self.a2 = self.purelin(n2)
            self.e = self.t - self.a2
            F2_der = np.diag(self.purelin_der(n2).reshape(-1))
            self.s2 = -2 * np.dot(F2_der, self.e)
            F1_der = np.diag(self.logsigmoid_der(n1).reshape(-1))
            self.s1 = np.dot(F1_der, np.dot(self.W2.T, self.s2))
            self.W1 += -alpha * np.dot(self.s1, self.p)
            self.b1 += -alpha * self.s1
            # Output Layer
            self.W2 += -alpha * np.dot(self.s2, self.a1.T)
            self.b2 += -alpha * self.s2
        if self.idx == 1:
            self.label_t.setText("t = 1 + sin(p * pi / 4) = {}".format(round(self.t, 2)))
        elif self.idx == 2:
            self.label_a1.setText("a1 = logsig(W1 * p + b1) = [{}; {}]".format(round(self.a1[0, 0], 2), round(self.a1[1, 0], 2)))
        elif self.idx == 3:
            self.label_a2.setText("a2 = purelin(W2 * a1 + b2) = {}".format(round(self.a2[0, 0], 2)))
        elif self.idx == 4:
            self.label_e.setText("e = t - a2 = {}".format(round(self.e[0, 0], 2)))
        elif self.idx == 5:
            self.label_s2.setText("s2 = -2 * dpurelin(n2) / dn2 * e = {}".format(round(self.s2[0, 0], 2)))
        elif self.idx == 6:
            self.label_s1.setText("s1 = dlogsig(n1) / dn1 * W2' * s2 = [{}; {}]".format(round(self.s1[0, 0], 2), round(self.s1[1, 0], 2)))
        elif self.idx == 7:
            self.label_W1.setText("W1 = W1 - lr * s1 * p' = [{}; {}]".format(round(self.W1[0, 0], 2), round(self.W1[1, 0], 2)))
            self.label_b1.setText("b1 = b1 - lr * s1 = [{}; {}]".format(round(self.b1[0, 0], 2), round(self.b1[1, 0]), 2))
            self.label_W2.setText("W2 = W2 - lr * s2 * a1' = [{}; {}]".format(round(self.W2[0, 0], 2), round(self.W2[0, 1], 2)))
            self.label_b2.setText("b2 = b2 - lr * s2 = {}".format(round(self.b2[0, 0], 2)))
        else:
            pass
        self.idx += 1

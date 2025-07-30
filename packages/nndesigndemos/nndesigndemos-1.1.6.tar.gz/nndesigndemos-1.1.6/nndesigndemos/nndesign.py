import os
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QApplication

from nndesigndemos.nndesign_layout import NNDLayout, open_link
from nndesigndemos.Window import MainWindowNN, MainWindowDL
from nndesigndemos.get_package_path import PACKAGE_PATH


class MainWindow(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        """ Window that shows the main menu, to choose between the two books """
        super(MainWindow, self).__init__(w_ratio, h_ratio, dpi, chapter_window=False, draw_vertical=False)

        # Coordinates (in px)
        x_title, y_title, w_title, h_title, add_x, add_y = 30, 5, 500, 100, 250, 20
        x_left, y_img, w, h_img, x_right = 20, 110, 230, 284, 20 + 260
        y_button, h_button = 415, 50
        y_text, h_text = 435, 200
        x_authors, y_authors, w_authors, h_authors = 290, 650, 300, 20

        self.setWindowTitle("Neural Network Design & Deep Learning Demos")

        self.make_label("label1", "Neural Network", (x_title, y_title, w_title, h_title), font_size=18, italics=True)
        self.make_label("label2", "DESIGN", (x_title, y_title + add_y, w_title, h_title), font_size=18)

        self.make_label("label3", "Neural Network", (x_title + add_x, y_title, w_title, h_title), font_size=18, italics=True)
        self.make_label("label4", "DESIGN: DEEP LEARNING", (x_title + add_x, y_title + add_y, w_title, h_title), font_size=18)

        self.make_label("label5", "By Amir Jafari, Martin Hagan, Xiao Qi", (x_authors, y_authors, w_authors, h_authors))

        # self.statusBar()
        # self.main_menu = self.menuBar()

        self.show_image("icon1", PACKAGE_PATH + "Logo/Figure.jpg", (x_left, y_img, w, h_img))

        self.show_image("icon2", PACKAGE_PATH + "Logo/Figure_DL.jpg", (x_right, y_img, w, h_img))

        # Not sure why this doesn't work
        # self.make_button(
        #     "button1", "Neural Network Design", (20, 4150, 230, 50), self.new_window1,
        #     "background-color: rgb(125, 150, 255);\nborder:3px solid rgb(100, 170, 255);\nfont-size:{}px".format(
        #         str(int(13 * (self.w_ratio + self.h_ratio) / 2))
        #     )
        # )
        # self.button1.setFont(QtGui.QFont("Times New Roman", 12, QtGui.QFont.Bold))

        self.make_label("book1_info", "Click on the button above to access the\ndemonstrations for the Neural Network\n"
                                      "Design book.\n\nEach demo is linked to a chapter section\nof the book. You can "
                                      "find more info at", (x_left, y_text, w, h_text))
        self.make_label("book1_link", '<a href="https://hagan.okstate.edu/nnd.html">https://hagan.okstate.edu/nnd.html/</a>', (x_left, y_text + 145, w, 30))
        self.book1_link.linkActivated.connect(open_link)

        self.make_label("book2_info", "Click on the button above to access the\ndemonstrations for the Neural Network\n"
                        "Design: Deep Learning book.\n\nEach demo is linked to a chapter section\nof the book. You can "
                        "find more info at", (x_right, y_text, w, h_text))
        self.make_label(
            "book2_link",
            '<a href="https://github.com/NNDesignDeepLearning">https://github.com/NNDesignDeepLearning</a>',
            (x_right, y_text + 145, w, 30),
            font_size=13,
        )
        self.book2_link.linkActivated.connect(open_link)

        self.button1 = QtWidgets.QPushButton("Neural Network Design", self)
        self.button1.setGeometry(x_left * self.w_ratio, y_button * self.h_ratio, w * self.w_ratio, h_button * self.h_ratio)
        self.button1.setFont(QtGui.QFont("Times New Roman", 12, QtGui.QFont.Weight.Bold.value))
        self.button1.clicked.connect(self.new_window1)
        self.button1.setStyleSheet("background-color: rgb(88, 157, 212);\nborder:3px solid rgb(88, 157, 212);"
                                   "\nfont-size:{}px".format(str(int(13 * (self.w_ratio + self.h_ratio) / 2))))
        self.button1_win = None

        self.button2 = QtWidgets.QPushButton("Neural Network Design: Deep Learning", self)
        self.button2.setGeometry(x_right * self.w_ratio, y_button * self.h_ratio, w * self.w_ratio, h_button * self.h_ratio)
        self.button2.setFont(QtGui.QFont("Times New Roman", 12, QtGui.QFont.Weight.Bold.value))
        self.button2.clicked.connect(self.new_window2)
        self.button2.setStyleSheet("background-color: rgb(147, 197, 209);\nborder:3px solid rgb(147, 197, 209);"
                                   "\nfont-size:{}px;\ncolor: white;".format(str(int(13 * (self.w_ratio + self.h_ratio) / 2))))
        self.button2_win = None

    def new_window1(self):
        self.button1_win = MainWindowNN(self.w_ratio, self.h_ratio, self.dpi)
        self.button1_win.show()

    def new_window2(self):
        self.button2_win = MainWindowDL(self.w_ratio, self.h_ratio, self.dpi)
        self.button2_win.show()


def nndtoc(play_sound=True):
    os.environ["NNDESIGNDEMOS_PLAY_SOUND"] = "1" if play_sound else "0"
    import sys
    # QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    dimensions = app.primaryScreen().geometry()
    w_screen, h_screen = dimensions.width(), dimensions.height()
    w_ratio, h_ratio = w_screen / 1000, h_screen / 800
    dpi = round(app.screens()[0].physicalDotsPerInch(), 1)
    win = MainWindow(int(w_ratio), int(h_ratio), int(dpi))
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    nndtoc()

from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.pyplot as plt

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class PatternClassification(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PatternClassification, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("RBF Pattern Classification", 17, "\nAlter the network's\nparameters by dragging\nthe slide bars.\n\n"
                                                            "Click on [Random]/[Reset]\nto set each parameter\nto a random/original value.\n\n"
                                                            "You can rotate the 3D plots\nby clicking and dragging\n"
                                                            "in the plot window.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", PACKAGE_PATH + "Figures/nnd17_1.svg",
                          icon_move_left=120, icon_coords=(130, 150, 500, 200), description_coords=(535, 90, 450, 300))

        # self.label_eq = QtWidgets.QLabel(self)
        # self.label_eq.setText("a = purelin(w2 * tansig(w1 * p + b1) + b2))")
        # self.label_eq.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        # self.label_eq.setGeometry(180 * self.w_ratio, 270 * self.h_ratio, (self.w_chapter_slider + 100) * self.w_ratio, 50 * self.h_ratio)

        p1, p2 = np.arange(-5, 5, 0.05), np.arange(-5, 5, 0.05)
        self.pp1, self.pp2 = np.meshgrid(p1, p2)

        self.make_plot(1, (5, 400, 260, 260))
        self.make_plot(2, (255, 400, 260, 260))
        self.figure2.subplots_adjust(left=0.15, bottom=0.175, right=0.95)

        self.axis3d = self.figure.add_subplot(projection='3d')
        self.axis3d.set_xlim(-5, 5)
        self.axis3d.set_ylim(-5, 5)
        self.axis3d.set_zlim(-2, 1)
        self.axis3d.set_xlabel("$p1$")
        self.axis3d.set_ylabel("$p2$")
        self.axis3d.set_zlabel("$a$")

        x_0_surf, y_0_surf = np.linspace(-5, 5, 100), np.linspace(-5, 5, 100)
        xx_0_surf, yy_0_surf = np.meshgrid(x_0_surf, y_0_surf)
        self.axis3d.plot_surface(xx_0_surf, yy_0_surf, np.zeros((100, 100)), color="gray", alpha=0.5)
        self.axis3d.set_xticks([-5, 0, 5])
        self.axis3d.set_yticks([-5, 0, 5])
        self.axis3d.set_zticks([-2, -1, 0, 1])
        self.axis3d.set_xlabel("$p1$")
        self.axis3d.set_ylabel("$p2$")

        self.axis = self.figure2.add_subplot(1, 1, 1)
        self.axis.scatter([1, -1], [1, -1], marker="*")
        self.axis.scatter([1, -1], [-1, 1], marker="o")
        self.axis.set_xticks([-5, 0, 5])
        self.axis.set_yticks([-5, 0, 5])

        self.axis.set_xlabel("$p1$")
        self.axis.set_ylabel("$p2$")

        self.make_slider("slider_w1_1", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (10, 115, 150, 50), self.graph, "label_w1_1", "W1(1,1)", (50, 115 - 25, 100, 50))
        self.slider_w1_1.valueChanged.connect(self.slider_update)
        self.slider_w1_1.sliderPressed.connect(self.slider_disconnect)
        self.slider_w1_1.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_w1_2", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 1, -10,
                         (10, 360, 150, 50), self.graph, "label_w1_2", "W1(2,1)", (50, 360 - 25, 100, 50))
        self.slider_w1_2.valueChanged.connect(self.slider_update)
        self.slider_w1_2.sliderPressed.connect(self.slider_disconnect)
        self.slider_w1_2.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_b1_1", QtCore.Qt.Orientation.Horizontal, (-10, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (170, 115, 150, 50), self.graph, "label_b1_1", "b1(1):", (210, 115 - 25, 100, 50))
        self.slider_b1_1.valueChanged.connect(self.slider_update)
        self.slider_b1_1.sliderPressed.connect(self.slider_disconnect)
        self.slider_b1_1.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_b1_2", QtCore.Qt.Orientation.Horizontal, (-10, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (170, 360, 150, 50), self.graph, "label_b1_2", "b1(2):", (210, 360 - 25, 100, 50))
        self.slider_b1_2.valueChanged.connect(self.slider_update)
        self.slider_b1_2.sliderPressed.connect(self.slider_disconnect)
        self.slider_b1_2.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_w2_1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 20,
                         (330, 115, 150, 50), self.graph, "label_w2_1", "W2(1,1):", (370, 115 - 25, 100, 50))
        self.slider_w2_1.valueChanged.connect(self.slider_update)
        self.slider_w2_1.sliderPressed.connect(self.slider_disconnect)
        self.slider_w2_1.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_w2_2", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 20,
                         (330, 360, 150, 50), self.graph, "label_w2_2", "W2(1,2):", (370, 360 - 25, 100, 50))
        self.slider_w2_2.valueChanged.connect(self.slider_update)
        self.slider_w2_2.sliderPressed.connect(self.slider_disconnect)
        self.slider_w2_2.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_b2", QtCore.Qt.Orientation.Horizontal, (-10, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, -10,
                         (self.x_chapter_usual, 380, self.w_chapter_slider, 50), self.graph, "label_b2", "b2: -1.0")
        self.slider_b2.valueChanged.connect(self.slider_update)
        self.slider_b2.sliderPressed.connect(self.slider_disconnect)
        self.slider_b2.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_w1_12", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 1, -10,
                         (self.x_chapter_usual, 450, self.w_chapter_slider, 50), self.graph, "label_w1_12", "W1(1,2): 1")
        self.slider_w1_12.valueChanged.connect(self.slider_update)
        self.slider_w1_12.sliderPressed.connect(self.slider_disconnect)
        self.slider_w1_12.sliderReleased.connect(self.slider_reconnect)

        self.make_slider("slider_w1_22", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (self.x_chapter_usual, 520, self.w_chapter_slider, 50), self.graph, "label_w1_22", "W1(2,2): 1")
        self.slider_w1_22.valueChanged.connect(self.slider_update)
        self.slider_w1_22.sliderPressed.connect(self.slider_disconnect)
        self.slider_w1_22.sliderReleased.connect(self.slider_reconnect)

        self.weight1_1 = self.slider_w1_1.value() / 10
        self.weight1_2 = self.slider_w1_2.value() / 10
        self.bias1_1 = self.slider_b1_1.value() / 10
        self.bias1_2 = self.slider_b1_2.value() / 10
        self.weight2_1 = self.slider_w2_1.value() / 10
        self.weight2_2 = self.slider_w2_2.value() / 10
        self.bias2 = self.slider_b2.value() / 10
        self.weight1_12 = self.slider_w1_12.value() / 10
        self.weight1_22 = self.slider_w1_22.value() / 10

        self.make_button("random_button", "Random", (self.x_chapter_button, 580, self.w_chapter_button, self.h_chapter_button), self.on_random)
        self.make_button("random_button", "Reset", (self.x_chapter_button, 610, self.w_chapter_button, self.h_chapter_button), self.on_reset)

        self.slider_update()

        self.do_graph = True
        self.graph()
        self.do_graph = False

    def slider_update(self):

        self.weight1_1 = self.slider_w1_1.value() / 10
        self.weight1_2 = self.slider_w1_2.value() / 10
        self.bias1_1 = self.slider_b1_1.value() / 10
        self.bias1_2 = self.slider_b1_2.value() / 10
        self.weight2_1 = self.slider_w2_1.value() / 10
        self.weight2_2 = self.slider_w2_2.value() / 10
        self.bias2 = self.slider_b2.value() / 10
        self.weight1_12 = self.slider_w1_12.value() / 10
        self.weight1_22 = self.slider_w1_22.value() / 10

        self.label_w1_1.setText("W1(1,1): " + str(self.weight1_1))
        self.label_w1_2.setText("W1(2,1): " + str(self.weight1_2))
        self.label_b1_1.setText("b1(1): " + str(self.bias1_1))
        self.label_b1_2.setText("b1(2): " + str(self.bias1_2))
        self.label_w2_1.setText("W2(1,1): " + str(self.weight2_1))
        self.label_w2_2.setText("W2(1,2): " + str(self.weight2_2))
        self.label_b2.setText("b2: " + str(self.bias2))
        self.label_w1_12.setText("W1(1,2): " + str(self.weight1_12))
        self.label_w1_22.setText("W1(2,2): " + str(self.weight1_22))

    def slider_disconnect(self):
        self.sender().valueChanged.disconnect(self.graph)

    def slider_reconnect(self):
        self.do_graph = True
        self.sender().valueChanged.connect(self.graph)
        self.sender().valueChanged.emit(self.sender().value())
        self.do_graph = False

    def on_random(self):
        self.do_graph = False
        self.slider_w1_1.setValue(round(np.random.uniform(-40, 40)))
        self.slider_w1_2.setValue(round(np.random.uniform(-40, 40)))
        self.slider_w1_12.setValue(round(np.random.uniform(-40, 40)))
        self.slider_w1_22.setValue(round(np.random.uniform(-40, 40)))
        self.slider_b1_1.setValue(round(np.random.uniform(-10, 10)))
        self.slider_b1_2.setValue(round(np.random.uniform(-10, 10)))
        self.slider_w2_1.setValue(round(np.random.uniform(-20, 20)))
        self.slider_w2_2.setValue(round(np.random.uniform(-20, 20)))
        self.slider_b2.setValue(round(np.random.uniform(-10, 10)))
        self.do_graph = True
        self.graph()
        self.do_graph = False

    def on_reset(self):
        self.do_graph = False
        self.slider_w1_1.setValue(10)
        self.slider_w1_2.setValue(-10)
        self.slider_w1_12.setValue(-10)
        self.slider_w1_22.setValue(10)
        self.slider_b1_1.setValue(10)
        self.slider_b1_2.setValue(10)
        self.slider_w2_1.setValue(20)
        self.slider_w2_2.setValue(20)
        self.slider_b2.setValue(-20)
        self.do_graph = True
        self.graph()
        self.do_graph = False

    def graph(self):

        if not self.do_graph:
            return

        weight_1, bias_1 = np.array([[self.weight1_1, self.weight1_2]]), np.array([[self.bias1_1, self.bias1_2]])
        weight_2, bias_2 = np.array([[self.weight2_1], [self.weight2_2]]), np.array([[self.bias2]])

        # a = W2(1)*exp(-((p-W1(1)).*b1(1)).^2) + W2(2)*exp(-((p-W1(2)).*b1(2)).^2) + b2
        out = weight_2[0, 0] * np.exp(-((self.pp1 - weight_1[0, 0]) * bias_1[0, 0]) ** 2 - ((self.pp2 - self.weight1_12) * bias_1[0, 0]) ** 2)
        out += weight_2[1, 0] * np.exp(-((self.pp1 - weight_1[0, 1]) * bias_1[0, 1]) ** 2 - ((self.pp2 - self.weight1_22) * bias_1[0, 0]) ** 2) + bias_2[0, 0]

        if len(self.axis3d.collections) > 1:
            self.axis3d.collections[1].remove()
        self.axis3d.plot_surface(self.pp1, self.pp2, out, color="cyan")
        self.canvas.draw()

        out_gray = 1 * (out >= 0)
        while len(self.axis.collections) > 2:
            self.axis.collections[-1].remove()
        self.axis.contourf(self.pp1, self.pp2, out_gray, cmap=plt.cm.Paired, alpha=0.6)
        self.canvas2.draw()

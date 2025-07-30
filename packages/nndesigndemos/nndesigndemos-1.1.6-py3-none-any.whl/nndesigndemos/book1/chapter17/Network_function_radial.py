from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class NetworkFunctionRadial(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(NetworkFunctionRadial, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.make_plot(1, (10, 400, 500, 250))
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(-5, 5)
        self.axis.set_ylim(0, 1)
        self.axis.plot([0] * 50, np.linspace(-5, 5, 50), color="black", linestyle="--", linewidth=0.2)
        self.axis.plot(np.linspace(0, 1, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis_output, = self.axis.plot([], [], markersize=3, color="red")

        self.fill_chapter("Network Function", 17, "Alter the network's\nparameters by dragging\nthe slide bars.\n\n"
                                                  "Click on [Random] to\nset each parameter\nto a random value.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", PACKAGE_PATH + "Figures/nnd17_1.svg",
                          icon_move_left=120, icon_coords=(130, 150, 500, 200), description_coords=(535, 120, 450, 160))

        self.make_slider("slider_w1_1", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 10, -10,
                         (10, 115, 150, 50), self.graph, "label_w1_1", "W1(1,1)", (50, 115 - 25, 100, 50))

        self.make_slider("slider_w1_2", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 10,
                         (10, 360, 150, 50), self.graph, "label_w1_2", "W1(2,1)", (50, 360 - 25, 100, 50))

        self.make_slider("slider_b1_1", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 20,
                         (170, 115, 150, 50), self.graph, "label_b1_1", "b1(1):", (210, 115 - 25, 100, 50))

        self.make_slider("slider_b1_2", QtCore.Qt.Orientation.Horizontal, (-40, 40), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 20,
                         (170, 360, 150, 50), self.graph, "label_b1_2", "b1(2):", (210, 360 - 25, 100, 50))

        self.make_slider("slider_w2_1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 10,
                         (330, 115, 150, 50), self.graph, "label_w2_1", "W2(1,1):", (370, 115 - 25, 100, 50))

        self.make_slider("slider_w2_2", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 10,
                         (330, 360, 150, 50), self.graph, "label_w2_2", "W2(1,2):", (370, 360 - 25, 100, 50))

        self.make_slider("slider_b2", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 0,
                         (self.x_chapter_usual, 290, self.w_chapter_slider, 50), self.graph, "label_b2", "b2: 0.0")

        self.make_button("random_button", "Random", (self.x_chapter_button, 350, self.w_chapter_button, self.h_chapter_button), self.on_random)

        self.graph()

    def graph(self):

        weight1_1 = self.slider_w1_1.value() / 10
        weight1_2 = self.slider_w1_2.value() / 10
        bias1_1 = self.slider_b1_1.value() / 10
        bias1_2 = self.slider_b1_2.value() / 10
        weight2_1 = self.slider_w2_1.value() / 10
        weight2_2 = self.slider_w2_2.value() / 10
        bias2 = self.slider_b2.value() / 10

        self.label_w1_1.setText("W1(1,1): " + str(weight1_1))
        self.label_w1_2.setText("W1(2,1): " + str(weight1_2))
        self.label_b1_1.setText("b1(1): " + str(bias1_1))
        self.label_b1_2.setText("b1(2): " + str(bias1_2))
        self.label_w2_1.setText("W2(1,1): " + str(weight2_1))
        self.label_w2_2.setText("W2(1,2): " + str(weight2_2))
        self.label_b2.setText("b2: " + str(bias2))

        weight_1, bias_1 = np.array([[weight1_1, weight1_2]]), np.array([[bias1_1, bias1_2]])
        weight_2, bias_2 = np.array([[weight2_1], [weight2_2]]), np.array([[bias2]])

        p = np.arange(-5, 5, 0.01)
        # a = W2(1)*exp(-((p-W1(1)).*b1(1)).^2) + W2(2)*exp(-((p-W1(2)).*b1(2)).^2) + b2
        out = weight_2[0, 0] * np.exp(-((p - weight_1[0, 0]) * bias_1[0, 0]) ** 2)
        out += weight_2[1, 0] * np.exp(-((p - weight_1[0, 1]) * bias_1[0, 1]) ** 2) + bias_2[0, 0]

        self.axis_output.set_data(p, out.reshape(-1))

        self.canvas.draw()

    def on_random(self):
        self.slider_w1_1.setValue(round(np.random.uniform(-40, 40)))
        self.slider_w1_2.setValue(round(np.random.uniform(-40, 40)))
        self.slider_b1_1.setValue(round(np.random.uniform(-40, 40)))
        self.slider_b1_2.setValue(round(np.random.uniform(-40, 40)))
        self.slider_w2_1.setValue(round(np.random.uniform(-20, 20)))
        self.slider_w2_2.setValue(round(np.random.uniform(-20, 20)))
        self.slider_b2.setValue(round(np.random.uniform(-20, 20)))
        self.graph()

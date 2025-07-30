from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class HopfieldNetwork(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(HopfieldNetwork, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Hopfield Network", 21, "Click in the left graph\nto simulate the\nHopfield Network.\n\n"
                                                  "Change the weights, biases\nand gain. Then click\n[Update] to change\n"
                                                  "the network.",
                          PACKAGE_PATH + "Logo/Logo_Ch_21.svg", None, description_coords=(535, 95, 450, 250))

        self.x_ = np.arange(-1, 1.0001, 0.05)
        self.y_ = np.copy(self.x_)
        self.X, self.Y = np.meshgrid(self.x_, self.y_)

        self.make_plot(1, (5, 90, 260, 260))
        self.figure.subplots_adjust(left=0.175, right=0.95, bottom=0.15, top=0.9)
        self.make_plot(2, (250, 90, 260, 260))
        self.figure2.subplots_adjust(left=0.175, right=0.975, bottom=0.175, top=0.9)

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Lyapunov Function", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-1, 1)
        self.axes_1.set_ylim(-1, 1)
        self.axes_1.set_xticks([-1, -0.5, 0, 0.5])
        self.axes_1.set_yticks([-1, -0.5, 0, 0.5])
        self.axes_1.set_xlabel("$a1$")
        self.axes_1.xaxis.set_label_coords(1, -0.025)
        self.axes_1.set_ylabel("$a2$")
        self.axes_1.yaxis.set_label_coords(-0.025, 1)
        self.axes1_point, = self.axes_1.plot([], "*")
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.x_data, self.y_data = None, None
        self.x, self.y = None, None
        self.ani = None
        self.path, = self.axes_1.plot([], color="blue")
        self.r = None

        self.axes_2 = self.figure2.add_subplot(projection='3d')
        self.axes_2.set_title("Lyapunov Function", fontdict={'fontsize': 10})
        # self.axes_2.set_xticks([-1, -0.5, 0, 0.5])
        # self.axes_2.set_yticks([-1, -0.5, 0, 0.5])
        # self.axes_2.set_zticks([-1, 0, 1])
        self.axes_2.set_xlabel("$a1$")
        # self.axes_2.xaxis.set_label_coords(1, -0.025)
        self.axes_2.set_ylabel("$a2$")
        # self.axes_2.yaxis.set_label_coords(-0.025, 1)
        self.axes_2.set_zlabel("$V(a)$")
        # self.axes_2.zaxis.set_label_coords(-0.025, 1)
        self.axes_2.set_xlim(-1, 1)
        self.axes_2.set_ylim(-1, 1)
        # self.axes_2.set_zlim(-1, 2)

        # self.paint_latex_string("latex_a1", "$W =$", 16, (80, 340, 500, 200))
        # self.paint_latex_string("latex_a2", "$[$", 45, (170, 340, 500, 200))
        # self.paint_latex_string("latex_a3", "$]$", 45, (320, 340, 500, 200))
        self.make_label("label_a", "W =", (140, 335, 500, 200), font_size=25)
        # self.make_label("label_a1", "[   ]", (190, 324, 500, 200), font_size=100)
        self.label_a.setStyleSheet("color:black")
        # self.label_a1.setStyleSheet("color:black")
        self.make_input_box("a_11", "0", (201, 360, 60, 100))
        self.make_input_box("a_12", "1", (260, 360, 60, 100))
        self.make_input_box("a_21", "1", (201, 410, 60, 100))
        self.make_input_box("a_22", "0", (260, 410, 60, 100))

        # self.paint_latex_string("latex_b1", "$b =$", 16, (120, 490, 500, 200))
        # self.paint_latex_string("latex_b2", "$[$", 45, (210, 490, 500, 200))
        # self.paint_latex_string("latex_b3", "$]$", 45, (290, 490, 500, 200))
        self.make_label("label_d", "b =", (190, 486, 500, 200), font_size=25)
        # self.make_label("label_dd", "[ ]", (227, 476, 500, 200), font_size=100)
        self.label_d.setStyleSheet("color:black")
        # self.label_dd.setStyleSheet("color:black")
        self.make_input_box("d_1", "0", (243, 510, 60, 100))
        self.make_input_box("d_2", "0", (243, 560, 60, 100))

        self.make_slider("slider_b", QtCore.Qt.Orientation.Horizontal, (0, 20), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 14,
                         (self.x_chapter_usual, 320, self.w_chapter_slider, 50), self.on_run,
                         "label_b", "Finite Value Gain: 1.4", (self.x_chapter_usual + 30, 320 - 25, 150, 50))

        self.make_combobox(1, ["Finite Gain", "Infinite Gain"], (self.x_chapter_usual, 430, self.w_chapter_slider, 50),
                           self.change_gain, "label_f", "Gain", (self.x_chapter_slider_label + 5, 410, 150, 50))
        self.finite_gain = True
        self.finite_value_gain = None

        self.make_button("run_button", "Update", (self.x_chapter_button, 380, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.on_run()

    def paintEvent(self, event):
        super(HopfieldNetwork, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        self.paint_bracket(painter, 201, 390, 478, 119)
        self.paint_bracket(painter, 241, 539, 630, 64)
        painter.end()

    def hop(self, t, y):
        a = 2 / np.pi * np.arctan(self.finite_value_gain * np.pi * y * 0.5)
        return -y + np.dot(self.W, a) + self.b.reshape(-1)

    def hopi(self, t, y):
        return 0.5 * np.dot(self.W, y) + self.b.reshape(-1)

    def animate_init(self):
        self.path.set_data(self.x_data, self.y_data)
        self.finite_value_gain = self.slider_b.value() / 10
        self.W = np.array(
            [[float(self.a_11.text()), float(self.a_12.text())], [float(self.a_21.text()), float(self.a_22.text())]])
        self.b = np.array([[float(self.d_1.text())], [float(self.d_2.text())]])
        if self.finite_gain:
            self.r = ode(self.hop).set_integrator("zvode")
            n0 = np.array([[2 * np.tan(np.pi * self.x / 2) / self.finite_value_gain / np.pi],
                           [2 * np.tan(np.pi * self.y / 2) / self.finite_value_gain / np.pi]])
            self.r.set_initial_value(n0, 0)
            t1 = 10
            dt = 0.1
            n = np.zeros((101, 2))
            count = 0
            while self.r.successful() and self.r.t < t1:
                N = self.r.integrate(self.r.t + dt)
                n[count, :] = N.reshape(-1)
                count += 1
            a = 2 * np.arctan(self.finite_value_gain * np.pi * n / 2) / np.pi
        else:
            self.r = ode(self.hopi).set_integrator("zvode")
            n0 = np.array([[self.x], [self.y]])
            self.r.set_initial_value(n0, 0)
            t1 = 10
            dt = 0.1
            n = np.zeros((101, 2))
            count = 0
            while self.r.successful() and self.r.t < t1:
                N = self.r.integrate(self.r.t + dt)
                n[count, :] = N.reshape(-1)
                count += 1
            a = n * (n < 1) * 1 + (n >= 1) * 1
        self.a = a * (a > -1) * 1 - (a <= -1) * 1
        return self.path,

    def on_animate(self, idx):
        self.path.set_data(self.a[:idx, 0], self.a[:idx, 1])
        return self.path,

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            if self.ani and self.ani.event_source:
                self.ani.event_source.stop()
            self.x_data, self.y_data = [event.xdata], [event.ydata]
            self.x, self.y = event.xdata, event.ydata
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=100,
                                     interval=20, repeat=False, blit=True)

    def change_gain(self, idx):
        self.finite_gain = idx == 0
        self.on_run()

    def on_run(self):
        W = np.array([[float(self.a_11.text()), float(self.a_12.text())], [float(self.a_21.text()), float(self.a_22.text())]])
        b = np.array([[float(self.d_1.text())], [float(self.d_2.text())]])
        self.update(W, b)

    def update(self, W, b):

        finite_value_gain = self.slider_b.value() / 10
        self.label_b.setText("Finite Value Gain: " + str(finite_value_gain))
        if not self.finite_gain:
            finite_value_gain = np.inf

        F = np.zeros((len(self.x_), len(self.y_)))
        for i in range(len(self.x_)):
            for j in range(len(self.y_)):
                a = np.array([[self.X[i, j]], [self.Y[i, j]]])
                F[i, j] = -0.5 * np.dot(a.T, np.dot(W, a)) - np.dot(b.T, a)
                for k in range(2):
                    temp1 = np.cos(np.pi / 2 * a[k, 0])
                    if temp1 == 0:
                        temp2 = -np.inf
                    else:
                        temp2 = np.log(np.clip(temp1, 0.001, 100))
                        # temp2 = np.log(temp1)
                    F[i, j] = F[i, j] - 4 / (finite_value_gain * np.pi ** 2) * temp2
        # F[0, -1] = 22.6143
        # F[-1, :] = np.array(list(F[0, :].reshape(-1))[::-1])

        # Removes stuff
        while self.axes_1.collections:
            for collection in self.axes_1.collections:
                collection.remove()
        while self.axes_2.collections:
            for collection in self.axes_2.collections:
                collection.remove()

        # Draws new stuff
        self.axes_1.contour(self.X, self.Y, F, levels=[-5, -2, -1, -0.5, -0.041, -0.023, -0.003, 0.017, 0.16, 0.45, 1, 2, 4, 8, 16])
        # indxx = 3:2:(length(xx)-2);
        #   indyy = 3:2:(length(yy)-2);
        #   xx = xx(indxx);
        #   yy = yy(indyy);
        #   F = F(indxx,:);
        #   F = F(:,indyy);
        #   func_mesh = mesh(xx,yy,F)
        indxx = np.arange(2, len(self.X) - 2, 2)
        indyy = np.arange(2, len(self.Y) - 2, 2)
        xx = self.x_[indxx]
        yy = self.y_[indyy]
        XX, YY = np.meshgrid(xx, yy)
        F = F[indxx, :]
        F = F[:, indyy]
        self.axes_2.plot_surface(XX, YY, F, color="cyan")
        self.canvas.draw()
        self.canvas2.draw()

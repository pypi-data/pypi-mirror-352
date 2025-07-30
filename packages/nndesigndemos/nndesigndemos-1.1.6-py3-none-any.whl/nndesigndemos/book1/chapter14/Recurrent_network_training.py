import numpy as np
import warnings
import matplotlib.cbook
from matplotlib.ticker import FormatStrFormatter
from matplotlib.animation import FuncAnimation
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class RecurrentNetworkTraining(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(RecurrentNetworkTraining, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Recurrent Network Training", 14, "Show the change in\nweight values due to\nthe training of a\n"
                                                            "recurrent network.\n\nClick on the contour plot\nto select the initial\n"
                                                            "weight values.\n\nThe weights will be\nupdated and the network\n"
                                                            "output will be shown at\nthe upper left figure.",
                          PACKAGE_PATH + "Logo/Logo_Ch_14.svg", PACKAGE_PATH + "Figures/nnd14_2.svg",
                          icon_move_left=70, icon_coords=(130, 100, 500, 200), description_coords=(535, 125, 450, 250),
                          icon_rescale=True)

        self.make_plot(1, (10, 300, 250, 200))
        self.figure.subplots_adjust(left=0.15, bottom=0.15)
        self.make_plot(2, (245, 300, 270, 380))
        self.make_plot(3, (10, 480, 250, 200))

        # self.make_slider("slider_w0", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
        #                  (self.x_chapter_usual, 380, self.w_chapter_slider, 50), None, "label_w0", "iW(0): 0.5")
        # self.make_slider("slider_w1", QtCore.Qt.Orientation.Horizontal, (-20, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
        #                  (self.x_chapter_usual, 450, self.w_chapter_slider, 50), None, "label_w1", "lW(1): 0.5")

        self.animation_speed = 100

        self.graph()

    # def print_view(self, event):
    #     print(self.a3.elev, self.a3.azim)

    def graph(self):
        self.figure.clf()  # Clear the plot
        self.figure2.clf()
        self.figure3.clf()

        self.a = self.figure.add_subplot(1, 1, 1)
        self.a2 = self.figure2.add_subplot(1, 1, 1)
        self.a3 = self.figure3.add_subplot(projection='3d')

        self.a.set_xlim(0, 20)
        # self.a2.set_xlim(-2, 2)
        self.a3.set_xlim(-2, 2)
        self.a3.set_ylim(-2, 2)
        # a3.set_zlim(-2, 2)
        self.a.set_title("Input and Target Sequences", fontsize=10)
        self.a2.set_title("Steepest Descent Trajectory", fontsize=10)
        self.a3.set_title("Performance Surface", fontsize=10, pad=1)
        self.a3.view_init(4.43, -64.78)
        self.a3.zaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        self.a.plot(np.linspace(0, 26, 50), [0] * 50, color="red", linestyle="dashed", linewidth=0.5)

        # self.canvas3.mpl_connect("motion_notify_event", self.print_view)

        # self.iw = self.slider_w0.value() / 10
        # self.lw = self.slider_w1.value() / 10
        self.iw = 0.5
        self.lw = 0.5
        # self.label_w0.setText("iW(0): " + str(self.iw))
        # self.label_w1.setText("lW(1): " + str(self.lw))

        self.P = np.array([0.25, 0.25, 0.25, 0.75, 0.75, 0.75, 0.75, 0.75, -0.75, -0.75, -0.75, -0.75, 0.55, 0.55, 0.55, -0.25, -0.25, -0.25, -0.25, -0.25])
        self.a0, t = 0, list(range(1, len(self.P) + 1))
        self.T = self.forward(self.iw, self.lw, self.P, self.a0)

        xx, yy = np.arange(-2, 2.1, 0.1), np.arange(-2, 2.1, 0.1)
        num = len(self.P)
        self.error = np.zeros((len(xx), len(yy)))
        j = 0
        for y1 in yy:
            y2 = self.forward(xx, y1, self.P, self.a0).T
            i = 0
            for x1 in xx:
                e = self.T - y2[i, :]
                self.error[i, j] = np.sum(e * e) / num
                i += 1
            j += 1
        self.X, self.Y = np.meshgrid(xx, yy)

        self.a.scatter([0] + t, [self.a0] + list(self.P), color="white", marker=".", edgecolor="blue")
        self.a.scatter([0] + t, [self.a0] + list(self.T), color="blue", marker=".", s=[1] * (len(t) + 1))
        self.a2.contour(self.X, self.Y, self.error.T, levels=[0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.09, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        self.a3.plot_surface(self.X, self.Y, self.error.T)

        self.ani1, self.ani2 = None, None
        self.x_data, self.y_data = [], []
        self.steepest_descent_data, = self.a2.plot([], linestyle='--', marker='*', label="Gradient Descent Path")
        self.net_approx, = self.a.plot([], linestyle='none', marker="+", color="blue", label="Network approximation")
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick)

        # self.figure.set_tight_layout(True)
        # self.figure2.set_tight_layout(True)
        self.canvas.draw()
        self.canvas2.draw()
        self.canvas3.draw()

    def forward(self, iw, lw, p, a0):
        if type(iw) != np.ndarray:
            y = [self.tansig(iw * p[0] + lw * a0)]
            for i in range(len(p) - 1):
                y.append(self.tansig(iw * p[i + 1] + lw * y[i]))
            return np.array(y)
        else:
            y = np.zeros((len(p), len(iw)))
            y[0, :] = self.tansig(iw * p[0] + lw * a0)
            for i in range(len(p) - 1):
                y[i + 1, :] = self.tansig(iw * p[i + 1] + lw * y[i, :])
            return y

    def gradient(self, iw, lw, p, yt, a0):
        y = [self.tansig(iw * p[0] + lw * a0)]
        e = [yt[0] - y[0]]
        df = 1 - y[0] ** 2
        dy_diw = df * p[0]
        dy_dlw = df * a0
        gw = -2 * e[0] * np.array([[dy_diw], [dy_dlw]])
        for i in range(len(p) - 1):
            y.append(self.tansig(iw * p[i + 1] + lw * y[i]))
            df = 1 - y[i + 1] ** 2
            dy_diw = df * (p[i + 1] + lw * dy_diw)
            dy_dlw = df * (y[i] + lw * dy_dlw)
            e.append(yt[i + 1] - y[i + 1])
            gw = gw - 2 * e[i + 1] * np.array([[dy_diw], [dy_dlw]])
        return gw

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data = [event.xdata]
            self.y_data = [event.ydata]
            self.net_approx.set_data([], [])
            self.canvas.draw()
            self.canvas2.draw()
            self.run_animation()

    def run_animation(self):
        if self.ani1 and self.ani1.event_source:
            self.ani1.event_source.stop()
        if self.ani2 and self.ani2.event_source:
            self.ani2.event_source.stop()
        self.ani2 = FuncAnimation(self.figure2, self.on_animate, init_func=self.animate_init, frames=100,
                                  interval=self.animation_speed, repeat=False, blit=False)
        self.ani1 = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=100,
                                  interval=self.animation_speed, repeat=False, blit=False)
        self.canvas.draw()
        self.canvas2.draw()

    def animate_init(self):
        self.steepest_descent_data.set_data(self.x_data, self.y_data)
        A2 = self.forward(self.x_data[-1], self.y_data[-1], self.P, self.a0)
        self.net_approx.set_data([0] + list(range(1, len(self.P) + 1)), [self.a0] + list(A2))
        E = self.T - A2
        gw = self.gradient(self.x_data[-1], self.y_data[-1], self.P, self.T, self.a0)
        self.dW = -gw
        self.nrmrt = np.sqrt(np.dot(gw.T, gw))
        return self.steepest_descent_data, self.net_approx

    def on_animate(self, idx):

        if self.nrmrt < 0.2:
            return self.steepest_descent_data, self.net_approx

        self.x_data.append(self.x_data[-1] + 0.1 * self.dW[0, 0])
        self.y_data.append(self.y_data[-1] + 0.1 * self.dW[1, 0])
        A2 = self.forward(self.x_data[-1], self.y_data[-1], self.P, self.a0)
        E = self.T - A2
        gw = self.gradient(self.x_data[-1], self.y_data[-1], self.P, self.T, self.a0)
        self.nrmrt = np.sqrt(np.dot(gw.T, gw))
        self.dW = -gw
        self.a2.set_xlim(min([-2, min(self.x_data)]), max([2, max(self.x_data)]))
        self.a2.set_ylim(min([-2, min(self.y_data)]), max([2, max(self.y_data)]))
        self.steepest_descent_data.set_data(self.x_data, self.y_data)
        self.net_approx.set_data([0] + list(range(1, len(self.P) + 1)), [self.a0] + list(A2))
        return self.steepest_descent_data, self.net_approx

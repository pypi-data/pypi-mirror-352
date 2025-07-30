import numpy as np
from scipy.io import loadmat
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FormatStrFormatter

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class SteepestDescentBackprop1(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(SteepestDescentBackprop1, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Steepest Descent Backprop #1", 12, "\n\nUse the pop up menu below\nto select the network\nparameters"
                                                              " to train\nwith backpropagation.\n\nThe corresponding error\nsurface "
                                                              "and contour are\nshown below.\n\nClick in the contour graph\nto start "
                                                              "the steepest\ndescent algorithm.",
                          PACKAGE_PATH + "Logo/Logo_Ch_12.svg", PACKAGE_PATH + "Figures/nnd12_1.svg",
                          icon_move_left=120, icon_coords=(130, 150, 500, 200))

        self.P = np.arange(-2, 2.1, 0.1).reshape(1, -1)
        self.W1, self.b1 = np.array([[10], [10]]), np.array([[-5], [5]])
        self.W2, self.b2 = np.array([[1, 1]]), np.array([[-1]])
        A1 = self.logsigmoid(np.dot(self.W1, self.P) + self.b1)
        self.T = self.logsigmoid(np.dot(self.W2, A1) + self.b2)
        self.lr, self.epochs = None, None

        self.make_plot(1, (255, 380, 260, 260))
        self.make_plot(2, (5, 380, 260, 260))

        self.axes = self.figure.add_subplot(1, 1, 1)
        self.path, = self.axes.plot([], linestyle='--', marker='*', label="Gradient Descent Path")
        self.x_data, self.y_data = [], []
        self.init_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.end_point_1, = self.axes.plot([], "o", fillstyle="none", markersize=11, color="k")
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.ani, self.event = None, None
        self.axes2 = self.figure2.add_subplot(projection='3d')
        self.axes2.view_init(30, -30)
        self.axes2.zaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        # self.canvas2.mpl_connect("motion_notify_event", self.print_view)
        self.axes2.set_title("Sum Sq. Error", fontdict={'fontsize': 10})
        
        self.pair_of_params = 1
        self.pair_params = [["W1(1, 1)", "W2(1, 1)"], ["W1(1, 1)", "b1(1)"], ["b1(1)", "b1(2)"]]
        self.plot_data()

        self.x, self.y = None, None

        self.make_combobox(1, ["W1(1, 1), W2(1, 1)", 'W1(1, 1), b1(1)', 'b1(1), b1(2)'],
                           (520, 370, 175, 50), self.change_pair_of_params,
                           "label_combo", "Pair of parameters", (545, 350, 150, 50))

        self.animation_speed = 0
        self.canvas.draw()

    # def print_view(self, event):
    #     print(self.axes2.elev, self.axes2.azim)

    def change_pair_of_params(self, idx):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.pair_of_params = idx + 1
        self.init_point_1.set_data([], [])
        self.end_point_1.set_data([], [])
        self.init_params()
        self.plot_data()

    def plot_data(self):
        self.x_data = []
        self.y_data = []
        self.path.set_data(self.x_data, self.y_data)
        while self.axes.collections:
            for collection in self.axes.collections:
                collection.remove()
        while self.axes2.collections:
            for collection in self.axes2.collections:
                collection.remove()
        f_data = loadmat(PACKAGE_PATH + "Data/nndbp_new_{}.mat".format(self.pair_of_params))
        x1, y1 = np.meshgrid(f_data["x1"], f_data["y1"])
        self.axes.contour(x1, y1, f_data["E1"], list(f_data["levels"].reshape(-1)))
        self.axes2.plot_surface(x1, y1, f_data["E1"], color="cyan")
        if self.pair_of_params == 1:
            self.axes.scatter([self.W1[0, 0]], [self.W2[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-5, 15)
            self.axes.set_ylim(-5, 15)
            self.axes.set_xticks([-5, 0, 5, 10])
            self.axes.set_yticks([-5, 0, 5, 10])
            self.axes2.set_xticks([-5, 0, 5, 10])
            self.axes2.set_yticks([-5, 0, 5, 10])
            self.axes2.view_init(30, -30)
        elif self.pair_of_params == 2:
            self.axes.scatter([self.W1[0, 0]], [self.b1[0, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 30)
            self.axes.set_ylim(-20, 10)
            self.axes.set_xticks([-10, 0, 10, 20])
            self.axes.set_yticks([-20, -10, -5, 0])
            self.axes2.set_xticks([-10, 0, 10, 20])
            self.axes2.set_yticks([-20, -10, 0, 10, 20])
            self.axes2.set_zticks([0, 1, 2])
            self.axes2.view_init(30, -30)
        elif self.pair_of_params == 3:
            self.axes.scatter([self.b1[0, 0]], [self.b1[1, 0]], color="black", marker="+")
            self.axes.set_xlim(-10, 10)
            self.axes.set_ylim(-10, 10)
            self.axes.set_xticks([-10, -5, 0, 5])
            self.axes.set_yticks([-10, -5, 0, 5])
            self.axes2.set_xticks([-10, -5, 0, 5])
            self.axes2.set_yticks([-5, 0, 5, 10])
            self.axes2.set_zticks([0, 1])
            self.axes2.view_init(30, -30)
        self.axes.set_xlabel(self.pair_params[self.pair_of_params - 1][0], fontsize=8)
        self.axes.xaxis.set_label_coords(0.95, -0.025)
        self.axes.set_ylabel(self.pair_params[self.pair_of_params - 1][1], fontsize=8)
        self.axes.yaxis.set_label_coords(-0.025, 0.95)
        self.axes2.tick_params(pad=0)
        self.axes2.set_xlabel(self.pair_params[self.pair_of_params - 1][0], labelpad=1)
        self.axes2.set_ylabel(self.pair_params[self.pair_of_params - 1][1], labelpad=1)
        self.canvas.draw()
        self.canvas2.draw()

    def animate_init(self):
        self.end_point_1.set_data([], [])
        self.path.set_data(self.x_data, self.y_data)
        return self.path, self.end_point_1

    def on_animate(self, idx):

        n1 = np.dot(self.W1, self.P) + self.b1
        a1 = self.logsigmoid(n1)
        n2 = np.dot(self.W2, a1) + self.b2
        a2 = self.logsigmoid(n2)

        e = self.T - a2

        D2 = a2 * (1 - a2) * e
        D1 = a1 * (1 - a1) * np.dot(self.W2.T, D2)
        dW1 = np.dot(D1, self.P.T) * self.lr
        db1 = np.dot(D1, np.ones((D1.shape[1], 1))) * self.lr
        dW2 = np.dot(D2, a1.T) * self.lr
        db2 = np.dot(D2, np.ones((D2.shape[1], 1))) * self.lr

        if self.pair_of_params == 1:
            self.W1[0, 0] += dW1[0, 0]
            self.W2[0, 0] += dW2[0, 0]
            self.x, self.y = self.W1[0, 0], self.W2[0, 0]
        elif self.pair_of_params == 2:
            self.W1[0, 0] += dW1[0, 0]
            self.b1[0, 0] += db1[0, 0]
            self.x, self.y = self.W1[0, 0], self.b1[0, 0]
        elif self.pair_of_params == 3:
            self.b1[0, 0] += db1[0, 0]
            self.b1[1, 0] += db1[1, 0]
            self.x, self.y = self.b1[0, 0], self.b1[1, 0]

        if idx == self.epochs - 1:
            self.end_point_1.set_data([self.x_data[-1]], [self.y_data[-1]])

        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.path.set_data(self.x_data, self.y_data)
        return self.path, self.end_point_1

    def on_mouseclick(self, event):
        self.init_params()
        self.event = event
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.path.set_data([], [])
        self.x_data, self.y_data = [], []
        self.init_point_1.set_data([event.xdata], [event.ydata])
        self.canvas.draw()
        self.run_animation(event)

    def run_animation(self, event):
        if event.xdata != None and event.xdata != None:
            self.x_data, self.y_data = [event.xdata], [event.ydata]
            self.x, self.y = event.xdata, event.ydata
            if self.pair_of_params == 1:
                self.W1[0, 0], self.W2[0, 0] = self.x, self.y
                self.lr, self.epochs = 3.5, 1000
            elif self.pair_of_params == 2:
                self.W1[0, 0], self.b1[0, 0] = self.x, self.y
                self.lr, self.epochs = 25, 300
            elif self.pair_of_params == 3:
                self.b1[0, 0], self.b1[1, 0] = self.x, self.y
                self.lr, self.epochs = 25, 60
            self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=self.epochs,
                                     interval=self.animation_speed, repeat=False, blit=True)

    def init_params(self):
        self.W1, self.b1 = np.array([[10.], [10.]]), np.array([[-5.], [5.]])
        self.W2, self.b2 = np.array([[1., 1.]]), np.array([[-1.]])

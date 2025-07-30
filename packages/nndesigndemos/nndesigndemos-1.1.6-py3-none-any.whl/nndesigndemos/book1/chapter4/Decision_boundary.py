from PyQt6 import QtWidgets
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class DecisionBoundaries(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(DecisionBoundaries, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Decision Boundaries", 4, "Move the perceptron\ndecision boundary by\ndragging the stars.\n\n"
                                                    "Try to divide the points so\nthat none of them are red.\n\nLeft-click"
                                                    " on the plot to add\na positive class.\n\nRight-click to add a\n"
                                                    "negative class.\n\nThe weight and bias will\ntake on values "
                                                    "associated\nwith the chosen decision\nboundary.",
                          PACKAGE_PATH + "Logo/Logo_Ch_4.svg", None, description_coords=(535, 140, 450, 300))

        self.make_label("label_error", "Error: ---", (self.x_chapter_slider_label, 485, 150, 100))

        self.w = np.array([1.79, 0.894])
        self.b = np.array([1.79])
        self.cid, self.cid2 = None, None
        self.closest_point = None

        self.point_1, self.point_2 = (-2, 2), (0, -2)
        self.prev_x_diff, self.prev_y_diff = None, None
        self.current_x_diff, self.current_y_diff = 2 - -2, 2 - -2
        self.data = [(1, 1, 1), (0, 0, 0), (1, 0, 0), (0, 1, 0)]

        self.make_plot(1, (5, 150, 510, 510))
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0.2, left=0.1)
        self.axes.set_xlim(-3, 3)
        self.axes.set_ylim(-3, 3)
        self.axes.tick_params(labelsize=8)
        self.axes.plot([0] * 20, np.linspace(-3, 3, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes.plot(np.linspace(-3, 3, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.pos_line, = self.axes.plot([], 'mo', label="Positive Class")
        self.neg_line, = self.axes.plot([], 'cs', label="Negative Class")
        self.miss_line_pos, = self.axes.plot([], 'ro')
        self.miss_line_neg, = self.axes.plot([], 'rs')
        self.decision, = self.axes.plot([], 'r-', label="Decision Boundary")
        self.point_1_draw, = self.axes.plot([], '*', markersize=12)
        self.point_2_draw, = self.axes.plot([], '*', markersize=12)
        self.weight_vector = self.axes.quiver([0], [0], [1], [-1], units="xy", scale=1, label="Weight vector")
        self.axes.legend(loc='lower center', fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2), framealpha=0.9, numpoints=1, ncol=2,
                         bbox_to_anchor=(0, -.28, 1, -.280), mode='expand')
        self.axes.set_title("Single Neuron Perceptron")
        self.point_1_draw.set_data([self.point_1[0]], [self.point_1[1]])
        self.point_2_draw.set_data([self.point_2[0]], [self.point_2[1]])
        self.draw_decision_boundary()
        self.compute_error()
        self.draw_data()
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        # latex_w = self.mathTex_to_QPixmap("$W = [1.0 \quad -1.0]$", 10)
        # self.latex_w = QtWidgets.QLabel(self)
        # self.latex_w.setPixmap(latex_w)
        # self.latex_w.setGeometry(50 * self.w_ratio, 80 * self.h_ratio, 300 * self.w_ratio, 100 * self.h_ratio)
        self.make_label("label_W", "W = [1.0  1.0]", (70, 80, 300, 100), font_size=30)
        self.label_W.setStyleSheet("color:black")

        # latex_b = self.mathTex_to_QPixmap("$b = [0.0]$", 10)
        # self.latex_b = QtWidgets.QLabel(self)
        # self.latex_b.setPixmap(latex_b)
        # self.latex_b.setGeometry(350 * self.w_ratio, 80 * self.h_ratio, 300 * self.w_ratio, 100 * self.h_ratio)
        self.make_label("label_b", "b = [0.0]", (320, 80, 300, 100), font_size=30)
        self.label_b.setStyleSheet("color:black")

        self.make_button("undo_click_button", "Undo Last Mouse Click", (self.x_chapter_button, 450, self.w_chapter_button, self.h_chapter_button), self.on_undo_mouseclick)
        self.make_button("clear_button", "Clear Data", (self.x_chapter_button, 480, self.w_chapter_button, self.h_chapter_button), self.on_clear)

    def on_mouseclick(self, event):
        """Add an item to the plot"""
        if event.xdata != None and event.ydata != None:
            d_click_p1 = abs(self.point_1[1] - event.ydata)
            d_click_p2 = abs(self.point_2[1] - event.ydata)
            self.closest_point = "1" if d_click_p1 <= d_click_p2 else "2"
            if min(d_click_p1, d_click_p2) < 0.2:
                self.cid2 = self.canvas.mpl_connect("motion_notify_event", self.on_mouse_drag)
                self.cid = self.canvas.mpl_connect("button_release_event", self.on_mousepressed)
            else:
                if self.cid:
                    self.canvas.mpl_disconnect(self.cid)
                if self.cid2:
                    self.canvas.mpl_disconnect(self.cid2)
                self.cid, self.cid2 = None, None
                self.data.append((event.xdata, event.ydata, 1 if event.button == 1 else 0))
                self.compute_error()
                self.draw_data()

    def on_mouse_drag(self, event):
        self.on_mousepressed(event, disconnect=False)

    def on_mousepressed(self, event, disconnect=True):
        if self.closest_point == "1":
            self.point_1 = (event.xdata, event.ydata)
        elif self.closest_point == "2":
            self.point_2 = (event.xdata, event.ydata)
        self.prev_x_diff, self.prev_y_diff = self.current_x_diff, self.current_y_diff
        # print(self.point_1, self.point_2)
        if not self.point_1[0] or not self.point_2[0]:
            return
        self.current_x_diff, self.current_y_diff = self.point_1[0] - self.point_2[0], self.point_1[1] - self.point_2[1]
        self.find_parameters()
        self.draw_decision_boundary()
        self.draw_data()
        self.compute_error()
        if disconnect:
            self.canvas.mpl_disconnect(self.cid2)


    def draw_data(self):
        self.point_1_draw.set_data([self.point_1[0]], [self.point_1[1]])
        self.point_2_draw.set_data([self.point_2[0]], [self.point_2[1]])
        data_pos, data_neg, data_miss_pos, data_miss_neg = [], [], [], []
        for xy, miss in zip(self.data, self.data_missclasified):
            if miss:
                if xy[2] == 1:
                    data_miss_pos.append(xy)
                elif xy[2] == 0:
                    data_miss_neg.append(xy)
            else:
                if xy[2] == 1:
                    data_pos.append(xy)
                elif xy[2] == 0:
                    data_neg.append(xy)
        self.pos_line.set_data([xy[0] for xy in data_pos], [xy[1] for xy in data_pos])
        self.neg_line.set_data([xy[0] for xy in data_neg], [xy[1] for xy in data_neg])
        self.miss_line_pos.set_data([xy[0] for xy in data_miss_pos], [xy[1] for xy in data_miss_pos])
        self.miss_line_neg.set_data([xy[0] for xy in data_miss_neg], [xy[1] for xy in data_miss_neg])
        self.canvas.draw()

    def draw_decision_boundary(self):
        lim = self.axes.get_xlim()
        X = np.linspace(lim[0], lim[1], 101)
        Y = self.find_decision_boundary(X)
        self.decision.set_data(X, Y)
        self.weight_vector.set_UVC(self.w[0], self.w[1])
        self.canvas.draw()

    def find_parameters(self):
        from numpy import ones, vstack
        from numpy.linalg import lstsq
        x_coords, y_coords = zip(*[self.point_1, self.point_2])
        A = vstack([x_coords, ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords, rcond=None)[0]
        if str(self.prev_x_diff)[0] != str(self.current_x_diff)[0]:
            if str(self.prev_y_diff)[0] != str(self.current_y_diff)[0]:
                self.w[1] = -self.w[1]
                self.w[0] = np.round(-m * self.w[1], 2)
            else:
                self.w[1] = np.round(-self.w[0] / m, 2)
        else:
            if str(self.prev_y_diff)[0] != str(self.current_y_diff)[0]:
                self.w[0] = np.round(-m * self.w[1], 2)
            else:
                self.w[1] = np.round(-self.w[0] / m, 2)
        scale = np.sqrt(self.w[0] ** 2 + self.w[1] ** 2)
        self.w[0] = np.round(self.w[0] / scale, 2)
        self.w[1] = np.round(self.w[1] / scale, 2)
        self.b = np.round(np.array([-c * self.w[1]]), 2)
        # self.latex_w.setPixmap(self.mathTex_to_QPixmap("$W = [{} \quad {}]$".format(self.w[0], self.w[1]), 10))
        self.label_W.setText("W = [{}  {}]".format(round(self.w[0], 1), round(self.w[1], 1)))
        # self.latex_b.setPixmap(self.mathTex_to_QPixmap("$b = [{}]$".format(self.b[0]), 10))
        self.label_b.setText("b = [{}]".format(round(self.b[0], 1)))
        self.compute_error()

    def find_decision_boundary(self, x):
        """Returns the corresponding y value for the input x on the decision
        boundary"""
        return -(x * self.w[0] + self.b) / (self.w[1] if self.w[1] != 0 else .000001)

    def run_forward(self, p):
        """Given an input of dimension R, run the network"""
        return self.hardlim(self.w.dot(p) + self.b)

    def compute_error(self):
        if self.data:
            self.data_missclasified, error = [], 0
            for xy in self.data:
                t_hat = self.run_forward(np.array(xy[0:2]))
                if t_hat != xy[2]:
                    self.data_missclasified.append(True)
                    error += 1
                else:
                    self.data_missclasified.append(False)
            self.label_error.setText("Error: {}".format(error))
        else:
            self.label_error.setText("Error: ---")

    def on_clear(self):
        self.data = []
        self.compute_error()
        self.draw_data()

    def clear_decision_boundary(self):
        self.decision.set_data([], [])
        self.canvas.draw()

    def on_undo_mouseclick(self):
        if self.data:
            self.data.pop()
            self.compute_error()
            self.draw_data()

import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation
from scipy.spatial import distance

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class LVQ1(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LVQ1, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("LVQ1", 16, "Click [Learn] to apply the\nLVQ1 rule once.\n\nClick [Train] to apply it\non all"
                                      " the inputs.\n\nClick [Random] to get\nrandom weights.\n\nLeft-click on the plot "
                                      "to add\na positive class.\n\nRight-click to add a\nnegative class.\n\n"
                                      "Misclassifications are shown in red.",
                          PACKAGE_PATH + "Logo/Logo_Ch_16.svg", None, description_coords=(535, 160, 450, 250))

        self.W2 = np.array([[1, 1, 0, 0], [0, 0, 1, 1]])
        self.alpha = 0.4

        self.make_plot(1, (15, 100, 500, 500))
        self.axes_1 = self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0.2, left=0.1)
        # self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_yticks([])
        self.axes_1.set_xticks([])
        self.axes_1.set_xlim(-3, 3)
        self.axes_1.set_ylim(-3, 3)
        self.axes_1.grid(True, linestyle='--')
        self.ani = None

        self.p_point_higlight, = self.axes_1.plot([], "*", markersize=16)
        self.P = np.array([[-1.5, -2.0, 2.0, 1.5, 2.0, 2.0, -2.0, -1.5],
                           [2.0, 1.5, 2.0, 2.0, -2.0, -1.5, -2.0, -2.0]])
        self.T = np.array([[1, 1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0, 1, 1]])
        self.pos_line, = self.axes_1.plot([], 'mo', label="Positive Class")
        self.neg_line, = self.axes_1.plot([], 'cs', label="Negative Class")
        self.miss_line_pos, = self.axes_1.plot([], 'ro')
        self.miss_line_neg, = self.axes_1.plot([], 'rs')
        self.W = None
        self.pos_weight, = self.axes_1.plot([], 'm+', label="Positive Weight", markersize=16)
        self.neg_weight, = self.axes_1.plot([], 'c+', label="Negative Weight", markersize=16)
        self.axes_1.legend(loc='lower center', fontsize=8, framealpha=0.9, numpoints=1, ncol=2,
                           bbox_to_anchor=(0, -.28, 1, -.280), mode='expand')
        # self.axes_1.legend(loc='lower center', fontsize=8, framealpha=0.9, numpoints=2, ncol=2,
        #                    bbox_to_anchor=(0, -.28, 1, -.280), mode='expand')
        # self.axes_1.legend(loc="lower center", ncol=4, bbox_to_anchor=(-3, -.28, 6, -.280))
        # self.axes_1.legend()
        self.init_weights()
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)
        self.cid, self.w_change = None, None

        self.make_label("warning_label", "", (self.x_chapter_usual + 10, 400, 300, 100))

        self.make_button("learn_button", "Learn", (20, 610, self.w_chapter_button - 30, self.h_chapter_button), self.on_learn)
        self.make_button("train_button", "Train", (200, 610, self.w_chapter_button - 30, self.h_chapter_button), self.on_run)
        self.make_button("random_button", "Random", (360, 610, self.w_chapter_button - 30, self.h_chapter_button), self.init_weights)

        self.make_button("undo_click_button", "Undo Last Mouse Click", (50, 640, self.w_chapter_button, self.h_chapter_button), self.on_undo_mouseclick)
        self.make_button("clear_button", "Clear Data", (250, 640, self.w_chapter_button, self.h_chapter_button), self.on_clear)

    def update_plot(self, omit_idx=None):

        if len(self.P) == 0:
            pos_weights_x, neg_weights_x, pos_weights_y, neg_weights_y = [], [], [], []
            for i in range(len(self.W)):
                if i == 0 or i == 1:
                    pos_weights_x.append(self.W[i, 0])
                    pos_weights_y.append(self.W[i, 1])
                else:
                    neg_weights_x.append(self.W[i, 0])
                    neg_weights_y.append(self.W[i, 1])
            self.pos_weight.set_data(pos_weights_x, pos_weights_y)
            self.neg_weight.set_data(neg_weights_x, neg_weights_y)
            self.pos_line.set_data([], [])
            self.neg_line.set_data([], [])
            self.miss_line_pos.set_data([], [])
            self.miss_line_neg.set_data([], [])
            return

        pos_points_x, neg_points_x, pos_points_y, neg_points_y = [], [], [], []
        for i in range(self.P.shape[1]):
            if omit_idx is not None and i == omit_idx:
                continue
            if self.T[0, i] == 0:
                pos_points_x.append(self.P[0, i])
                pos_points_y.append(self.P[1, i])
            else:
                neg_points_x.append(self.P[0, i])
                neg_points_y.append(self.P[1, i])
        self.pos_line.set_data(pos_points_x, pos_points_y)
        self.neg_line.set_data(neg_points_x, neg_points_y)

        pos_weights_x, neg_weights_x, pos_weights_y, neg_weights_y = [], [], [], []
        for i in range(len(self.W)):
            if i == 0 or i == 1:
                pos_weights_x.append(self.W[i, 0])
                pos_weights_y.append(self.W[i, 1])
            else:
                neg_weights_x.append(self.W[i, 0])
                neg_weights_y.append(self.W[i, 1])
        self.pos_weight.set_data(pos_weights_x, pos_weights_y)
        self.neg_weight.set_data(neg_weights_x, neg_weights_y)

        dist_v = np.zeros((len(self.W), self.P.shape[1]))
        for i in range(len(self.W)):
            for j in range(self.P.shape[1]):
                dist_v[i, j] = distance.euclidean(self.W[i].reshape(-1), self.P[:, j].reshape(-1))
        a1 = self.compet(-dist_v, axis=0)
        a2 = np.dot(self.W2, a1)
        e = self.T - a2
        miss_pos_points_x, miss_pos_points_y, miss_neg_points_x, miss_neg_points_y = [], [], [], []
        for i in range(self.P.shape[1]):
            if omit_idx is not None and i == omit_idx:
                continue
            if e[0, i] == 0:
                if self.T[0, i] == 0:
                    miss_pos_points_x.append(self.P[0, i])
                    miss_pos_points_y.append(self.P[1, i])
                else:
                    miss_neg_points_x.append(self.P[0, i])
                    miss_neg_points_y.append(self.P[1, i])
        self.miss_line_pos.set_data(miss_pos_points_x, miss_pos_points_y)
        self.miss_line_neg.set_data(miss_neg_points_x, miss_neg_points_y)

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()

    def slide(self):
        self.ani_stop()
        if self.axes_1.collections:
            self.axes_1.collections[-1].remove()
        self.alpha = float(self.slider_lr.value() / 10)
        self.label_lr.setText("Learning_rate: {}".format(self.alpha))
        self.update_plot()
        self.canvas.draw()
        # self.on_run()

    def init_weights(self):
        self.ani_stop()
        self.W = 2 * np.random.uniform(0, 1, (4, 2)) - 1
        self.update_plot()
        self.canvas.draw()

    def animate_init_train(self):
        if self.axes_1.collections:
            self.axes_1.collections[-1].remove()
        return self.pos_line, self.neg_line, self.pos_weight, self.neg_weight, self.miss_line_pos, self.miss_line_neg, self.p_point_higlight

    def on_animate_train(self, idx):

        if idx == 0:
            seed = np.random.randint(0, 1000)
            np.random.seed(seed)
            np.random.shuffle(self.P.T)
            np.random.seed(seed)
            np.random.shuffle(self.T.T)

        if idx in list(np.arange(0, 10000, 3)):
            i = np.random.randint(0, self.P.shape[1])
            self.p = self.P[:, int(idx / 3)]
            self.t = self.T[:, int(idx / 3)]
            dist_v = np.zeros((len(self.W),))
            for i in range(len(self.W)):
                dist_v[i] = distance.euclidean(self.W[i].reshape(-1), self.p.reshape(-1))
            self.a1 = self.compet(-dist_v)
            a2 = np.dot(self.W2, self.a1)
            e = self.t - a2
            if sum(e == 0) > 0:
                self.color = "red"
            else:
                self.color = "green"
        elif idx in list(np.arange(1, 10000, 3)):
            e = np.dot(self.W2.T, self.t)
            i = np.argmax(self.a1)
            w1_new = self.W[i, :] - (e[i] * 2 - 1) * (self.alpha * self.a1[i] * (self.p.T - self.W[i, :]))
        elif idx in list(np.arange(2, 10000, 3)):
            self.p_point_higlight.set_data([], [])

        if idx in list(np.arange(0, 10000, 3)):
            self.update_plot(omit_idx=idx / 3)
            self.p_point_higlight.set_data([self.p[0]], [self.p[1]])
            self.p_point_higlight.set_color(self.color)
        elif idx in list(np.arange(1, 1000, 3)):
            self.update_plot(omit_idx=idx - 1 / 3)
            self.update_v = self.axes_1.quiver([self.W[i, :][0]], [self.W[i, :][1]], [w1_new[0] - self.W[i, :][0]], [w1_new[1] - self.W[i, :][1]], units="xy", scale=1, color=self.color)
            self.W[i, :] = np.copy(w1_new)
        elif idx in list(np.arange(2, 1000, 3)):
            self.axes_1.collections[-1].remove()
            self.update_plot()

        return self.pos_line, self.neg_line, self.pos_weight, self.neg_weight, self.miss_line_pos, self.miss_line_neg, self.p_point_higlight

    def on_learn(self):
        self.ani_stop()
        if len(self.P) > 0:
            self.warning_label.setText("")
            self.ani = FuncAnimation(self.figure, self.on_animate_train, init_func=self.animate_init_train, frames=3,
                                     interval=1000, repeat=False, blit=False)
        else:
            self.warning_label.setText("  Draw at least one point!")
        self.update_plot()
        self.canvas.draw()

    def on_run(self):
        self.ani_stop()
        if len(self.P) > 0:
            self.warning_label.setText("")
            self.ani = FuncAnimation(self.figure, self.on_animate_train, init_func=self.animate_init_train, frames=3 * self.P.shape[1],
                                     interval=1000, repeat=False, blit=False)
        else:
            self.warning_label.setText("  Draw at least one point!")
        self.update_plot()
        self.canvas.draw()

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            self.ani_stop()
            if len(self.P) > 0:
                self.P = np.hstack((self.P, np.array([[event.xdata], [event.ydata]])))
                if event.button == 1:
                    self.T = np.hstack((self.T, np.array([[1], [0]])))
                else:
                    self.T = np.hstack((self.T, np.array([[0], [1]])))
            else:
                self.P = np.array([[event.xdata], [event.ydata]])
                if event.button == 1:
                    self.T = np.array([[1], [0]])
                else:
                    self.T = np.array([[0], [1]])
            self.update_plot()
            self.canvas.draw()

    def on_mousepressed(self, event):
        if self.w_change == 1:
            self.W_1 = [event.xdata, event.ydata]
        elif self.w_change == 2:
            self.W_2 = [event.xdata, event.ydata]
        elif self.w_change == 3:
            self.W_3 = [event.xdata, event.ydata]
        self.update_plot()
        self.canvas.draw()

    def on_undo_mouseclick(self):
        self.ani_stop()
        if len(self.P) > 0:
            self.P = self.P[:, :-1]
            self.T = self.T[:, :-1]
            self.update_plot()
            self.canvas.draw()

    def on_clear(self):
        self.ani_stop()
        if len(self.P) > 0:
            self.P = []
            self.T = []
            self.update_plot()
            self.canvas.draw()

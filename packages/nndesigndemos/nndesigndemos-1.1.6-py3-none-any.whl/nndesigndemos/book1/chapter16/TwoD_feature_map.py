from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class TwoDFeatureMap(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(TwoDFeatureMap, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("2-D Feature Map", 16, "Click [Train] to present 500\nvectors to the feature map.\n\n"
                                                 "Several clicks are required\nto obtain a stable network.\n\n"
                                                 "Click [Reset] to start over\nif the network develops\na twist.",
                          PACKAGE_PATH + "Logo/Logo_Ch_16.svg", None)

        Sx, Sy = 6, 6
        S = Sx * Sy
        self.max_dist = np.ceil(np.sqrt(np.sum(np.array([Sx, Sy]) ** 2)))
        self.NDEC = 0.999

        self.W_ = np.zeros((S, 3))
        self.W_[:, -1] = 1
        Y, X = np.meshgrid(np.arange(1, Sy + 1), np.arange(1, Sx + 1))
        Ind2Pos = np.array([X.reshape(-1), Y.reshape(-1)]).T
        self.N = np.zeros((S, S))
        for i in range(S):
            for j in range(i):
                self.N[i, j] = np.sqrt(np.sum((Ind2Pos[i, :] - Ind2Pos[j, :]) ** 2))

        self.Nto, self.Nfrom = np.where(self.N.T == 1)
        self.NN = len(self.Nfrom)

        self.N = self.N + self.N.T

        self.P = np.ones((3, 1000))
        # np.random.seed(0)  # This is only for testing - comment out for production
        self.P[:2, :] = np.random.random(
            (1000, 2)).T - 0.5  # The transpose is done so we get the same random numbers as in MATLAB
        self.P = np.divide(self.P, (np.ones((3, 1)) * np.sqrt(np.sum(self.P ** 2, axis=0))))

        up = np.arange(-0.5, 0.5, 0.1)
        down = -np.copy(up)
        flat = np.zeros((1, len(up))) + 0.5
        xx = np.array(list(up) + list(flat.reshape(-1)) + list(down) + list(-flat.reshape(-1)) + [up[0]])
        yy = np.array(list(-flat.reshape(-1)) + list(up) + list(flat.reshape(-1)) + list(down) + [-flat[0, 0]])
        zz = np.array([list(xx), list(yy)])
        zz = zz / (np.ones((2, 1)) * np.sqrt(np.sum(zz ** 2, axis=0) + 1))

        self.make_plot(1, (15, 100, 500, 500))
        self.axis1 = self.figure.add_subplot(1, 1, 1)
        self.axis1.set_xlim(-1, 1)
        self.axis1.set_ylim(-1, 1)
        self.axis1.set_xticks([])
        self.axis1.set_yticks([])
        self.axis1.plot(zz[0, :], zz[1, :])
        self.lines = []
        self.lines_anim = []
        self.canvas.draw()

        self.W = self.W_
        self.ani = None
        self.n_runs = 0

        # self.label_eq = QtWidgets.QLabel(self)
        # self.label_eq.setText("a = purelin(w * p + b)")
        # self.label_eq.setFont(QtGui.QFont("Times New Roman", 12, italic=True))
        # self.label_eq.setGeometry((self.x_chapter_slider_label - 30) * self.w_ratio, 350 * self.h_ratio, 150 * self.w_ratio, 100 * self.h_ratio)

        self.make_label("label_presentations", "Presentations: 0", (535, 290, 150, 100))

        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 100,
                         (15, 610, 250, 50), self.slide, "label_lr", "Learning Rate: 1.0", (90, 585, 150, 50))
        self.lr = 1

        self.make_slider("slider_nei", QtCore.Qt.Orientation.Horizontal, (0, 90), QtWidgets.QSlider.TickPosition.TicksBelow, 10, 90,
                         (265, 610, 250, 50), self.slide, "label_nei", "Neighborhood: 9.00", (335, 585, 150, 50))
        self.nei = 9

        self.make_button("run_button", "Train", (self.x_chapter_button, 370, self.w_chapter_button, self.h_chapter_button), self.on_run_2)
        self.make_button("reset_button", "Reset", (self.x_chapter_button, 400, self.w_chapter_button, self.h_chapter_button), self.on_reset)

        self.do_slide = True

    def on_reset(self):
        self.W = self.W_
        while self.lines_anim:
            self.lines_anim.pop().remove()
        self.canvas.draw()
        self.do_slide = False
        self.lr = 1
        self.nei = self.max_dist
        self.label_lr.setText("Learning rate: " + str(self.lr))
        self.label_nei.setText("Neighborhood: " + str(self.nei))
        self.slider_lr.setValue(self.lr * 100)
        self.slider_nei.setValue(round(self.nei * 10))
        self.do_slide = True
        self.n_runs = 0
        self.label_presentations.setText("Presentations: 0")

    def slide(self):
        if self.do_slide:
            self.lr = self.slider_lr.value() / 100
            self.nei = self.slider_nei.value() / 10
            self.label_lr.setText("Learning rate: " + str(self.lr))
            self.label_nei.setText("Neighborhood: " + str(self.nei))

    def on_run(self):

        if self.lines:
            for line in self.lines:
                line.pop(0).remove()
            self.lines = []

        s, r = self.W.shape
        Q = self.P.shape[1]

        for z in range(500):

            q = int(np.fix(np.random.random() * Q))
            p = self.P[:, q].reshape(-1, 1)

            a = self.compet_(np.dot(self.W, p))
            i = np.argmax(a)
            N_c = np.copy(self.N)[:, i]
            N_c[N_c <= self.nei] = 1
            N_c[N_c != 1] = 0
            a = 0.5 * (a + N_c.reshape(-1, 1))

            self.W = self.W + self.lr * np.dot(a, np.ones((1, r))) * (np.dot(np.ones((s, 1)), p.T) - self.W)
            self.lr = (self.lr - 0.01) * 0.998 + 0.01
            self.nei = (self.nei - 1) * self.NDEC + 1

        for i in range(self.NN):
            from_ = self.Nfrom[i]
            to_ = self.Nto[i]
            print(self.W[from_, 0], self.W[to_, 0], "---", self.W[from_, 1], self.W[to_, 1])
            self.lines.append(self.axis1.plot([self.W[from_, 0], self.W[to_, 0]], [self.W[from_, 1], self.W[to_, 1]], color="red"))

        nei_temp = self.nei
        self.slider_lr.setValue(self.lr * 100)
        self.nei = nei_temp
        self.slider_nei.setValue(self.nei * 10)
        self.label_lr.setText("Learning rate: " + str(self.lr))
        self.label_nei.setText("Neighborhood: " + str(self.nei))

        self.canvas.draw()

    def animate_init(self):
        while self.lines_anim:
            self.lines_anim.pop().remove()
        for _ in range(self.NN):
            self.lines_anim.append(self.axis1.plot([], color="red", linewidth=0.5)[0])

    def on_animate(self, idx):

        s, r = self.W.shape
        Q = self.P.shape[1]

        for z in range(100):
            q = int(np.fix(np.random.random() * Q))
            p = self.P[:, q].reshape(-1, 1)

            a = self.compet_(np.dot(self.W, p))
            i = np.argmax(a)
            N_c = np.copy(self.N)[:, i]
            N_c[N_c <= self.nei] = 1
            N_c[N_c != 1] = 0
            a = 0.5 * (a + N_c.reshape(-1, 1))

            self.W = self.W + self.lr * np.dot(a, np.ones((1, r))) * (np.dot(np.ones((s, 1)), p.T) - self.W)
            self.lr = (self.lr - 0.01) * 0.998 + 0.01
            self.nei = (self.nei - 1) * self.NDEC + 1
            self.do_slide = False
            self.slider_lr.setValue(round(self.lr * 100))
            self.slider_nei.setValue(round(self.nei * 10))
            self.label_lr.setText("Learning rate: " + str(round(self.lr, 2)))
            self.label_nei.setText("Neighborhood: " + str(round(self.nei, 2)))
            self.do_slide = True
            self.label_presentations.setText("Presentations: " + str((self.n_runs - 1) * 500 + idx * 100 + z + 1))

        for i in range(self.NN):
            from_ = self.Nfrom[i]
            to_ = self.Nto[i]
            self.lines_anim[i].set_data([self.W[from_, 0], self.W[to_, 0]], [self.W[from_, 1], self.W[to_, 1]])

    def on_run_2(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.n_runs += 1
        self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init,
                                 frames=5, interval=0, repeat=False, blit=False)
        self.canvas.draw()

    @staticmethod
    def compet_(n):
        max_idx = np.argmax(n)
        out = np.zeros(n.shape)
        out[max_idx] = 1
        return out

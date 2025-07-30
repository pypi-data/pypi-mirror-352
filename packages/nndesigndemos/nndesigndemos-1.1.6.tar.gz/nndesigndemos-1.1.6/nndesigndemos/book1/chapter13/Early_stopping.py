from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class EarlyStopping(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(EarlyStopping, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Early Stopping", 13, "Use the slider to change the\nNoise Standard Deviation of\nthe training points.\n\n"
                                                "Click [Train] to train\non the training points.\n\nThe training and validation\n"
                                                "performance indexes will be\npresented on the right.\n\nYou will notice that\n"
                                                "without early stopping\nthe validation error\nwill increase.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, description_coords=(535, 120, 450, 300))

        self.max_epoch = 120
        self.T = 2
        self.pp0 = np.linspace(-1, 1, 201)
        self.tt0 = np.sin(2 * np.pi * self.pp0 / self.T)

        self.pp = np.linspace(-0.95, 0.95, 20)
        self.p = np.linspace(-1, 1, 21)

        self.make_plot(1, (100, 90, 300, 300))
        self.make_plot(2, (100, 380, 300, 300))

        self.train_error, self.error_train = [], None
        self.test_error, self.error_test = [], None
        self.ani_1, self.ani_2 = None, None
        self.W1, self.b1, self.W2, self.b2 = None, None, None, None
        self.S1, self.random_state = 20, 42
        # np.random.seed(self.random_state)
        self.tt, self.t = None, None

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Function", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-1, 1)
        self.axes_1.set_ylim(-1.5, 1.5)
        self.axes_1.plot(self.pp0, np.sin(2 * np.pi * self.pp0 / self.T))
        self.net_approx, = self.axes_1.plot([], linestyle="--")
        self.train_points, = self.axes_1.plot([], marker='*', label="Train", linestyle="")
        self.test_points, = self.axes_1.plot([], marker='.', label="Test", linestyle="")
        self.axes_1.legend()
        self.canvas.draw()

        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_title("Performance Indexes", fontdict={'fontsize': 10})
        self.train_e, = self.axes_2.plot([], [], linestyle='-', color="b", label="train error")
        self.test_e, = self.axes_2.plot([], [], linestyle='-', color="r", label="test error")
        self.axes_2.legend()
        # self.axes_2.plot([1, 1])
        self.axes_2.plot(1, 1000, marker="*")
        self.axes_2.plot(100, 1000, marker="*")
        self.axes_2.plot(1, 0.01, marker="*")
        self.axes_2.plot(100, 0.01, marker="*")
        self.axes_2.set_xscale("log")
        self.axes_2.set_yscale("log")
        # self.axes_2.set_xlim(1, 100)
        # self.axes_2.set_ylim(0.1, 1000)
        # self.axes_2.set_xticks([1, 10, 100])
        # self.axes_2.set_yticks([0.1, 0, 10, 100, 1000])
        # for line in self.axes_2.lines:
        #     line.remove()
        self.figure2.set_tight_layout(True)
        self.canvas2.draw()

        self.nsd = 1
        self.make_slider("slider_nsd", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (self.x_chapter_usual, 410, self.w_chapter_slider, 100), self.slide,
                         "label_nsd", "Noise standard deviation: 1.0", (self.x_chapter_usual + 10, 380, self.w_chapter_slider, 100))

        self.animation_speed = 100

        self.plot_train_test_data()

        self.run_button = QtWidgets.QPushButton("Train", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 490 * self.h_ratio, self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.on_run)

        self.make_button("pause_button", "Pause", (self.x_chapter_button, 520, self.w_chapter_button, self.h_chapter_button), self.on_stop)
        self.pause = True

        self.init_params()
        self.full_batch = False

    def ani_stop(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.stop()

    def ani_start(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.start()
        if self.ani_2 and self.ani_2.event_source:
            self.ani_2.event_source.start()

    def on_stop(self):
        if self.pause:
            self.ani_stop()
            self.pause_button.setText("Unpause")
            self.pause = False
        else:
            self.ani_start()
            self.pause_button.setText("Pause")
            self.pause = True

    def animate_init_1(self):
        self.error_goal_reached = False
        self.a1 = self.logsigmoid_stable(np.dot(self.W1, self.pp.reshape(1, -1)) + self.b1)
        self.a2 = self.purelin(np.dot(self.W2, self.a1) + self.b2)
        self.e = self.tt.reshape(1, -1) - self.a2
        self.error_prev = np.dot(self.e, self.e.T).item()
        self.mu = 10
        self.RS = self.S1 * 1
        self.RS1 = self.RS + 1
        self.RSS = self.RS + self.S1
        self.RSS1 = self.RSS + 1
        self.RSS2 = self.RSS + self.S1 * 1
        self.RSS3 = self.RSS2 + 1
        self.RSS4 = self.RSS2 + 1
        self.ii = np.eye(self.RSS4)
        self.train_e.set_data([], [])
        self.test_e.set_data([], [])
        self.net_approx.set_data([], [])
        return self.train_e, self.test_e

    def animate_init_2(self):
        self.net_approx.set_data([], [])
        return self.net_approx,

    def on_animate_1(self, idx):
        self.error_train, self.error_test = self.train_v2()
        self.train_error.append(self.error_train)
        self.train_e.set_data(list(range(len(self.train_error))), self.train_error)
        self.test_error.append(self.error_test)
        self.test_e.set_data(list(range(len(self.test_error))), self.test_error)
        return self.train_e, self.test_e

    def on_animate_2(self, idx):
        nn_output = []
        for sample, target in zip(self.pp0, self.tt0):
            a, n2, n1, a1, a0 = self.forward(sample)
            nn_output.append(a)
        self.net_approx.set_data(self.pp0, nn_output)
        # self.axes_2.set_yscale("log")
        return self.net_approx,

    def on_run(self):
        self.pause_button.setText("Pause")
        self.pause = True
        self.init_params()
        self.ani_stop()
        self.net_approx.set_data([], [])
        self.train_error, self.test_error = [], []
        self.canvas.draw()
        self.canvas2.draw()
        self.run_animation()

    def run_animation(self):
        self.ani_stop()
        self.ani_1 = FuncAnimation(self.figure2, self.on_animate_1, init_func=self.animate_init_1, frames=self.max_epoch,
                                   interval=self.animation_speed, repeat=False, blit=True)
        self.ani_2 = FuncAnimation(self.figure, self.on_animate_2, init_func=self.animate_init_2, frames=self.max_epoch,
                                   interval=self.animation_speed, repeat=False, blit=True)

    def slide(self):
        # if list(self.ani_1.frame_seq):  # If the animation is running
        #     self.slider_nsd.setValue(self.nsd * 10)
            # self.ani_1.event_source.start()
        # else:
        self.init_params()
        # np.random.seed(self.random_state)
        self.nsd = float(self.slider_nsd.value() / 10)
        self.label_nsd.setText("Noise standard deviation: " + str(self.nsd))
        self.plot_train_test_data()
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        self.ani_stop()
        self.train_error, self.test_error = [], []
        self.net_approx.set_data([], [])
        self.canvas.draw()
        self.canvas2.draw()

    def plot_train_test_data(self):
        self.tt = np.sin(2 * np.pi * self.pp / self.T) + np.random.uniform(-2, 2, self.pp.shape) * 0.2 * self.nsd
        self.train_points.set_data(self.pp, self.tt)
        self.t = np.sin(2 * np.pi * self.p / self.T) + np.random.uniform(-2, 2, self.p.shape) * 0.2 * self.nsd
        self.test_points.set_data(self.p, self.t)

    def init_params(self):
        # np.random.seed(self.random_state)
        self.W1 = np.random.uniform(-0.5, 0.5, (self.S1, 1))
        self.b1 = np.random.uniform(-0.5, 0.5, (self.S1, 1))
        self.W2 = np.random.uniform(-0.5, 0.5, (1, self.S1))
        self.b2 = np.random.uniform(-0.5, 0.5, (1, 1))

    def forward(self, sample):
        a0 = sample.reshape(-1, 1)
        # Hidden Layer's Net Input
        n1 = np.dot(self.W1, a0) + self.b1
        #  Hidden Layer's Transformation
        a1 = self.logsigmoid(n1)
        # Output Layer's Net Input
        n2 = np.dot(self.W2, a1) + self.b2
        # Output Layer's Transformation
        return self.purelin(n2), n2, n1, a1, a0

    def train(self):
        alpha = 0.03

        error_train, dw1, db1, dw2, db2 = [], 0, 0, 0, 0
        for sample, target in zip(self.pp, self.tt):
            a, n2, n1, a1, a0 = self.forward(sample)
            e = target - a
            error_train.append(e)
            # error = np.append(error, e)
            # Output Layer
            F2_der = np.diag(self.purelin_der(n2).reshape(-1))
            s = -2 * np.dot(F2_der, e)  # (s2 = s)
            # Hidden Layer
            F1_der = np.diag(self.logsigmoid_der(n1).reshape(-1))
            s1 = np.dot(F1_der, np.dot(self.W2.T, s))

            if self.full_batch:
                dw1 += np.dot(s1, a0.T)
                db1 += s1
                dw2 += np.dot(s, a1.T)
                db2 += s
            else:
                # Updates the weights and biases
                # Hidden Layer
                self.W1 += -alpha * np.dot(s1, a0.T)
                self.b1 += -alpha * s1
                # Output Layer
                self.W2 += -alpha * np.dot(s, a1.T)
                self.b2 += -alpha * s

        if self.full_batch:
            # Updates the weights and biases
            # Hidden Layer
            self.W1 += -alpha * dw1
            self.b1 += -alpha * db1
            # Output Layer
            self.W2 += -alpha * dw2
            self.b2 += -alpha * db2

        error_test = []
        for sample, target in zip(self.p, self.t):
            a, n2, n1, a1, a0 = self.forward(sample)
            e = target - a
            error_test.append(e)

        return np.sum(np.abs(error_train)), np.sum(np.abs(error_test))

    def train_v2(self):

        self.mu /= 2

        self.a1 = np.kron(self.a1, np.ones((1, 1)))
        d2 = self.lin_delta(self.a2)
        d1 = self.log_delta(self.a1, d2, self.W2)
        jac1 = self.marq(np.kron(self.pp.reshape(1, -1), np.ones((1, 1))), d1)
        jac2 = self.marq(self.a1, d2)
        jac = np.hstack((jac1, d1.T))
        jac = np.hstack((jac, jac2))
        jac = np.hstack((jac, d2.T))
        je = np.dot(jac.T, self.e.T)

        grad = np.sqrt(np.dot(je.T, je)).item()
        if grad < 1e-8:
            error_test = []
            for sample, target in zip(self.p, self.t):
                a, n2, n1, a1, a0 = self.forward(sample)
                e = target - a
                error_test.append(e)
            return self.error_prev, np.sum(np.abs(error_test))

        jj = np.dot(jac.T, jac)
        # Can't get this operation to produce the exact same results as MATLAB...
        dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
        dW1 = dw[:self.RS]
        db1 = dw[self.RS:self.RSS]
        dW2 = dw[self.RSS:self.RSS2].reshape(1, -1)
        db2 = dw[self.RSS2].reshape(1, 1)

        self.a1 = self.logsigmoid_stable(np.dot((self.W1 + dW1), self.pp.reshape(1, -1)) + self.b1 + db1)
        self.a2 = self.purelin(np.dot((self.W2 + dW2), self.a1) + self.b2 + db2)
        self.e = self.tt.reshape(1, -1) - self.a2
        error = np.dot(self.e, self.e.T).item()

        while error >= self.error_prev:

            try:

                self.mu *= 2
                if self.mu > 1e10:
                    break

                dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
                dW1 = dw[:self.RS]
                db1 = dw[self.RS:self.RSS]
                dW2 = dw[self.RSS:self.RSS2].reshape(1, -1)
                db2 = dw[self.RSS2].reshape(1, 1)

                self.a1 = self.logsigmoid_stable(np.dot((self.W1 + dW1), self.pp.reshape(1, -1)) + self.b1 + db1)
                self.a2 = self.purelin(np.dot((self.W2 + dW2), self.a1) + self.b2 + db2)
                self.e = self.tt.reshape(1, -1) - self.a2
                error = np.dot(self.e, self.e.T).item()

            except Exception as e:
                if str(e) == "Singular matrix":
                    print("The matrix was singular... Increasing mu 10-fold")
                    self.mu *= 2
                else:
                    raise e

        if error < self.error_prev:
            self.W1 += dW1
            self.b1 += db1
            self.W2 += dW2
            self.b2 += db2
            self.error_prev = error

        if self.error_prev <= 0.005:
            if self.error_goal_reached:
                print("Error goal reached!")
                self.error_goal_reached = None
            error_test = []
            for sample, target in zip(self.p, self.t):
                a, n2, n1, a1, a0 = self.forward(sample)
                e = target - a
                error_test.append(e)
            return self.error_prev, np.sum(np.abs(error_test))

        error_test = []
        for sample, target in zip(self.p, self.t):
            a, n2, n1, a1, a0 = self.forward(sample)
            e = target - a
            error_test.append(e)
        return self.error_prev, np.sum(np.abs(error_test))

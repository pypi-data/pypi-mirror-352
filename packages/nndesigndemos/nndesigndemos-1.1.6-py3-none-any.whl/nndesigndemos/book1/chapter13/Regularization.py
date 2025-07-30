from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class Regularization(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Regularization, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Regularization", 13, "Click [Train] to train the\nnetwork on the noisy\ndata points.\n\n"
                                                "Use the slide bars to choose\nthe Regularization Ratio\nand the "
                                                "Noise Standard\nDeviation.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, description_coords=(535, 90, 450, 250))

        self.max_epoch = 500
        self.T = 2
        pp0 = np.linspace(-1, 1, 201)

        self.pp = np.linspace(-0.95, 0.95, 20)
        self.P = np.linspace(-1, 1, 100)

        self.ani, self.tt, self.clicked = None, None, False
        self.W1, self.b1, self.W2, self.b2 = None, None, None, None
        self.S1, self.random_state = 20, 42
        np.random.seed(self.random_state)

        self.make_plot(1, (20, 100, 470, 470))
        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Function Approxiation", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-1, 1)
        self.axes_1.set_ylim(-1.5, 1.5)
        self.axes_1.set_yticks([-1, -0.5, 0, 0.5, 1])
        self.axes_1.plot(pp0, np.sin(2 * np.pi * pp0 / self.T))
        self.net_approx, = self.axes_1.plot([], linestyle="--")
        self.train_points, = self.axes_1.plot([], marker='*', label="Train", linestyle="")
        self.axes_1.legend()
        self.canvas.draw()

        self.nsd = 1
        self.make_slider("slider_nsd", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (20, 580, 470, 50), self.slide,
                         "label_nsd", "Noise standard deviation: 1.0",
                         (180, 555, 200, 50))

        self.animation_speed = 0

        self.regularization_ratio = 0.25
        self.make_slider("slider_rer", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 25,
                         (20, 640, 470, 50), self.slide,
                         "label_rer", "Regularization Ratio: 0.25",
                         (200, 615, 200, 50))

        self.plot_train_test_data()
        self.canvas.draw()

        self.make_button("run_button", "Train", (self.x_chapter_button, 290, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.init_params()

    def animate_init(self):
        self.net_approx.set_data([], [])
        return self.net_approx,

    def on_animate(self, idx):
        alpha = 0.03
        nn_output = []
        for sample, target in zip(self.pp, self.tt):
            # Propagates the input forward
            # Reshapes input as 1x1
            a0 = sample.reshape(-1, 1)
            # Hidden Layer's Net Input
            n1 = np.dot(self.W1, a0) + self.b1
            #  Hidden Layer's Transformation
            a1 = self.logsigmoid(n1)
            # Output Layer's Net Input
            n2 = np.dot(self.W2, a1) + self.b2
            # Output Layer's Transformation
            a = self.purelin(n2)  # (a2 = a)
            nn_output.append(a)

            # Back-propagates the sensitivities
            # Compares our NN's output with the real value
            e = target - a
            # error = np.append(error, e)
            # Output Layer
            F2_der = np.diag(self.purelin_der(n2).reshape(-1))
            s = -2 * np.dot(F2_der, e)  # (s2 = s)
            # Hidden Layer
            F1_der = np.diag(self.logsigmoid_der(n1).reshape(-1))
            s1 = np.dot(F1_der, np.dot(self.W2.T, s))

            # Updates the weights and biases
            # Hidden Layer
            self.W1 += -alpha * np.dot(s1, a0.T)
            self.b1 += -alpha * s1
            # Output Layer
            self.W2 += -alpha * np.dot(s, a1.T)
            self.b2 += -alpha * s
        self.net_approx.set_data(self.pp, nn_output)
        return self.net_approx,

    def animate_init_v2(self):
        self.init_params()
        self.error_goal_reached = False
        self.a1 = self.tansig(np.dot(self.W1, self.pp.reshape(1, -1)) + self.b1)
        self.a2 = self.purelin(np.dot(self.W2, self.a1) + self.b2)
        self.e = self.tt.reshape(1, -1) - self.a2
        self.error_prev = np.dot(self.e, self.e.T).item()
        for param in [self.W1, self.b1, self.W2, self.b2]:
            self.error_prev += self.regularization_ratio * np.dot(param.reshape(1, -1), param.reshape(-1, 1)).item()
        self.mu = 0.01
        self.RS = self.S1 * 1
        self.RS1 = self.RS + 1
        self.RSS = self.RS + self.S1
        self.RSS1 = self.RSS + 1
        self.RSS2 = self.RSS + self.S1 * 1
        self.RSS3 = self.RSS2 + 1
        self.RSS4 = self.RSS2 + 1
        self.ii = np.eye(self.RSS4)
        self.net_approx.set_data([], [])
        return self.net_approx,

    def on_animate_v2(self, idx):
        """ Marqdt version """

        self.mu /= 10

        self.a1 = np.kron(self.a1, np.ones((1, 1)))
        d2 = self.lin_delta(self.a2)
        d1 = self.tan_delta(self.a1, d2, self.W2)
        jac1 = self.marq(np.kron(self.pp.reshape(1, -1), np.ones((1, 1))), d1)
        jac2 = self.marq(self.a1, d2)
        jac = np.hstack((jac1, d1.T))
        jac = np.hstack((jac, jac2))
        jac = np.hstack((jac, d2.T))
        je = np.dot(jac.T, self.e.T)

        grad = np.sqrt(np.dot(je.T, je)).item()
        # for param in [self.W1, self.b1, self.W2, self.b2]:
        #     grad += self.regularization_ratio * np.dot(param, param.T).item()
        if grad < 1e-7:
            self.net_approx.set_data(self.P, self.forward(self.P.reshape(1, -1)))
            return self.net_approx,

        jj = np.dot(jac.T, jac)
        # Can't get this operation to produce the exact same results as MATLAB...
        dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
        dW1 = dw[:self.RS]
        db1 = dw[self.RS:self.RSS]
        dW2 = dw[self.RSS:self.RSS2].reshape(1, -1)
        db2 = dw[self.RSS2].reshape(1, 1)

        self.a1 = self.tansig(np.dot((self.W1 + dW1), self.pp.reshape(1, -1)) + self.b1 + db1)
        self.a2 = self.purelin(np.dot((self.W2 + dW2), self.a1) + self.b2 + db2)
        self.e = self.tt.reshape(1, -1) - self.a2
        error = np.dot(self.e, self.e.T).item()
        for param in [self.W1 + dW1, self.b1 + db1, self.W2 + dW2, self.b2 + db2]:
            error += self.regularization_ratio * np.dot(param.reshape(1, -1), param.reshape(-1, 1)).item()

        while error >= self.error_prev:

            try:

                self.mu *= 10
                if self.mu > 1e10:
                    break

                dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
                dW1 = dw[:self.RS]
                db1 = dw[self.RS:self.RSS]
                dW2 = dw[self.RSS:self.RSS2].reshape(1, -1)
                db2 = dw[self.RSS2].reshape(1, 1)

                self.a1 = self.tansig(np.dot((self.W1 + dW1), self.pp.reshape(1, -1)) + self.b1 + db1)
                self.a2 = self.purelin(np.dot((self.W2 + dW2), self.a1) + self.b2 + db2)
                self.e = self.tt.reshape(1, -1) - self.a2
                error = np.dot(self.e, self.e.T).item()
                for param in [self.W1 + dW1, self.b1 + db1, self.W2 + dW2, self.b2 + db2]:
                    error += self.regularization_ratio * np.dot(param.reshape(1, -1), param.reshape(-1, 1)).item()

            except Exception as e:
                if str(e) == "Singular matrix":
                    print("The matrix was singular... Increasing mu 10-fold")
                    self.mu *= 10
                else:
                    raise e

        if error < self.error_prev:
            self.W1 += dW1
            self.b1 += db1
            self.W2 += dW2
            self.b2 += db2
            self.error_prev = error

        if self.error_prev <= 0:
            if self.error_goal_reached:
                print("Error goal reached!")
                self.error_goal_reached = None
            self.net_approx.set_data(self.P, self.forward(self.P.reshape(1, -1)))
            return self.net_approx,

        self.net_approx.set_data(self.P, self.forward(self.P.reshape(1, -1)))
        return self.net_approx,

    def forward(self, p_in):
        a1 = self.tansig(np.dot(self.W1, p_in) + self.b1)
        return self.purelin(np.dot(self.W2, a1) + self.b2)

    def on_run(self):
        self.clicked = True
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.run_animation()

    def run_animation(self):
        self.ani = FuncAnimation(self.figure, self.on_animate_v2, init_func=self.animate_init_v2, frames=self.max_epoch,
                                 interval=self.animation_speed, repeat=False, blit=True)

    def plot_train_test_data(self):
        self.tt = np.sin(2 * np.pi * self.pp / self.T) + np.random.uniform(-2, 2, self.pp.shape) * 0.2 * self.nsd
        self.train_points.set_data(self.pp, self.tt)

    def slide(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        # np.random.seed(self.random_state)
        self.nsd = float(self.slider_nsd.value() / 10)
        self.label_nsd.setText("Noise standard deviation: " + str(self.nsd))
        self.plot_train_test_data()
        # self.animation_speed = int(self.slider_anim_speed.value()) * 100
        # self.label_anim_speed.setText("Animation Delay: " + str(self.animation_speed) + " ms")
        self.regularization_ratio = int(self.slider_rer.value()) / 100
        self.label_rer.setText("Regularization Ratio: " + str(self.regularization_ratio))
        self.net_approx.set_data([], [])
        self.canvas.draw()
        # if self.clicked:
        #     self.run_animation()

    def init_params(self):
        np.random.seed(self.random_state)
        self.W1 = np.random.uniform(-0.5, 0.5, (self.S1, 1))
        self.b1 = np.random.uniform(-0.5, 0.5, (self.S1, 1))
        self.W2 = np.random.uniform(-0.5, 0.5, (1, self.S1))
        self.b2 = np.random.uniform(-0.5, 0.5, (1, 1))

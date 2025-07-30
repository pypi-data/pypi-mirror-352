from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class NonlinearOptimization(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(NonlinearOptimization, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Nonlinear Optimization", 17, "\n\n\nUse the slide bars to\nchoose the number of\nneurons in the"
                                                        " hidden\nlayer and the difficulty\nof the function.\n\nSelect a Weight"
                                                        "\nInizialization method.\n\nClick [Train] to train the\nRadial-basis network\n"
                                                        "(orange function) on the\nblue function.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", None)

        self.make_plot(1, (25, 100, 470, 320))
        self.make_plot(2, (25, 410, 470, 160))

        self.error_goal_reached = False
        self.error_prev = 1000
        self.ani, self.ani2 = None, None

        self.S1 = 4
        self.diff = 1
        self.W1, self.b1, self.W2, self.b2 = None, None, None, None
        self.p = np.linspace(-2, 2, 100)
        self.f_to_approx = lambda p: 1 + np.sin(np.pi * p * self.diff / 4)

        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xlim(-2, 2)
        self.axis.set_ylim(-2, 4)
        self.axis.set_xticks([-2, -1, 0, 1, 2])
        self.axis.set_yticks([-2, -1, 0, 1, 2, 3, 4])
        self.axis.plot(np.linspace(-2, 2, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_title("Function Approximation")
        self.axis.set_ylabel("Target")
        self.data_to_approx, = self.axis.plot([], label="Function to Approximate")
        self.net_approx, = self.axis.plot([], label="Network Approximation")

        self.figure2.set_tight_layout(True)
        self.axis2 = self.figure2.add_subplot(1, 1, 1)
        self.axis2.set_xlim(-2, 2)
        self.axis2.set_ylim(0, 1)
        self.axis2.set_xticks([-2, -1, 0, 1, 2])
        self.axis2.set_yticks([0, 0.5])
        self.axis2.set_xlabel("Input")
        self.axis2.set_ylabel("$a^1$")
        self.axis2.yaxis.set_label_coords(-0.025, 1)

        # self.lines = []
        self.lines_anim, self.lines_anim_2 = [], []

        self.make_label("label_s11", "2", (40, 550, 20, 50))
        self.make_label("label_s12", "9", (475, 550, 20, 50))
        self.make_label("label_s1", "Number of Hidden Neurons S1: 4", (170, 550, 200, 50))
        self.make_label("label_diff1", "1", (40, 610, 20, 50))
        self.make_label("label_diff2", "9", (475, 610, 20, 50))
        self.make_label("label_diff", "Difficulty index: 1", (210, 610, 200, 50))
        self.make_slider("slider_s1", QtCore.Qt.Orientation.Horizontal, (2, 9), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 4, (20, 580, 480, 50), self.slide)
        self.make_slider("slider_diff", QtCore.Qt.Orientation.Horizontal, (1, 9), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 1, (20, 635, 480, 50), self.slide)

        self.make_button("run_button", "Train", (self.x_chapter_button, 370, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.make_combobox(1, ["Lin. Least Squares", "Orth. Least Squares", "Random Weights"],
                           (self.x_chapter_button - 10, 425, self.w_chapter_button + 10, 50), self.change_init,
                           "label_init_method", "Initialization Method", (self.x_chapter_button + 10, 425 - 20, self.w_chapter_button, 50))

        self.change_init(0)

    def plot_f(self):
        self.data_to_approx.set_data(self.p, 1 + np.sin(np.pi * self.p * self.diff / 4))

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        if self.ani2 and self.ani2.event_source:
            self.ani2.event_source.stop()

    def change_init(self, idx):
        self.ani_stop()
        self.idx = idx
        self.init_params()

    def init_params(self):
        if self.idx == 0:
            n_points = self.S1
            d1 = (2 - -2) / (n_points - 1)
            p = np.arange(-2, 2 + 0.0001, d1)
            t = 1 + np.sin(np.pi * p * self.diff / 4)
            self.W1, self.b1, self.W2, self.b2 = self.rb_ls(p, t, self.S1)
        elif self.idx == 1:
            n_points = self.S1
            d1 = (2 - -2) / (n_points - 1)
            p = np.arange(-2, 2 + 0.0001, d1)
            t = 1 + np.sin(np.pi * p * self.diff / 4)
            self.W1, self.b1, self.W2, self.b2, _, _, _ = self.rb_ols(p, t, np.copy(p), np.ones(p.shape), self.S1)
        elif self.idx == 2:
            self.W1 = 2 * np.random.uniform(0, 1, (self.S1, 1)) - 0.5
            self.b1 = 2 * np.random.uniform(0, 1, (self.S1, 1)) - 0.5
            self.W2 = 2 * np.random.uniform(0, 1, (1, self.S1)) - 0.5
            self.b2 = 2 * np.random.uniform(0, 0, (1, 1)) - 0.5
        if len(self.W1) < self.S1:
            self.W1 = np.vstack((self.W1, np.zeros((1, self.S1 - len(self.W1)))))
            self.b1 = np.vstack((self.b1, np.zeros((1, self.S1 - len(self.b1)))))
            self.W2 = np.hstack((self.W2, np.zeros((1, self.S1 - self.W2.shape[1]))))
        self.W1_i, self.b1_i, self.W2_i, self.b2_i = self.W1, self.b1, self.W2, self.b2
        self.graph()

    def slide(self):
        self.error_goal_reached = False
        self.error_prev = 1000
        self.ani_stop()
        slider_s1 = self.slider_s1.value()
        if self.S1 != slider_s1:
            self.S1 = slider_s1
            self.init_params()
        slider_diff = self.slider_diff.value()
        if self.diff != slider_diff:
            self.diff = slider_diff
            self.init_params()
        self.label_s1.setText("Number of Hidden Neurons S1: {}".format(self.S1))
        self.label_diff.setText("Difficulty Index: {}".format(self.diff))
        self.f_to_approx = lambda p: 1 + np.sin(np.pi * p * self.diff / 4)

    def on_run(self):
        self.ani_stop()
        n_epochs = 200
        self.ani = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=n_epochs,
                                 interval=0, repeat=False, blit=False)
        self.ani2 = FuncAnimation(self.figure2, self.on_animate_2, init_func=self.animate_init_2, frames=n_epochs,
                                  interval=0, repeat=False, blit=False)
        self.canvas.draw()
        self.canvas2.draw()

    def animate_init(self):
        self.W1, self.b1, self.W2, self.b2 = self.W1_i, self.b1_i, self.W2_i, self.b2_i
        self.graph()
        self.error_goal_reached = False
        # self.p2 = self.p
        # self.Q2 = len(self.p)
        # p2 = np.arange(-2, 2.01, 0.4 / self.diff)
        # self.p_ = self.p
        self.p_ = np.arange(-2, 2 + 0.1 / self.diff, 0.1 / self.diff)
        # self.Q2 = len(self.p)
        self.Q2 = len(self.p_)
        # self.p2 = np.repeat(self.p.reshape(1, -1), self.S1, 0)
        self.p2 = np.repeat(self.p_.reshape(1, -1), self.S1, 0)
        # A1 = exp(-(abs(pp2-W1*ones(1,Q2)).*(B1*ones(1,Q2))).^2);
        # %A2 = W2*A1+B2*ones(1,Q);
        # A2 = W2*A1 + B2*ones(1,Q2);
        self.a1 = np.exp(-(np.abs(self.p2 - self.W1.dot(np.ones((1, self.Q2)))) * (self.b1.dot(np.ones((1, self.Q2))))) ** 2)
        self.a2 = self.W2.dot(self.a1) + self.b2.dot(np.ones((1, self.Q2)))
        # self.t = self.f_to_approx(self.p)
        # self.t = 1 + np.sin(np.pi * self.p * self.diff / 4)
        self.t = 1 + np.sin(np.pi * self.p_ * self.diff / 4)
        self.e = self.t - self.a2
        self.error_prev = np.dot(self.e, self.e.T).item()
        self.mu = 0.01
        self.mingrad = 0.001
        self.RS = self.S1 * 1
        self.RS1 = self.RS + 1
        self.RSS = self.RS + self.S1
        self.RSS1 = self.RSS + 1
        self.RSS2 = self.RSS + self.S1 * 1
        self.RSS3 = self.RSS2 + 1
        self.RSS4 = self.RSS2 + 1
        self.ii = np.eye(self.RSS4)
        self.net_approx.set_data([], [])
        # return self.net_approx,

    def on_animate(self, idx):
        """ Marqdt version """

        self.mu /= 10

        self.a1 = np.kron(self.a1, np.ones((1, 1)))
        d2 = self.lin_delta(self.a2)
        SS2 = -2 * (np.abs(self.p2 - self.W1.dot(np.ones((1, self.Q2)))) * (self.b1.dot(np.ones((1, self.Q2))))) * self.a1 * (self.W2.T.dot(d2))
        den = np.abs(self.p2 - self.W1.dot(np.ones((1, self.Q2))))
        flg = (den != 0)
        den = den + np.logical_not(flg) * 1
        d1 = SS2 * ((self.b1.dot(np.ones((1, self.Q2)))) * (self.W1.dot(np.ones((1, self.Q2))) - self.p2)) * (flg * 1) / den
        d1b = SS2 * np.abs(self.p2 - self.W1.dot(np.ones((1, self.Q2))))
        jac1 = d1.T
        jac2 = self.marq(self.a1, d2)
        jac = np.hstack((jac1, d1b.T))
        jac = np.hstack((jac, jac2))
        jac = np.hstack((jac, d2.T))
        je = np.dot(jac.T, self.e.T)

        # grad = np.sqrt(np.dot(je.T, je)).item()
        # if grad < self.mingrad:
        #     self.net_approx.set_data(self.p_.reshape(-1), self.a2.reshape(-1))
        #     self.ani_stop()
        #     return
            # return self.net_approx,

        jj = np.dot(jac.T, jac)
        try:
            dw = -np.dot(np.linalg.inv(jj + self.mu * self.ii), je)
        except:
            return
        dW1 = dw[:self.RS]
        db1 = dw[self.RS:self.RSS]
        dW2 = dw[self.RSS:self.RSS2].reshape(1, -1)
        db2 = dw[self.RSS2].reshape(1, 1)

        self.a1 = np.exp(-(np.abs(self.p2 - (self.W1 + dW1).dot(np.ones((1, self.Q2)))) * ((self.b1 + db1).dot(np.ones((1, self.Q2))))) ** 2)
        self.a2 = (self.W2 + dW2).dot(self.a1) + (self.b2 + db2).dot(np.ones((1, self.Q2)))
        self.e = self.t - self.a2
        error = np.dot(self.e, self.e.T).item()

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

                self.a1 = np.exp(-(np.abs(self.p2 - (self.W1 + dW1).dot(np.ones((1, self.Q2)))) * ((self.b1 + db1).dot(np.ones((1, self.Q2))))) ** 2)
                self.a2 = (self.W2 + dW2).dot(self.a1) + (self.b2 + db2).dot(np.ones((1, self.Q2)))
                self.e = self.t - self.a2
                error = np.dot(self.e, self.e.T).item()

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
            self.b2 += db2.item()
            self.error_prev = error

        pp = np.repeat(self.p_.reshape(1, -1), self.S1, 0)
        n12 = np.abs(pp - np.dot(self.W1, np.ones((1, self.Q2)))) * np.dot(self.b1, np.ones((1, self.Q2)))
        a12 = np.exp(-n12 ** 2)
        a22 = np.dot(self.W2, a12) + self.b2
        temp = np.vstack((np.dot(self.W2.T, np.ones((1, self.Q2))) * a12, self.b2 * np.ones((1, self.Q2))))
        for i in range(len(temp)):
            self.lines_anim[i].set_data(self.p_, temp[i])
        for i in range(len(a12)):
            self.lines_anim_2[i].set_data(self.p_, a12[i])

        if self.error_prev <= 0.005:
            if self.error_goal_reached:
                print("Error goal reached!")
                self.error_goal_reached = None
            self.net_approx.set_data(self.p_.reshape(-1), self.a2.reshape(-1))
            self.ani_stop()
            return
            # return self.net_approx,

        self.net_approx.set_data(self.p_.reshape(-1), self.a2.reshape(-1))
        # return self.net_approx,

    def animate_init_2(self):
        return

    def on_animate_2(self, idx):
        return

    def graph(self):

        """self.axis.clear()
        self.axis2.clear()

        self.axis.set_xlim(-2, 2)
        self.axis.set_ylim(-2, 4)
        self.axis.set_xticks([-2, -1, 0, 1, 2])
        self.axis.set_yticks([-2, -1, 0, 1, 2, 3, 4])
        self.axis.plot(np.linspace(-2, 2, 10), [0] * 10, color="black", linestyle="--", linewidth=0.2)
        self.axis.set_title("Function Approximation")
        self.axis.set_ylabel("Target")
        self.data_to_approx, = self.axis.plot([], label="Function to Approximate")
        self.net_approx, = self.axis.plot([], label="Network Approximation")
        self.plot_f()

        self.axis2.set_xlim(-2, 2)
        self.axis2.set_ylim(0, 1)
        self.axis2.set_xticks([-2, -1, 0, 1, 2])
        self.axis2.set_yticks([0, 0.5])
        self.axis2.set_xlabel("Input")
        self.axis2.set_ylabel("$a^1$")
        self.axis2.yaxis.set_label_coords(-0.025, 1)"""

        W1, b1, W2, b2 = self.W1, self.b1, self.W2, self.b2
        S1 = self.S1
        n_points = self.S1
        # if n_points > 1:
        #     d1 = (2 - -2) / (n_points - 1)
        # else:
        #     d1 = (2 - -2) / (S1 - 1)
        d1 = (2 - -2) / (n_points - 1)
        p = np.arange(-2, 2 + 0.0001, d1)
        t = 1 + np.sin(np.pi * p * self.diff / 4)

        total = 2 - -2
        Q = len(p)
        pp = np.repeat(p.reshape(1, -1), S1, 0)

        n1 = np.abs(pp - np.dot(W1, np.ones((1, Q)))) * np.dot(b1, np.ones((1, Q)))
        a1 = np.exp(-n1 ** 2)
        a2 = np.dot(W2, a1) + b2

        p2 = np.arange(-2, 2 + total / 1000, total / 1000)
        Q2 = len(p2)
        self.Q2 = Q2
        self.p2 = p2

        pp2 = np.repeat(p2.reshape(1, -1), S1, 0)
        n12 = np.abs(pp2 - np.dot(W1, np.ones((1, Q2)))) * np.dot(b1, np.ones((1, Q2)))
        a12 = np.exp(-n12 ** 2)
        a22 = np.dot(W2, a12) + b2
        # t_exact = 1 + np.sin(np.pi * p2 * self.diff / 5)

        temp = np.vstack((np.dot(W2.T, np.ones((1, Q2))) * a12, b2 * np.ones((1, Q2))))

        """if self.lines:
            for line in self.lines:
                line.pop(0).remove()
            self.lines = []
            
         for i in range(len(temp)):
            self.lines.append(self.axis.plot(p2, temp[i], linestyle="--", color="black", linewidth=0.5))
        for i in range(len(a12)):
            self.lines.append(self.axis2.plot(p2, a12[i], color="black"))"""

        while self.lines_anim:
            self.lines_anim.pop().remove()
        for i in range(len(temp)):
            self.lines_anim.append(self.axis.plot([], linestyle="--", color="black", linewidth=0.5)[0])
            self.lines_anim[i].set_data(p2, temp[i])

        while self.lines_anim_2:
            self.lines_anim_2.pop().remove()
        for i in range(len(a12)):
            self.lines_anim_2.append(self.axis2.plot([], color="black")[0])
            self.lines_anim_2[i].set_data(p2, a12[i])

        self.plot_f()
        self.net_approx.set_data(p2.reshape(-1), a22.reshape(-1))

        self.canvas.draw()
        self.canvas2.draw()

    @staticmethod
    def rb_ls(p, t, n):
        ro = 0
        delta = (2 - -2) / (n - 1)
        bias = 1.6652 / delta
        W1 = (np.arange(-2 + 0.01, 2 + 0.02, delta)).T.reshape(-1, 1)
        b1 = bias * np.ones(W1.shape)
        Q = len(p)
        pp = np.repeat(p.reshape(1, -1), n, 0)
        n1 = np.abs(pp - np.dot(W1, np.ones((1, Q)))) * np.dot(b1, np.ones((1, Q)))
        a1 = np.exp(-n1 ** 2)
        Z = np.vstack((a1, np.ones((1, Q))))
        x = np.dot(np.linalg.pinv(np.dot(Z, Z.T) + ro * np.eye(n + 1)), np.dot(Z, t.reshape(-1, 1)))
        W2, b2 = x[:-1].T, x[-1]
        return W1, b1, W2, b2

    @staticmethod
    def rb_ols(p, t, c, b, n):

        p = p.reshape(-1, 1)
        c = c.reshape(-1, 1)
        b = b.reshape(-1, 1)
        t = t.reshape(-1, 1)
        q = len(p)
        nc = len(c)
        o = np.zeros((nc + 1, 1))
        h = np.zeros((nc + 1, 1))
        rr = np.eye(nc + 1)
        indexT = list(range(nc + 1))
        if n > nc + 1:
            n = nc + 1
        bindex = []
        sst = np.dot(t.T, t).item()

        temp = np.dot(p.reshape(-1, 1), np.ones((1, nc))) - np.dot(np.ones((q, 1)), c.T.reshape(1, -1))
        btot = np.dot(np.ones((q, 1)), b.T.reshape(1, -1))
        uo = np.exp(-(temp * btot) ** 2)
        uo = np.hstack((uo, np.ones((q, 1))))
        u = uo
        m = u

        for i in range(nc + 1):
            ssm = np.dot(m[:, i].T, m[:, i])
            h[i] = np.dot(m[:, i].T, t) / ssm
            o[i] = h[i] ** 2 * ssm / sst
        o1, ind1 = np.max(o), np.argmax(o)
        of = o1
        hf = [h[ind1]]

        mf = m[:, ind1].reshape(-1, 1)
        ssmf = np.dot(mf.T, mf)
        u = np.delete(u, ind1, 1)
        if indexT[ind1] == nc:
            bindex = 1
            indf = []
        else:
            indf = indexT[ind1]
        indexT.pop(ind1)
        m = np.copy(u)

        for k in range(2, n + 1):
            o = np.zeros((nc + 2 - k, 1))
            h = np.zeros((nc + 2 - k, 1))
            r = np.zeros((q - k + 1, k, k))
            for i in range(q - k + 1):
                for j in range(k - 1):
                    if type(ssmf) == np.float64:
                        r[i, j, k - 1] = np.dot(mf, u[:, i]) / ssmf
                        m[:, i] = m[:, i] - r[i, j, k - 1] * mf[j]
                    else:
                        r[i, j, k - 1] = np.dot(mf[:, j].reshape(1, -1), u[:, i][..., None]) / ssmf[0, j]
                        m[:, i] = m[:, i] - r[i, j, k - 1] * mf[:, j]
                ssm = m[:, i].T.dot(m[:, i])
                h[i] = m[:, i].T.dot(t) / ssm
                o[i] = h[i] ** 2 * ssm / sst
            o1, ind1 = np.max(o), np.argmax(o)
            mf = np.hstack((mf, m[:, ind1].reshape(-1, 1)))
            if type(ssmf) == np.float64:
                ssmf = m[:, ind1].T.dot(m[:, ind1])
            else:
                try:
                    ssmf = np.vstack((ssmf.T, m[:, ind1].T.dot(m[:, ind1]))).T
                except:
                    print("!")
            of = np.hstack((of, o1))
            u = np.delete(u, ind1, 1)
            hf.append(h[ind1].item())
            for j in range(k - 1):
                rr[j, k - 1] = r[ind1, j, k - 1]
            if indexT[ind1] == nc + 1:
                bindex = k - 1
            else:
                indf = np.hstack((indf, indexT[ind1]))
            indexT.pop(ind1)
            m = np.copy(u)

        nn = len(hf)
        xx = np.zeros((nn, 1))
        xx[nn - 1] = hf[nn - 1]
        for i in list(range(nn - 1))[::-1]:
            xx[i] = hf[i]
            for j in list(range(i + 1, nn))[::-1]:
                xx[i] = xx[i] - rr[i, j] * xx[j]

        if len(indf) != 0:
            w1 = c[indf.astype(int)]
            b1 = b[indf.astype(int)]
        else:
            w1, b1 = [], []
        if bindex:
            if xx[:bindex - 1].size > 0:
                w2 = np.hstack((xx[:bindex - 1], xx[bindex: nn])).T
            else:
                w2 = xx[bindex: nn].T
            b2 = xx[0, bindex - 1]
            # indf = int(np.hstack((np.hstack((indf[:bindex - 1], nc + 1)), indf[bindex:])).item()) - 1
            # if indf:
            #     uu = uo[:, np.int(np.array(indf)) - 1]
            # else:
            #     uu = uo[:, []]
        else:
            b2 = 0
            w2 = xx.T
            # uu = uo[:, np.int(indf)]
        return w1, b1, w2, np.array(b2).astype(float), mf, of, indf

from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class OrthogonalLeastSquares(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(OrthogonalLeastSquares, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Orthogonal Least Squares", 17, "\n\nUse the slide bars to\nchoose the network or\nfunction values.\n\n"
                                                          "Click [Add Neuron] to\nincrease the size of\nHidden Layer.\n\n"
                                                          "The function is shown in\nblue and the network\nresponse in red.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", None)

        self.randseq = [-0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754,
                        -0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754]

        self.make_plot(1, (20, 100, 450, 300))
        self.make_plot(2, (20, 390, 450, 140))
        self.figure2.set_tight_layout(True)
        self.canvas2.draw()

        self.make_combobox(1, ["Yes", "No"], (self.x_chapter_usual, 420, self.w_chapter_slider, 50), self.change_auto_bias,
                           "label_f", "Auto Bias", (self.x_chapter_usual + 60, 420 - 20, 100, 50))
        self.auto_bias = True

        self.make_label("label_w1_1", "Hidden Neurons:", (35, 530, self.w_chapter_slider, 50))
        self.make_label("label_w1_2", "- Requested: 0", (45, 550, self.w_chapter_slider, 50))
        self.make_label("label_w1_3", "- Calculated: 0", (45, 570, self.w_chapter_slider, 50))
        self.S1 = 0

        self.make_slider("slider_b1_2", QtCore.Qt.Orientation.Horizontal, (2, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (170, 560, 150, 50), self.on_reset, "label_b1_2", "Number of Points: 10", (180, 530, 150, 50))
        self.make_slider("slider_b", QtCore.Qt.Orientation.Horizontal, (10, 1000), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 100,
                         (320, 560, 150, 50), self.on_reset, "label_b", "b: 1.00", (380, 530, 150, 50))

        self.make_slider("slider_w2_2", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 0,
                         (20, 630, 150, 50), self.on_reset, "label_w2_2", "Stdev Noise: 0.0", (50, 600, 150, 50))
        self.make_slider("slider_b2", QtCore.Qt.Orientation.Horizontal, (25, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 50,
                         (170, 630, 150, 50), self.on_reset, "label_b2", "Function Frequency: 0.50", (175, 600, 150, 50))
        self.make_slider("slider_fp", QtCore.Qt.Orientation.Horizontal, (0, 360), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 90,
                         (320, 630, 150, 50), self.on_reset, "label_fp", "Function Phase: 90", (340, 600, 150, 50))

        self.make_button("run_button", "Add Neuron", (self.x_chapter_button, 350, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.make_button("reset_button", "Reset", (self.x_chapter_button, 380, self.w_chapter_button, self.h_chapter_button), self.on_reset)

        self.graph(plot_red=False)

    def on_reset(self):
        self.S1 = 0
        self.label_w1_2.setText("- Requested: 0")
        self.label_w1_3.setText("- Calculated: 0")
        self.graph()

    def on_run(self):
        """Add a neuron and update the graph"""
        self.S1 += 1
        self.label_w1_2.setText("- Requested: " + str(self.S1))
        # Note: The actual calculated neurons will be determined in graph()
        # and updated there, not here
        self.graph()

    def graph(self, plot_red=True):
        axis = self.figure.add_subplot(1, 1, 1)
        axis.clear()
        axis.set_xlim(-2, 2)
        axis.set_ylim(-2, 4)
        axis.set_xticks([-2, -1, 0, 1])
        axis.set_yticks([-2, -1, 0, 1, 2, 3])
        axis.plot(np.linspace(-2, 2, 10), [0]*10, color="black", linestyle="--", linewidth=0.2)
        axis.set_title("Function Approximation")
        axis.set_xlabel("$p$")
        axis.xaxis.set_label_coords(1, -0.025)
        axis.set_ylabel("$a^2$")
        axis.yaxis.set_label_coords(-0.025, 1)

        axis2 = self.figure2.add_subplot(1, 1, 1)
        axis2.clear()
        axis2.set_xlim(-2, 2)
        axis2.set_ylim(0, 1)
        axis2.set_xticks([-2, -1, 0, 1])
        axis2.set_yticks([0, 0.5])
        axis2.set_xlabel("$p$")
        axis2.xaxis.set_label_coords(1, -0.025)
        axis2.set_ylabel("$a^1$")
        axis2.yaxis.set_label_coords(-0.025, 1)

        if self.auto_bias:
            bias = 1
            self.slider_b.setValue(bias * 100)
            self.label_b.setText("b: 1.00")
        else:
            bias = self.get_slider_value_and_update(self.slider_b, self.label_b, 1 / 100, 2)
        n_points = self.get_slider_value_and_update(self.slider_b1_2, self.label_b1_2)
        sigma = self.get_slider_value_and_update(self.slider_w2_2, self.label_w2_2, 1 / 10, 2)
        freq = self.get_slider_value_and_update(self.slider_b2, self.label_b2, 1 / 100, 2)
        phase = self.get_slider_value_and_update(self.slider_fp, self.label_fp)

        d1 = (2 - -2) / (n_points - 1)
        p = np.arange(-2, 2 + 0.0001, d1)
        t = np.sin(2 * np.pi * (freq * p + phase / 360)) + 1 + sigma * np.array(self.randseq[:len(p)])
        c = np.copy(p)
        if self.auto_bias:
            b = np.ones(p.shape)
        else:
            b = np.ones(p.shape) * bias
        
        # The requested neuron count shouldn't exceed data points + 1 (include bias term)
        effective_n = min(self.S1, len(p) + 1)
        W1, b1, W2, b2 = self.rb_ols(p, t, c, b, effective_n)

        # Update the calculated neuron count in the display
        if isinstance(W1, np.float64) or len(W1) == 0:
            S1 = 0
        else:
            S1 = len(W1)
        
        self.label_w1_3.setText("- Calculated: " + str(S1))
        
        total = 2 - -2

        p2 = np.arange(-2, 2 + total / 1000, total / 1000)
        Q2 = len(p2)
        
        # Calculate network response for fine grid
        if S1 == 0:
            a12 = np.zeros((1, Q2))
            a22 = b2 * np.ones((1, Q2))
        else:
            try:
                pp2 = np.repeat(p2.reshape(1, -1), S1, 0)
                n12 = np.abs(pp2 - np.dot(W1.reshape(-1, 1), np.ones((1, Q2)))) * np.dot(b1.reshape(-1, 1), np.ones((1, Q2)))
                a12 = np.exp(-n12 ** 2)
                a22 = np.dot(W2.reshape(1, -1), a12) + b2 * np.ones((1, Q2))
            except:
                # Fallback if there's an issue with calculations
                a12 = np.zeros((1, Q2))
                a22 = b2 * np.ones((1, Q2))
        
        t_exact = np.sin(2 * np.pi * (freq * p2 + phase / 360)) + 1
        
        # Calculate individual neuron contributions
        if S1 == 0:
            temp = b2 * np.ones((1, Q2))
        else:
            try:
                # Direct calculation of individual contributions
                indiv_contribs = []
                for i in range(S1):
                    indiv_contribs.append(W2[i] * a12[i, :])
                temp = np.vstack((indiv_contribs, b2 * np.ones((1, Q2))))
            except:
                temp = b2 * np.ones((1, Q2))
        
        axis.scatter(p, t, color="white", edgecolor="black")
        for i in range(len(temp)):
            axis.plot(p2, temp[i], linestyle="--", color="black", linewidth=0.5)
        axis.plot(p2, t_exact, color="blue", linewidth=2)
        if plot_red:
            axis.plot(p2, a22.reshape(-1), color="red", linewidth=1)
        if S1 == 0:
            axis2.plot(p2, [0] * len(p2), color="black")
        else:
            for i in range(len(a12)):
                axis2.plot(p2, a12[i], color="black")

        self.canvas.draw()
        self.canvas2.draw()

    def change_auto_bias(self, idx):
        self.auto_bias = idx == 0
        self.graph()

    @staticmethod
    def rb_ols(p, t, c, b, n):
        """Orthogonal Least Squares algorithm for RBF networks"""
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

        # Generate all possible basis functions
        temp = np.dot(p, np.ones((1, nc))) - np.dot(np.ones((q, 1)), c.T)
        btot = np.dot(np.ones((q, 1)), b.T)
        uo = np.exp(-(temp * btot) ** 2)
        uo = np.hstack((uo, np.ones((q, 1))))
        u = uo.copy()
        m = u.copy()

        # Initial selection
        for i in range(nc + 1):
            ssm = np.dot(m[:, i].T, m[:, i])
            if ssm < 1e-10:
                h[i] = 0
                o[i] = 0
            else:
                h[i] = np.dot(m[:, i].T, t) / ssm
                o[i] = h[i] ** 2 * ssm / sst

        if np.max(o) <= 0:
            return np.array([]), np.array([]), np.array([0]), 0, np.array([]), np.array([]), np.array([])
            
        if np.max(o) == 0:
            ind1 = 0
            o1 = 1e-20
        else:
            o1, ind1 = np.max(o), np.argmax(o)
        of = o1
        hf = [h[ind1].item()]

        mf = m[:, ind1].reshape(-1, 1)
        
        if ind1 < u.shape[1]:
            u = np.delete(u, ind1, 1)
        
        if indexT[ind1] == nc:
            bindex = 1
            indf = []
        else:
            indf = np.array([indexT[ind1]])
            
        if ind1 < len(indexT):
            indexT.pop(ind1)
            
        m = u.copy()

        # Key change: Modify early stopping criteria to match MATLAB version
        # Instead of using a fixed threshold, continue until the maximum requested neurons
        # or until we run out of basis functions
        for k in range(2, n + 1):
            if m.shape[1] == 0:
                break
                
            o = np.zeros((m.shape[1], 1))
            h = np.zeros((m.shape[1], 1))
            r = np.zeros((m.shape[1], k - 1))
            
            for i in range(m.shape[1]):
                for j in range(k - 1):
                    mf_dot = np.dot(mf[:, j].T, mf[:, j])
                    if mf_dot < 1e-15:  # Use a smaller threshold to allow more neurons
                        r[i, j] = 0
                    else:
                        r[i, j] = np.dot(mf[:, j].T, m[:, i]) / mf_dot
                    m[:, i] = m[:, i] - r[i, j] * mf[:, j]
                
                ssm = np.dot(m[:, i].T, m[:, i])
                if ssm < 1e-15:  # Use a smaller threshold to allow more neurons
                    h[i] = 0
                    o[i] = 0
                else:
                    h[i] = np.dot(m[:, i].T, t) / ssm
                    o[i] = h[i] ** 2 * ssm / sst
            
            # Only stop if actually zero contribution, not just very small
            if np.max(o) == 0:
                ind1 = 0
                o1 = 1e-20
            else:
                o1, ind1 = np.max(o), np.argmax(o)
            mf = np.hstack((mf, m[:, ind1].reshape(-1, 1)))
            of = np.append(of, o1)
            hf.append(h[ind1].item())
            
            for j in range(k - 1):
                rr[j, k - 1] = r[ind1, j]
            
            if ind1 < len(indexT) and indexT[ind1] == nc:
                bindex = k - 1
            else:
                if ind1 < len(indexT):
                    indf = np.append(indf, indexT[ind1])
            
            if ind1 < len(indexT):
                indexT.pop(ind1)
            if ind1 < u.shape[1]:
                u = np.delete(u, ind1, 1)
                
            m = u.copy()
            
            if m.shape[1] == 0:
                break

        # If no neurons selected, return empty result
        nn = len(hf)
        if nn == 0:
            return np.array([]), np.array([]), np.array([0]), 0, np.array([]), np.array([]), np.array([])
            
        # Convert selections to network parameters
        xx = np.zeros(nn)
        xx[nn - 1] = hf[nn - 1]
        
        # Back-substitution to get weights
        for i in range(nn - 2, -1, -1):
            xx[i] = hf[i]
            for j in range(i + 1, nn):
                xx[i] = xx[i] - rr[i, j] * xx[j]

        # Extract network parameters
        if len(indf) > 0:
            w1 = c[indf.astype(int)]
            b1 = b[indf.astype(int)]
        else:
            w1, b1 = np.array([]), np.array([])
            
        if bindex:
            if bindex > 1 and bindex <= nn:
                w2 = np.concatenate([xx[:bindex - 1], xx[bindex:]])
                b2 = xx[bindex - 1]
            else:
                w2 = xx[bindex:]
                b2 = xx[bindex - 1] if bindex - 1 >= 0 else 0
        else:
            b2 = 0
            w2 = xx
            
        return w1, b1, w2, b2

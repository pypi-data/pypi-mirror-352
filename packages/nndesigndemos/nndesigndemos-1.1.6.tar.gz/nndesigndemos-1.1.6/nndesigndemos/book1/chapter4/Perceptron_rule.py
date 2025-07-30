from PyQt6 import QtWidgets
import random
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class PerceptronRule(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PerceptronRule, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Perceptron rule", 4, "Left-click on the plot to add\na positive class.\n\nRight-click to add a\nnegative class.\n\n"
                                                "Click [Learn] to apply the\nperceptron rule to a\nsingle vector."
                                                "\n\nClick [Train] to apply the\nrule to all the vectors\nfor n_epochs.\n\n"
                                                "Click [Random] to initialize \nparameters randomly.",
                          PACKAGE_PATH + "Logo/Logo_Ch_4.svg", None, description_coords=(535, 80, 450, 400))

        self.make_label("error_label", "Error: ---", (320, 615, 50, 100))
        self.make_label("epoch_label", " -   Iterations so far: 0", (370, 615, 150, 100))
        self.make_label("warning_label", "", (20, 615, 400, 100))

        self.data = [(1, 2, 1), (0, -1, 0), (-1, 2, 0)]
        self.Weights = np.array([1, -0.8])
        self.bias = np.array([0])
        self.total_error = 0
        self.data_missclasified, error = [], 0
        for xy in self.data:
            t_hat = self.run_forward(np.array(xy[0:2]))
            if t_hat != xy[2]:
                self.data_missclasified.append(True)
                error += 1
            else:
                self.data_missclasified.append(False)
        self.total_error += error
        self.error_label.setText("Error: {}".format(self.total_error))

        self.total_epochs = 0
        self.R = 2  # Num input dimensions
        self.S = 1  # Num neurons

        # Add a plot
        self.make_plot(1, (5, 150, 510, 510))
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0.2, left=0.1)
        self.axes.set_xlim(-3, 3)
        self.axes.set_ylim(-3, 3)
        self.axes.tick_params(labelsize=10)
        # self.axes.set_xlabel("$p^1$", fontsize=10)
        # self.axes.xaxis.set_label_coords(0.5, 0.1)
        # self.axes.set_ylabel("$p^2$", fontsize=10)
        # self.axes.yaxis.set_label_coords(-0.05, 0.5)
        self.axes.plot([0] * 20, np.linspace(-3, 3, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes.plot(np.linspace(-3, 3, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.pos_line, = self.axes.plot([], 'mo', label="Positive Class")
        self.neg_line, = self.axes.plot([], 'cs', label="Negative Class")
        self.miss_line_pos, = self.axes.plot([], 'ro')
        self.miss_line_neg, = self.axes.plot([], 'rs')
        self.highlight_data, = self.axes.plot([], "*", markersize=16)
        self.highlight_data_miss, = self.axes.plot([], "*", markersize=16, color="red")
        self.decision, = self.axes.plot([], 'r-', label="Decision Boundary")
        self.axes.legend(loc='lower center', fontsize=int(8 * (self.w_ratio + self.h_ratio) / 2), framealpha=0.9, numpoints=1, ncol=2,
                         bbox_to_anchor=(0, -.28, 1, -.280), mode='expand')
        # self.axes.legend(loc='lower left', fontsize=8, numpoints=1, ncol=3, bbox_to_anchor=(-0.1, -.24, 1.1, -.280))
        self.axes.set_title("Single Neuron Perceptron")
        self.canvas.draw()
        # Add event handler for a mouseclick in the plot
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        self.make_combobox(1, ["1", "10", "100", "1000"], (self.x_chapter_usual, 560, self.w_chapter_slider, 50),
                           label_attr_name="whatever", label_str="Epochs to Run",
                           label_coords=(self.x_chapter_usual + 30, 560 - 20, self.w_chapter_slider, 50))

        self.make_combobox(2, ["Yes", "No"], (self.x_chapter_usual, 605, self.w_chapter_slider, 50),
                           label_attr_name="whatever", label_str="Use Bias",
                           label_coords=(self.x_chapter_usual + 30, 605 - 20, self.w_chapter_slider, 50))
        self.use_bias = self.comboBox2.currentText() == "Yes"

        self.make_button("run_button", "Train",
                         (self.x_chapter_button, 520, self.w_chapter_button, self.h_chapter_button), self.on_run)
        self.make_button("run_button", "Learn",
                         (self.x_chapter_button, 495, self.w_chapter_button, self.h_chapter_button), self.on_run_3)
        self.make_button("rerun_button", "Random",
                         (self.x_chapter_button, 470, self.w_chapter_button, self.h_chapter_button), self.on_reset)
        self.make_button("undo_click_button", "Undo Last Mouse Click",
                         (self.x_chapter_button, 445, self.w_chapter_button, self.h_chapter_button), self.on_undo_mouseclick)
        self.make_button("clear_button", "Clear Data",
                         (self.x_chapter_button, 420, self.w_chapter_button, self.h_chapter_button),
                         self.on_clear)

        self.ani1, self.ani2 = None, None
        self.learn = None

        # latex_w = self.mathTex_to_QPixmap("$W = [1.0 \quad -1.0]$", 6)
        # latex_w = self.mathTex_to_QPixmap("$W = [1.0 \quad -0.8]$", 10)
        # self.latex_w = QtWidgets.QLabel(self)
        # self.latex_w.setPixmap(latex_w)
        # self.latex_w.setGeometry((self.x_chapter_usual + 10) * self.w_ratio, 420 * self.h_ratio, 150 * self.w_ratio, 100 * self.h_ratio)
        # self.latex_w.setGeometry(50 * self.w_ratio, 80 * self.h_ratio, 300 * self.w_ratio, 100 * self.h_ratio)
        self.make_label("label_W", "W = [1.0  -0.8]", (70, 80, 300, 100), font_size=30)
        self.label_W.setStyleSheet("color:black")

        # latex_b = self.mathTex_to_QPixmap("$b = [0.0]$", 6)
        # latex_b = self.mathTex_to_QPixmap("$b = [0.0]$", 10)
        # self.latex_b = QtWidgets.QLabel(self)
        # self.latex_b.setPixmap(latex_b)
        # self.latex_b.setGeometry((self.x_chapter_usual + 10) * self.w_ratio, 450 * self.h_ratio, 150 * self.w_ratio, 100 * self.h_ratio)
        # self.latex_b.setGeometry(350 * self.w_ratio, 80 * self.h_ratio, 300 * self.w_ratio, 100 * self.h_ratio)
        self.make_label("label_b", "b = [0.0]", (320, 80, 300, 100), font_size=30)
        self.label_b.setStyleSheet("color:black")

        self.draw_decision_boundary()
        self.draw_data()
        self.canvas.draw()

    def draw_data(self):

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
        # self.canvas.draw()

    def draw_decision_boundary(self):
        lim = self.axes.get_xlim()
        X = np.linspace(lim[0], lim[1], 101)
        Y = self.find_decision_boundary(X)
        self.decision.set_data(X, Y)
        # self.canvas.draw()

    def clear_decision_boundary(self):
        self.decision.set_data([], [])
        # self.canvas.draw()

    def ani_stop(self):
        if self.ani1 and self.ani1.event_source:
            self.ani1.event_source.stop()
        if self.ani2 and self.ani2.event_source:
            self.ani2.event_source.stop()

    def on_mouseclick(self, event):
        """Add an item to the plot"""
        if event.xdata != None and event.xdata != None:
            self.data.append((event.xdata, event.ydata, 1 if event.button == 1 else 0))
            self.ani_stop()
            self.data_missclasified, error = [], 0
            for xy in self.data:
                t_hat = self.run_forward(np.array(xy[0:2]))
                if t_hat != xy[2]:
                    self.data_missclasified.append(True)
                    error += 1
                else:
                    self.data_missclasified.append(False)
            self.draw_data()
            self.canvas.draw()

    def on_clear(self):
        self.ani_stop()
        self.data = []
        # self.clear_decision_boundary()
        self.initialize_weights()
        self.total_epochs = 0
        self.update_run_status()
        self.draw_data()
        self.canvas.draw()

    def update_run_status(self):
        if self.total_epochs == 0:
            self.epoch_label.setText(" -   Iterations so far: 0")
        else:
            self.epoch_label.setText(" -   Iterations so far: {}".format(self.total_epochs))
        self.error_label.setText("Error: {}".format(self.total_error))

    def on_run(self):

        self.ani_stop()

        self.use_bias = self.comboBox2.currentText() == "Yes"
        if not self.use_bias:
            self.bias = np.array([0])

        if int(self.comboBox1.currentText()) > 1:

            if len(self.data) < 2:
                self.warning_label.setText("Please select at least two data points before training.")
            else:
                if len(np.unique([cls[2] for cls in self.data])) == 1:
                    self.warning_label.setText("Please select at least one data point of each class.")
                else:
                    self.warning_label.setText("")
                    # Do 10 epochs
                    for epoch in range(int(self.comboBox1.currentText())):

                        # training = self.data.copy()
                        # np.random.shuffle(training)
                        for d in self.data:
                            self.total_epochs += 1
                            self.train_one_iteration(np.array(d[0:2]), d[2])

                        # Calculate the error for the epoch
                        self.all_t_hat = np.array([self.run_forward(np.array(xy[0:2])) for xy in self.data])
                        self.total_error = abs(np.array([t[2] for t in self.data]) - self.all_t_hat).sum()

                        if self.total_error == 0:
                            break

                    self.data_missclasified, error = [], 0
                    for xy in self.data:
                        t_hat = self.run_forward(np.array(xy[0:2]))
                        if t_hat != xy[2]:
                            self.data_missclasified.append(True)
                            error += 1
                        else:
                            self.data_missclasified.append(False)
                    self.total_error = error
                    self.draw_data()

                    self.update_run_status()
                    self.draw_decision_boundary()

                    # self.latex_w.setPixmap(self.mathTex_to_QPixmap(
                    #     "$W = [{} \quad {}]$".format(round(self.Weights[0], 2), round(self.Weights[1], 2)), 10))
                    # self.latex_b.setPixmap(self.mathTex_to_QPixmap("$b = [{}]$".format(round(self.bias[0], 2)), 10))
                    self.label_W.setText("W = [{}  {}]".format(round(self.Weights[0], 1), round(self.Weights[1], 1)))
                    self.label_b.setText("b = [{}]".format(round(self.bias[0], 1)))

                    self.canvas.draw()


        else:

            self.learn = False
            self.ani1 = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init,
                                      frames=len(self.data) * 2 + 1,
                                      interval=1000, repeat=False, blit=False)
            self.canvas.draw()

    def on_run_2(self):
        self.ani_stop()
        self.learn = False
        self.ani1 = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=len(self.data) * 2 + 1,
                                  interval=1000, repeat=False, blit=False)
        self.canvas.draw()

    def on_run_3(self):
        self.ani_stop()
        self.learn = True
        random.shuffle(self.data)
        self.ani2 = FuncAnimation(self.figure, self.on_animate, init_func=self.animate_init, frames=3,
                                  interval=1000, repeat=False, blit=False)
        self.canvas.draw()

    def animate_init(self):
        # self.pos_line.set_data([], [])
        # self.neg_line.set_data([], [])
        # self.miss_line_pos.set_data([], [])
        # self.miss_line_neg.set_data([], [])
        # self.decision.set_data([], [])
        self.use_bias = self.comboBox2.currentText() == "Yes"
        if not self.use_bias:
            self.bias = np.array([0])
        self.all_t_hat = np.array([self.run_forward(np.array(xy[0:2])) for xy in self.data])
        self.total_error = abs(np.array([t[2] for t in self.data]) - self.all_t_hat).sum()
        # self.canvas.draw()
        return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss

    def on_animate(self, idx):
        """ GD version """

        if len(self.data) < 2:
            self.warning_label.setText("Please select at least two data points before training.")
            return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss
        else:
            if len(np.unique([cls[2] for cls in self.data])) == 1:
                self.warning_label.setText("Please select at least one data point of each class.")
                return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss
            else:
                self.warning_label.setText("")

                if self.total_error == 0:
                    self.warning_label.setText("The error is 0!")
                    return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss

                # training = self.data.copy()
                # np.random.shuffle(training)
                # for d in self.data:
                    # self.train_one_iteration(np.array(d[0:2]), d[2])
                # if idx > len(self.data) - 1:
                #     return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision
                # else:
                if self.learn and idx == 2:
                    self.highlight_data.set_data([], [])
                    self.highlight_data_miss.set_data([], [])
                    self.draw_decision_boundary()
                    return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss
                if idx == len(self.data) * 2:
                    self.highlight_data.set_data([], [])
                    self.highlight_data_miss.set_data([], [])
                    self.draw_decision_boundary()
                    return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss
                else:
                    if idx % 2 == 0:
                        t_hat = self.run_forward(np.array(self.data[int(idx / 2)][0:2]))
                        if t_hat != self.data[int(idx / 2)][2]:
                            self.highlight_data_miss.set_data([self.data[int(idx / 2)][0]], [self.data[int(idx / 2)][1]])
                        else:
                            self.highlight_data.set_data([self.data[int(idx / 2)][0]], [self.data[int(idx / 2)][1]])
                    else:
                        self.highlight_data.set_data([], [])
                        self.highlight_data_miss.set_data([], [])
                        self.train_one_iteration(np.array(self.data[idx // 2][0:2]), self.data[idx // 2][2])
                        self.total_epochs += 1

                # Calculate the error for the epoch
                self.all_t_hat = np.array([self.run_forward(np.array(xy[0:2])) for xy in self.data])
                self.total_error = abs(np.array([t[2] for t in self.data]) - self.all_t_hat).sum()

                self.update_run_status()
                self.draw_decision_boundary()
                self.data_missclasified, error = [], 0
                for xy in self.data:
                    t_hat = self.run_forward(np.array(xy[0:2]))
                    if t_hat != xy[2]:
                        self.data_missclasified.append(True)
                        error += 1
                    else:
                        self.data_missclasified.append(False)
                self.draw_data()

                self.epoch_label.setText(" -   Iterations so far: {}".format(self.total_epochs))
                self.error_label.setText("Error: {}".format(self.total_error))

                # self.latex_w.setPixmap(self.mathTex_to_QPixmap("$W = [{} \quad {}]$".format(round(self.Weights[0], 2), round(self.Weights[1], 2)), 10))
                # self.latex_b.setPixmap(self.mathTex_to_QPixmap("$b = [{}]$".format(round(self.bias[0], 2)), 10))
                self.label_W.setText("W = [{}  {}]".format(round(self.Weights[0], 1), round(self.Weights[1], 1)))
                self.label_b.setText("b = [{}]".format(round(self.bias[0], 1)))

                return self.pos_line, self.neg_line, self.miss_line_pos, self.miss_line_neg, self.decision, self.highlight_data, self.highlight_data_miss

    def on_reset(self):
        self.ani_stop()
        self.warning_label.setText("")
        self.initialize_weights()
        # self.latex_w.setPixmap(self.mathTex_to_QPixmap("$W = [{} \quad {}]$".format(round(self.Weights[0], 2), round(self.Weights[1], 2)), 10))
        # self.latex_b.setPixmap(self.mathTex_to_QPixmap("$b = [{}]$".format(round(self.bias[0], 2)), 10))
        self.label_W.setText("W = [{}  {}]".format(round(self.Weights[0], 1), round(self.Weights[1], 1)))
        self.label_b.setText("b = [{}]".format(round(self.bias[0], 1)))
        self.total_epochs = 0
        self.clear_decision_boundary()
        self.draw_decision_boundary()
        self.data_missclasified, error = [], 0
        for xy in self.data:
            t_hat = self.run_forward(np.array(xy[0:2]))
            if t_hat != xy[2]:
                self.data_missclasified.append(True)
                error += 1
            else:
                self.data_missclasified.append(False)
        self.total_error = error
        self.draw_data()
        self.update_run_status()
        self.canvas.draw()

    def on_undo_mouseclick(self):
        self.ani_stop()
        if self.data:
            self.data.pop()
            self.draw_data()
            self.canvas.draw()

    def run_forward(self, p):
        """Given an input of dimension R, run the network"""
        return self.hardlim(self.Weights.dot(p) + self.bias)

    def train_one_iteration(self, p, t):
        """Given one input of dimension R and its target, perform one training iteration.
        Update the weights and biases using the Perceptron learning Rule."""

        t_hat = self.run_forward(p)
        self.error = t - t_hat

        # Adjust weights and bias based on the error from this iteration
        self.Weights = self.Weights + self.error * p.T
        if self.use_bias:
            self.bias = self.bias + self.error
        return self.error

    def find_decision_boundary(self, x):
        """Returns the corresponding y value for the input x on the decision
        boundary"""
        return -(x * self.Weights[0] + self.bias) / \
               (self.Weights[1] if self.Weights[1] != 0 else .000001)

    def initialize_weights(self):
        self.ani_stop()
        self.Weights = (np.random.random(self.R) - 0.5) * 20
        self.bias = (np.random.random(self.S) - 0.5) * 20

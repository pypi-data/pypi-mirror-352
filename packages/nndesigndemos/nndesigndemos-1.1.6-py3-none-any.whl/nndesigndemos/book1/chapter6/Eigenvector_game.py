from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.pyplot as plt
from matplotlib import patches

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class EigenvectorGame(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(EigenvectorGame, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Eigenvector Game", 6, "Your job is to find\nthe two eigenvectors of an\nunknown transformation.\n\n"
                                                 "Click on the plot to draw a\nvector (in red) and see\nthe transformed vector.\n\n"
                                                 "If their directions are\nthe same or opposite,\nthe first eigenvector will\nshow up in green.\n\n"
                                                 "Repeat to find\nthe second eigenvector.",
                          PACKAGE_PATH + "Logo/Logo_Ch_6.svg", None, description_coords=(535, 100, 450, 350))

        self.make_plot(2, (150, 95, 210, 210))
        self.ax = self.figure2.add_subplot(1, 1, 1)

        if self.play_sound:
            self.initial_sound('start_sound', "Sound/dk-a2600_walk.wav")
            self.initial_sound('miss_sound', "Sound/smb_bump.wav")
            self.initial_sound('win_1_sound', "Sound/mb_coin.wav")
            self.initial_sound('win_2_sound', "Sound/npc-yc_mario-win.wav")
            self.initial_sound('lose_sound', "Sound/mb_die.wav")

        self.make_plot(1, (75, 300, 370, 370))
        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        # self.axes_1.set_title("Original Vectors", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-2, 2)
        self.axes_1.set_ylim(-2, 2)
        self.axes1_points = []
        self.axes1_v1 = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1)
        self.axes1_v2 = self.axes_1.quiver([0], [0], [0], [0],  units="xy", scale=1)
        self.axes1_eig1 = self.axes_1.quiver([0], [0], [0], [0],  units="xy", scale=1, color="green")
        self.eig1_found, self.slope1 = False, None
        self.axes1_eig2 = self.axes_1.quiver([0], [0], [0], [0],  units="xy", scale=1, color="green")
        self.eig2_found = False
        self.axes_1.set_xticks([-2, -1, 0, 1])
        self.axes_1.set_yticks([-2, -1, 0, 1])
        self.axes_1.set_xlabel("$x$")
        self.axes_1.xaxis.set_label_coords(1, -0.025)
        self.axes_1.set_ylabel("$y$")
        self.axes_1.yaxis.set_label_coords(-0.025, 1)
        self.axes_1.plot([0] * 20, np.linspace(-2, 2, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_1.plot(np.linspace(-2, 2, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick1)

        self.make_slider("slider_n_tries", QtCore.Qt.Orientation.Vertical, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 10,
                         (590, 430, 100, 180), self.freeze, "label_n_tries", "Number of Tries Left: 10",
                         (540, 400, 150, 50))
        self.make_label("label_message", "", (150, 100, 400, 150))
        self.make_label("label_message1", "", (150, 200, 400, 150))
        self.make_button("button", "Restart", (self.x_chapter_button, 615, self.w_chapter_button, self.h_chapter_button), self.random_transform)
        self.A, self.eig_v1, self.eig_v2 = None, None, None
        self.play_start_sound = False
        self.random_transform()
        self.play_start_sound = True
        self.save_show_face()

    def save_show_face(self, draw_win=False):
        """fig, ax = plt.subplots()
        ax.set_axis_off()
        circle = plt.Circle((0.5, 0.5), 0.5, color="yellow", fill=True)
        ax.add_artist(circle)
        circle = plt.Circle((0.3, 0.65), 0.05, color="black", fill=True)
        ax.add_artist(circle)
        circle = plt.Circle((0.7, 0.65), 0.05, color="black", fill=True)
        ax.add_artist(circle)
        if self.n_tries > 5:
            arc = patches.Arc((0.5, 0.35), self.n_tries / 100, 0.6, 90, 90, 270, color="black", linewidth=10)
        elif self.n_tries < 5:
            if self.n_tries == 0:
                arc = patches.Arc((0.5, 0.35), 1 / (1 * 3), 0.6, 90, 270, 90, color="black", linewidth=10)
            else:
                arc = patches.Arc((0.5, 0.35), 1 / (self.n_tries * 3), 0.6, 90, 270, 90, color="black", linewidth=10)
        else:
            arc = patches.Arc((0.5, 0.35), 0.01, 0.6, 90, 270, 90, color="black", linewidth=10)
        ax.add_artist(arc)
        fig.savefig("temp.png", transparent=True)"""
        self.ax.clear()
        self.ax.set_axis_off()
        circle = plt.Circle((0.5, 0.5), 0.5, color="yellow", fill=True)
        self.ax.add_artist(circle)
        circle = plt.Circle((0.3, 0.65), 0.05, color="black", fill=True)
        self.ax.add_artist(circle)
        circle = plt.Circle((0.7, 0.65), 0.05, color="black", fill=True)
        self.ax.add_artist(circle)
        if draw_win:
            arc = patches.Arc((0.5, 0.35), 15 / 50, 0.6, angle=90, theta1=90, theta2=270, color="black", linewidth=3)
        else:
            if self.n_tries > 5:
                arc = patches.Arc((0.5, 0.35), self.n_tries / 50, 0.6, angle=90, theta1=90, theta2=270, color="black", linewidth=3)
            elif self.n_tries < 5:
                if self.n_tries == 0:
                    arc = patches.Arc((0.5, 0.35), 1 / (1 * 3), 0.6, angle=90, theta1=270, theta2=90, color="black", linewidth=3)
                else:
                    arc = patches.Arc((0.5, 0.35), 1 / (self.n_tries * 5), 0.6, angle=90, theta1=270, theta2=90, color="black", linewidth=3)
            else:
                arc = patches.Arc((0.5, 0.35), 0.01, 0.6, angle=90, theta1=270, theta2=90, color="black", linewidth=3)
        self.ax.add_artist(arc)
        self.canvas2.draw()

    def freeze(self):
        self.slider_n_tries.setValue(self.n_tries)

    def random_transform(self):
        if self.play_start_sound:
            if self.play_sound:
                self.start_sound.play()
        self.label_message.setText("")
        self.label_message1.setText("")
        self.n_tries = 10
        self.label_n_tries.setText("Number of Tries Left: 10")
        self.slider_n_tries.setValue(10)
        self.clear_all()
        self.eig1_found, self.slope1, self.eig2_found = False, None, False
        self.axes1_eig1.set_UVC(0, 0)
        self.axes1_eig2.set_UVC(0, 0)
        self.canvas.draw()
        self.label_message.setText("")
        self.A = np.eye(2)
        while np.any(np.abs(np.array([self.A[0, 1], self.A[1, 0]])) < 0.15):
            angle1 = np.random.normal() * 360 - 180
            if angle1 <= -180:
                angle1 = 180
            elif angle1 >= 180:
                angle1 = 180
            else:
                angle1 = round(angle1, 1)
                while angle1 % 10 == 0:
                    angle1 += 1
            v1 = 0.8 * np.array([[np.cos(angle1 * 0.0175)], [np.sin(angle1 * 0.0175)]])
            angle2 = angle1
            while np.sum(angle2 == (angle1 + np.array([0, 170, 180, 190, 350, -170, -180, -190, -350]))) > 0:
                angle2 = np.random.normal() * 360 - 180
                if angle2 <= -180:
                    angle2 = 180
                elif angle2 >= 180:
                    angle2 = 180
                else:
                    angle2 = round(angle2, 1)
                    while angle2 % 10 == 0:
                        angle2 += 1
            v2 = 0.8 * np.array([[np.cos(angle2 * 0.0175)], [np.sin(angle2 * 0.0175)]])
            m = np.array([[v1[0, 0], v2[0, 0]], [v1[1, 0], v2[1, 0]]])
            e = (0.4 * np.random.uniform(0, 1, (2, 1)) + 0.3) * np.sign(np.random.uniform(0, 1, (2, 1)) - 0.5)
            self.A = np.dot(m, np.dot(np.diag(e.reshape(-1)), np.linalg.inv(m)))
            e, v = np.linalg.eig(self.A)
        self.eig_v1, self.eig_v2 = np.array([[v[0, 0]], [v[1, 0]]]), np.array([[v[0, 1]], [v[1, 1]]])
        self.axes_1.set_title("")
        self.save_show_face()
        self.canvas.draw()
        self.canvas2.draw()

    def on_mouseclick1(self, event):
        if event.xdata != None and event.xdata != None and not self.eig2_found:
            if self.n_tries > 0:
                self.n_tries -= 1
                self.label_n_tries.setText("Number of Tries Left: {}".format(self.n_tries))
                self.slider_n_tries.setValue(self.n_tries)
                self.save_show_face()
                self.clear_all()
                self.axes1_points = [(round(event.xdata, 2), round(event.ydata, 2))]
                self.draw_vector()

    def draw_vector(self):
        x_trimmed1, y_trimmed1 = self.axes1_points[0][0], self.axes1_points[0][1]
        while abs(x_trimmed1) > 2:
            x_trimmed1 /= 1.1
            y_trimmed1 /= 1.1
        self.axes1_v1.set_UVC(x_trimmed1, y_trimmed1)
        slope_v1 = self.axes1_points[0][1] / self.axes1_points[0][0]
        v_transformed = np.dot(self.A, np.array([[self.axes1_points[0][0]], [self.axes1_points[0][1]]]))
        slope_v1_t = v_transformed[1, 0] / v_transformed[0, 0]
        x_trimmed, y_trimmed = v_transformed[0, 0], v_transformed[1, 0]
        while abs(x_trimmed) > 2:
            x_trimmed /= 1.1
            y_trimmed /= 1.1
        self.axes1_v2.set_UVC(x_trimmed, y_trimmed)
        if not self.slope1:
            if 1.2 > abs(slope_v1 / slope_v1_t) > 0.8:
                self.axes1_eig1.set_UVC(x_trimmed1, y_trimmed1)
                self.eig1_found, self.slope1 = True, slope_v1
                self.axes_1.set_title("First eigenvector found! 1 left!")
                # self.label_message1.setText("First eigenvector found!")
                self.axes1_v1.set_color("black")
                if self.play_sound:
                    self.win_1_sound.play()
            else:
                self.axes1_v1.set_color("red")
                if self.play_sound:
                    self.miss_sound.play()
        else:
            if (1.2 < abs(slope_v1 / self.slope1) or abs(slope_v1 / self.slope1) < 0.8) and 1.2 > abs(slope_v1 / slope_v1_t) > 0.8:
                self.axes1_eig2.set_UVC(x_trimmed1, y_trimmed1)
                self.eig2_found = True
                self.clear_all()
                # self.label_message1.setText("Second eigenvector found!")
                self.axes_1.set_title("Second eigenvector found! You won :D")
                # self.label_message.setText("You won :D. Click Restart to play again")
                self.axes1_v1.set_color("black")
                self.save_show_face(draw_win=True)
                if self.play_sound:
                    self.win_2_sound.play()
            else:
                self.axes1_v1.set_color("red")
                if self.play_sound:
                    self.miss_sound.play()
        if not self.eig2_found and self.n_tries == 0:
            self.axes_1.set_title("You lost :(. Click Restart to try again")
            if self.play_sound:
                self.lose_sound.play()
            # self.label_message.setText("You lost :(. Click Restart to try again")
        self.canvas.draw()

    def clear_all(self):
        self.axes1_v1.set_UVC(0, 0)
        self.axes1_v2.set_UVC(0, 0)
        self.canvas.draw()

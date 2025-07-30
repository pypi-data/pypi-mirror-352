import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ReciprocalBasis(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ReciprocalBasis, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Reciprocal Basis", 5, "\nClick on the plot to\ndefine the basis {v1, v2}\nand the vector x to be\nexpanded"
                                                 " in terms\nof {v1, v2}."
                                                 "\n\nClick [Expand] to expand\na new vector.\n\nClick [Start] to\ndefine a new basis.",
                          PACKAGE_PATH + "Logo/Logo_Ch_5.svg", None)

        self.make_plot(1, (115, 100, 290, 290))
        self.make_plot(2, (115, 385, 290, 290))

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick1)
        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.fill_plots()
        self.axes1_points = []
        self.canvas.draw()
        self.canvas2.draw()

        self.make_label("label_explanation", "", (530, 315, 160, 200))
        self.make_label("label_warning", "", (510, 500, 150, 100))

        self.remove_vector = True
        self.make_button("button", "Expand", (self.x_chapter_button, 530, self.w_chapter_button, self.h_chapter_button),
                         self.expand)
        self.make_button("button", "Start", (self.x_chapter_button, 500, self.w_chapter_button, self.h_chapter_button),
                         self.clear_all)

    def fill_plots(self):

        self.axes_1.set_title("Basis Vectors", fontdict={'fontsize': 10})
        self.axes_1.set_xlim(-2, 2)
        self.axes_1.set_ylim(-2, 2)
        self.axes1_v1 = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
        self.axes1_v2 = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
        self.text_v1, self.text_v2 = None, None
        self.axes1_s1 = self.axes_1.quiver([0], [0], [1], [0], units="xy", scale=1)
        self.axes_1.text(1.2, 0, "s1")
        self.axes1_s2 = self.axes_1.quiver([0], [0], [0], [1], units="xy", scale=1)
        self.axes_1.text(0, 1.2, "s1")
        self.axes1_x = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, color="r")
        self.text_x = None
        self.axes1_proj = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, headlength=0, headwidth=0,
                                             headaxislength=0)
        self.axes1_proj1 = self.axes_1.quiver([0], [0], [0], [0], units="xy", scale=1, headlength=0, headwidth=0,
                                              headaxislength=0)
        self.axes_1.plot([0] * 20, np.linspace(-2, 2, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_1.plot(np.linspace(-2, 2, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.axes1_proj_line, = self.axes_1.plot([], "-")
        self.text_start = self.axes_1.text(-1.1, -0.5, "<CLICK ON ME>")

        self.axes_2.set_title("Vector Expansion", fontdict={'fontsize': 10})
        self.axes_2.set_xlim(-2, 2)
        self.axes_2.set_ylim(-2, 2)
        self.axes2_v1 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
        self.axes2_v2 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
        self.text_v1_2, self.text_v2_2 = None, None
        self.axes2_x = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="r")
        self.text_x_2 = None
        self.axes_2_l1 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="black")
        self.axes_2_l2 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="black")
        self.axes_2.plot([0] * 20, np.linspace(-2, 2, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_2.plot(np.linspace(-2, 2, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")

    def on_mouseclick1(self, event):
        if event.xdata != None and event.xdata != None:
            if event.xdata > 1.5 or event.xdata < -1.5:
                event.xdata /= 2
                event.ydata /= 2
            if event.ydata > 1.5 or event.ydata < -1.5:
                event.ydata /= 2
                event.xdata /= 2
            self.axes1_points.append((event.xdata, event.ydata))
            if len(self.axes1_points) == 1:
                self.text_start.remove()
                self.text_start = self.axes_1.text(-1.05, -0.5, "<ONCE MORE>")
            self.draw_vector()

    def draw_vector(self):
        if len(self.axes1_points) == 1:
            self.axes1_v1.set_UVC(self.axes1_points[0][0], self.axes1_points[0][1])
            if self.text_v1:
                self.text_v1.remove()
            mult_factor = 1.4 if self.axes1_points[0][0] < 0 and self.axes1_points[0][1] < 0 else 1.2
            self.text_v1 = self.axes_1.text(self.axes1_points[0][0] * mult_factor, self.axes1_points[0][1] * mult_factor, "v1")
        elif len(self.axes1_points) == 2:
            cos_angle = (self.axes1_points[0][0] * self.axes1_points[1][0] + self.axes1_points[1][0] *
                         self.axes1_points[1][1]) / (
                                np.sqrt(self.axes1_points[0][0] ** 2 + self.axes1_points[0][1] ** 2) * np.sqrt(
                            self.axes1_points[1][0] ** 2 + self.axes1_points[1][1] ** 2)
                        )
            if cos_angle == 1:
                self.axes1_points = []
                self.axes1_v1.set_UVC(0, 0)
                self.axes1_v2.set_UVC(0, 0)
                self.label_warning.setText("WHOOPS!  You entered\nparallel vectors, which\ncannot form a basis.\nPlease try again!")
            else:
                self.axes1_v2.set_UVC(self.axes1_points[1][0], self.axes1_points[1][1])
                if self.text_v2:
                    self.text_v2.remove()
                mult_factor = 1.4 if self.axes1_points[1][0] < 0 and self.axes1_points[1][1] < 0 else 1.2
                self.text_v2 = self.axes_1.text(self.axes1_points[1][0] * mult_factor,
                                                self.axes1_points[1][1] * mult_factor, "v2")
        elif len(self.axes1_points) == 3:
            self.text_start.remove()
            self.axes1_x.set_UVC(self.axes1_points[2][0], self.axes1_points[2][1])
            if self.text_x:
                self.text_x.remove()
            mult_factor = 1.4 if self.axes1_points[2][0] < 0 and self.axes1_points[2][1] < 0 else 1.2
            self.text_v2 = self.axes_1.text(self.axes1_points[2][0] * mult_factor,
                                            self.axes1_points[2][1] * mult_factor, "x")
            self.remove_vector = False
            self.expand()
            self.remove_vector = True
        self.canvas.draw()

    def expand(self):
        if self.remove_vector:
            self.label_explanation.setText("")
            if self.axes1_x.U != 0 or self.axes1_x.V != 0:
                self.axes1_x.set_UVC(0, 0)
                if self.text_v2:
                    self.text_v2.remove()
                self.text_start = self.axes_1.text(-1.05, -0.5, "<ONCE MORE>")
                self.canvas.draw()
                self.axes_2.clear()
                self.axes_2.set_title("Vector Expansion", fontdict={'fontsize': 10})
                self.axes_2.set_xlim(-2, 2)
                self.axes_2.set_ylim(-2, 2)
                self.axes2_v1 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
                self.axes2_v2 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="g")
                self.text_v1_2, self.text_v2_2 = None, None
                self.axes2_x = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="r")
                self.text_x_2 = None
                self.axes_2_l1 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="black")
                self.axes_2_l2 = self.axes_2.quiver([0], [0], [0], [0], units="xy", scale=1, color="black")
                self.axes_2.plot([0] * 20, np.linspace(-2, 2, 20), linestyle="dashed", linewidth=0.5, color="gray")
                self.axes_2.plot(np.linspace(-2, 2, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
                self.canvas2.draw()
                if self.axes1_points:
                    self.axes1_points.pop()
        else:
            explanation = " Your vector x is:\n\n x = {} * s1 + {} * s2".format(round(self.axes1_points[2][0], 2), round(self.axes1_points[2][1], 2))
            b = np.array([[self.axes1_points[0][0], self.axes1_points[1][0]],
                          [self.axes1_points[0][1], self.axes1_points[1][1]]])
            x = np.array([[self.axes1_points[2][0]], [self.axes1_points[2][1]]])
            xv = np.dot(np.linalg.inv(b), x)
            explanation += "\n\n The expansion for x in\n terms of v1 and v2 is:\n\n x = {} * v1 + {} * v2".format(round(xv[0, 0], 2), round(xv[1, 0], 2))
            self.label_explanation.setText(explanation)
            # self.axes2_line1.set_data([0, xv[0, 0] * self.axes1_points[0][0]], [0, xv[0, 0] * self.axes1_points[0][1]])
            # self.axes2_line2.set_data([xv[0, 0] * self.axes1_points[0][0], self.axes1_points[2][0]],
            #                           [xv[0, 0] * self.axes1_points[0][1], self.axes1_points[2][1]])
            self.axes_2_l1.set_UVC(xv[0, 0] * self.axes1_points[0][0], xv[0, 0] * self.axes1_points[0][1])
            self.axes_2_l2 = self.axes_2.quiver([xv[0, 0] * self.axes1_points[0][0]], [xv[0, 0] * self.axes1_points[0][1]],
                                                [self.axes1_points[2][0] - xv[0, 0] * self.axes1_points[0][0]], [self.axes1_points[2][1] - xv[0, 0] * self.axes1_points[0][1]],
                                                units="xy", scale=1, color="black")
            # self.axes1_v1.set_UVC(self.axes1_points[0][0], self.axes1_points[0][1])
            # self.axes1_v2.set_UVC(self.axes1_points[1][0], self.axes1_points[1][1])
            self.axes2_v1.set_UVC(self.axes1_points[0][0], self.axes1_points[0][1])
            if self.text_v1_2:
                self.text_v1_2.remove()
            mult_factor = 1.4 if self.axes1_points[0][0] < 0 and self.axes1_points[0][1] < 0 else 1.2
            self.text_v1_2 = self.axes_2.text(self.axes1_points[0][0] * mult_factor,
                                              self.axes1_points[0][1] * mult_factor, "v1")
            self.axes2_v2.set_UVC(self.axes1_points[1][0], self.axes1_points[1][1])
            if self.text_v2_2:
                self.text_v2_2.remove()
            mult_factor = 1.4 if self.axes1_points[1][0] < 0 and self.axes1_points[1][1] < 0 else 1.2
            self.text_v2_2 = self.axes_2.text(self.axes1_points[1][0] * mult_factor,
                                              self.axes1_points[1][1] * mult_factor, "v2")
            # self.axes1_x.set_UVC(self.axes1_points[2][0], self.axes1_points[2][1])
            self.axes2_x.set_UVC(self.axes1_points[2][0], self.axes1_points[2][1])
            if self.text_x_2:
                self.text_x_2.remove()
            mult_factor = 1.4 if self.axes1_points[2][0] < 0 and self.axes1_points[2][1] < 0 else 1.2
            self.text_x_2 = self.axes_2.text(self.axes1_points[2][0] * mult_factor,
                                             self.axes1_points[2][1] * mult_factor, "x")
            self.canvas.draw()
            self.canvas2.draw()

    def clear_all(self):
        self.label_explanation.setText("")
        self.axes_1.clear()
        self.axes_2.clear()
        self.fill_plots()
        self.axes1_points = []
        self.draw_vector()
        self.canvas.draw()
        self.canvas2.draw()

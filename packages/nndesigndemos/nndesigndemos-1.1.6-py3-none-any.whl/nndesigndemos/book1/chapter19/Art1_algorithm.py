from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.patches as patches

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class ART1Algorithm(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(ART1Algorithm, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("ART1 Algorithm", 19, "\n\nClick on the green\ngrids to define patterns.\nClick on the buttons\n"
                                                "to present them.\n\nThe ART1 network's\nprototype patterns are\nshown below.\n\n"
                                                "Use the slider to set\nthe ART1 vigilance.",
                          PACKAGE_PATH + "Logo/Logo_Ch_19.svg", None)

        self.wid_up = 0.99
        self.hei_up = 1.01
        self.nrows_up = 5
        self.ncols_up = 5
        inbetween_up = 0.11
        self.xx_up = np.arange(0, self.ncols_up, (self.wid_up + inbetween_up))
        self.yy_up = np.arange(0, self.nrows_up, (self.hei_up + inbetween_up))

        self.s2, self.s1 = 4, 25
        self.w21, self.w12 = np.ones((self.s1, self.s2)), np.zeros((self.s2, self.s1))
        for k in range(4):
            self.w12[k, :] = 2 * self.w21[:, k].T / (2 + np.sum(self.w21[:, k]) - 1)

        self.make_label("label_pattern1", "Pattern 1", (50, 125, 150, 50))
        self.make_plot(1, (1, 150, 130, 130))
        self.axis1 = self.figure.add_axes([0, 0, 1, 1])
        self.pattern1 = [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0]
        self.pattern11 = np.flip(np.array(self.pattern1).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern11[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis1.add_patch(sq)
        self.axis1.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis1.axis("off")
        self.canvas.draw()
        self.canvas.mpl_connect("button_press_event", self.on_mouseclick1)

        self.make_button("button1", "Present", (15, 275, 100, 25), self.button1_pressed)

        # --

        self.make_label("label_pattern2", "Pattern 2", (175, 125, 150, 50))
        self.make_plot(2, (130, 150, 130, 130))
        self.axis2 = self.figure2.add_axes([0, 0, 1, 1])
        self.pattern2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0]
        self.pattern22 = np.flip(np.array(self.pattern2).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern22[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis2.add_patch(sq)
        self.axis2.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis2.axis("off")
        self.canvas2.draw()
        self.canvas2.mpl_connect("button_press_event", self.on_mouseclick2)

        self.make_button("button2", "Present", (20 + 125, 275, 100, 25), self.button2_pressed)

        # --

        self.make_label("label_pattern3", "Pattern 3", (300, 125, 150, 50))
        self.make_plot(3, (260, 150, 130, 130))
        self.axis3 = self.figure3.add_axes([0, 0, 1, 1])
        self.pattern3 = [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.pattern33 = np.flip(np.array(self.pattern3).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern33[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis3.add_patch(sq)
        self.axis3.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis3.axis("off")
        self.canvas3.draw()
        self.canvas3.mpl_connect("button_press_event", self.on_mouseclick3)

        self.make_button("button3", "Present", (25 + 125 * 2, 275, 100, 25), self.button3_pressed)

        # ---

        self.make_label("label_pattern31", "Pattern 4", (425, 125, 150, 50))
        self.make_plot(31, (390, 150, 130, 130))
        self.axis31 = self.figure31.add_axes([0, 0, 1, 1])
        self.pattern31 = [0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.pattern331 = np.flip(np.array(self.pattern31).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern331[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis31.add_patch(sq)
        self.axis31.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis31.axis("off")
        self.canvas31.draw()
        self.canvas31.mpl_connect("button_press_event", self.on_mouseclick31)

        self.make_button("button31", "Present", (30 + 125 * 3, 275, 100, 25), self.button31_pressed)

        # ---

        self.make_label("label_pattern4", "Prototype 1", (50, 335, 150, 50))
        self.make_plot(4, (1, 360, 130, 130))
        self.axis4 = self.figure4.add_axes([0, 0, 1, 1])

        # ---

        self.make_label("label_pattern5", "Prototype 2", (165, 335, 150, 50))
        self.make_plot(5, (130, 360, 130, 130))
        self.axis5 = self.figure5.add_axes([0, 0, 1, 1])

        # --

        self.make_label("label_pattern6", "Prototype 3", (295, 335, 150, 50))
        self.make_plot(6, (260, 360, 130, 130))
        self.axis6 = self.figure6.add_axes([0, 0, 1, 1])

        # --

        self.make_label("label_pattern7", "Prototype 4", (425, 335, 150, 50))
        self.make_plot(7, (390, 360, 130, 130))
        self.axis7 = self.figure7.add_axes([0, 0, 1, 1])

        # --

        self.on_clear()

        self.make_slider("slider_rho", QtCore.Qt.Orientation.Horizontal, (0, 100), QtWidgets.QSlider.TickPosition.TicksAbove, 1, 60,
                         (20, 560, 480, 50), self.slide, "label_rho", "Vigilance (rho): 0.6", (200, 535, 170, 50))
        self.rho = 0.6

        self.make_button("clear_button", "Clear", (self.x_chapter_button, 345, self.w_chapter_button, self.h_chapter_button), self.on_clear)

    def on_clear(self):

        self.pattern4 = [0] * 25
        self.pattern44 = np.flip(np.array(self.pattern4).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern44[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis4.add_patch(sq)
        self.axis4.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis4.axis("off")
        self.canvas4.draw()

        self.pattern5 = [0] * 25
        self.pattern55 = np.flip(np.array(self.pattern5).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern55[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis5.add_patch(sq)
        self.axis5.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis5.axis("off")
        self.canvas5.draw()

        self.pattern6 = [0] * 25
        self.pattern66 = np.flip(np.array(self.pattern6).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern66[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis6.add_patch(sq)
        self.axis6.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis6.axis("off")
        self.canvas6.draw()

        self.pattern7 = [0] * 25
        self.pattern77 = np.flip(np.array(self.pattern7).reshape((self.ncols_up, self.nrows_up)), axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern77[yi, xi] == 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis7.add_patch(sq)
        self.axis7.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis7.axis("off")
        self.canvas7.draw()

    def slide(self):
        self.rho = self.slider_rho.value() / 100
        self.label_rho.setText("Vigilance (rho): " + str(self.rho))

    def change_squares(self, axis, canvas, k):
        for patch in axis.patches:
            patch.remove()
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if np.flip(self.w21[:, k].reshape((self.ncols_up, self.nrows_up)), axis=1)[xi, yi] > 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                axis.add_patch(sq)
        canvas.draw()

    def change_prototype(self, button_id):

        P = 1 - np.array([list(self.pattern11.T.reshape(-1))[::-1], list(self.pattern22.T.reshape(-1))[::-1],
                          list(self.pattern33.T.reshape(-1))[::-1], list(self.pattern331.T.reshape(-1))[::-1]]).T
        ind_x = []
        while True:
            p = P[:, button_id]
            a1 = p

            n1 = np.dot(self.w12, a1)
            n1[ind_x] = -np.inf
            k = np.argmax(n1)
            a2 = np.zeros((self.s2, 1))
            a2[k, 0] = 1

            expect = self.w21[:, k]
            a1 = p * expect

            if np.sum(a1) / np.sum(p) < self.rho:
                a0 = 1
            else:
                a0 = 0

            if a0:
                ind_x.append(k)
                if len(ind_x) == self.s2:
                    if self.s2 == 4:
                        print("More than four prototypes needed")
                    else:
                        self.w21 = np.hstack((self.w21, np.ones((self.s1, 1))))
                        self.w12 = np.vstack((self.w12, 2 * np.ones((1, self.s1)) / (2 + self.s1 - 1)))
                        self.s2 += 1
                print("TODO")
            else:
                self.w12[k, :] = 2 * a1.T / (2 + np.sum(a1) - 1)
                self.w21[:, k] = a1
                break

        k = 0
        for axis, canvas in zip([self.axis4, self.axis5, self.axis6, self.axis7], [self.canvas4, self.canvas5, self.canvas6, self.canvas7]):
            self.change_squares(axis, canvas, k)
            k += 1

    def button1_pressed(self):
        self.change_prototype(0)

    def button2_pressed(self):
        self.change_prototype(1)

    def button3_pressed(self):
        self.change_prototype(2)

    def button31_pressed(self):
        self.change_prototype(3)

    def on_mouseclick1(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis1.patches:
                patch.remove()
            if self.pattern11[yyy, xxx] == 0:
                self.pattern11[yyy, xxx] = 1
            else:
                self.pattern11[yyy, xxx] = 0
            self.pattern1 = np.flip(self.pattern11.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern11[yi, xi] == 0:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis1.add_patch(sq)
            self.canvas.draw()

    def on_mouseclick2(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis2.patches:
                patch.remove()
            if self.pattern22[yyy, xxx] == 0:
                self.pattern22[yyy, xxx] = 1
            else:
                self.pattern22[yyy, xxx] = 0
            self.pattern2 = np.flip(self.pattern22.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern22[yi, xi] == 0:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis2.add_patch(sq)
            self.canvas2.draw()

    def on_mouseclick3(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis3.patches:
                patch.remove()
            if self.pattern33[yyy, xxx] == 0:
                self.pattern33[yyy, xxx] = 1
            else:
                self.pattern33[yyy, xxx] = 0
            self.pattern3 = np.flip(self.pattern33.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern33[yi, xi] == 0:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis3.add_patch(sq)
            self.canvas3.draw()

    def on_mouseclick31(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis31.patches:
                patch.remove()
            if self.pattern331[yyy, xxx] == 0:
                self.pattern331[yyy, xxx] = 1
            else:
                self.pattern331[yyy, xxx] = 0
            self.pattern31 = np.flip(self.pattern331.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern331[yi, xi] == 0:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis31.add_patch(sq)
            self.canvas31.draw()

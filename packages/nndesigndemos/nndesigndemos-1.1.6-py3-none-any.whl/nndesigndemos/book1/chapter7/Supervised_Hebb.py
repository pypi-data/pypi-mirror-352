import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.patches as patches

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class SupervisedHebb(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(SupervisedHebb, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Supervised Hebb", 7, "Click on the green grids\nto define target patterns.\n\n"
                                                "Click on the gray grid\nto define a test pattern.\n\n"
                                                "Select a rule to calculate\nthe network weights.",
                          PACKAGE_PATH + "Logo/Logo_Ch_7.svg", None)

        self.wid_up = 1
        self.hei_up = 1
        self.nrows_up = 6
        self.ncols_up = 5
        inbetween_up = 0.1
        self.xx_up = np.arange(0, self.ncols_up, (self.wid_up + inbetween_up))
        self.yy_up = np.arange(0, self.nrows_up, (self.hei_up + inbetween_up))

        self.make_label("label_pattern1", "Pattern 1", (75, 105, 150, 50))
        self.make_plot(1, (15, 130, 170, 170))
        self.axis1 = self.figure.add_axes([0, 0, 1, 1])
        self.pattern1 = [0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0]
        self.pattern11 = np.flip(np.array(self.pattern1).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern11[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis1.add_patch(sq)
        self.axis1.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis1.axis("off")
        self.canvas.show()
        self.canvas.mpl_connect("button_press_event", self.on_mouseclick1)

        # --

        self.make_label("label_pattern2", "Pattern 2", (235, 105, 150, 50))
        self.make_plot(2, (175, 130, 170, 170))
        # self.figure2 = Figure(frameon=False)
        self.axis2 = self.figure2.add_axes([0, 0, 1, 1])
        self.pattern2 = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.pattern22 = np.flip(np.array(self.pattern2).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern22[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis2.add_patch(sq)
        self.axis2.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis2.axis("off")
        self.canvas2.show()
        self.canvas2.mpl_connect("button_press_event", self.on_mouseclick2)

        # --

        self.make_label("label_pattern3", "Pattern 3", (390, 105, 150, 50))
        self.make_plot(3, (335, 130, 170, 170))
        self.axis3 = self.figure3.add_axes([0, 0, 1, 1])
        self.pattern3 = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1]
        self.pattern33 = np.flip(np.array(self.pattern3).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern33[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis3.add_patch(sq)
        self.axis3.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis3.axis("off")
        self.canvas3.show()
        self.canvas3.mpl_connect("button_press_event", self.on_mouseclick3)

        # ---

        self.make_label("label_pattern4", "Test Pattern", (115, 305, 150, 50))
        self.make_plot(4, (30, 330, 240, 240))
        self.axis4 = self.figure4.add_axes([0, 0, 1, 1])
        self.pattern4 = self.pattern1[:]
        self.pattern44 = np.copy(self.pattern11)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern44[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="gray")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis4.add_patch(sq)
        self.axis4.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis4.axis("off")
        self.canvas4.draw()
        self.canvas4.mpl_connect("button_press_event", self.on_mouseclick4)

        # ---

        self.make_label("label_pattern5", "Response Pattern", (320, 305, 150, 50))
        self.make_plot(5, (250, 330, 240, 240))
        self.axis5 = self.figure5.add_axes([0, 0, 1, 1])
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern11[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis5.add_patch(sq)
        self.axis5.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis5.axis("off")
        self.canvas5.draw()

        # --

        self.make_combobox(1, ["Hebb", 'Pseudoinverse'], (self.x_chapter_usual, 300, self.w_chapter_slider, 100),
                           self.change_rule, "label_combobox", "Learning Rule", (self.x_chapter_usual + 50, 300, 100, 50))
        self.rule = 0

        # self.run_button = QtWidgets.QPushButton("Weights", self)
        #         self.run_button.setStyleSheet("font-size:13px")
        #         self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 420 * self.h_ratio,
        #                                     self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        #         self.run_button.clicked.connect(self.on_run)

    #  def on_run(self):
    #
    #         pattern = np.array([self.pattern1, self.pattern2, self.pattern3]).T * 2 - 1
    #         if self.rule == 0:
    #             w = np.dot(pattern, pattern.T)
    #         elif self.rule == 1:
    #             w = np.dot(pattern, np.linalg.pinv(pattern))
    #         plt.imshow(w)
    #         plt.title("Network Weights")
    #         plt.xlabel("Input")
    #         plt.ylabel("Neuron")

    def on_mouseclick1(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis1.patches:
                patch.remove()
            if self.pattern11[yyy, xxx] == 1:
                self.pattern11[yyy, xxx] = 0
            else:
                self.pattern11[yyy, xxx] = 1
            self.pattern1 = np.flip(self.pattern11.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern11[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis1.add_patch(sq)
            self.canvas.draw()
            self.response()

    def on_mouseclick2(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis2.patches:
                patch.remove()
            if self.pattern22[yyy, xxx] == 1:
                self.pattern22[yyy, xxx] = 0
            else:
                self.pattern22[yyy, xxx] = 1
            self.pattern2 = np.flip(self.pattern22.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern22[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis2.add_patch(sq)
            self.canvas2.draw()
            self.response()

    def on_mouseclick3(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis3.patches:
                patch.remove()
            if self.pattern33[yyy, xxx] == 1:
                self.pattern33[yyy, xxx] = 0
            else:
                self.pattern33[yyy, xxx] = 1
            self.pattern3 = np.flip(self.pattern33.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern33[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis3.add_patch(sq)
            self.canvas3.draw()
            self.response()

    def on_mouseclick4(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis4.patches:
                patch.remove()
            if self.pattern44[yyy, xxx] == 1:
                self.pattern44[yyy, xxx] = 0
            else:
                self.pattern44[yyy, xxx] = 1
            self.pattern4 = np.flip(self.pattern44.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern44[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="gray")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis4.add_patch(sq)
            self.canvas4.draw()
            self.response()

    def response(self):
        pattern = np.array([self.pattern1, self.pattern2, self.pattern3]).T * 2 - 1
        p = np.array(self.pattern4).T * 2 - 1
        if self.rule == 0:
            w = np.dot(pattern, pattern.T)
        elif self.rule == 1:
            w = np.dot(pattern, np.linalg.pinv(pattern))
        a = np.flip(np.dot(w, p).reshape(self.ncols_up, self.nrows_up).T, axis=0)
        for patch in self.axis5.patches:
            patch.remove()
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if a[yi, xi] > 0:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis5.add_patch(sq)
        self.canvas5.draw()

    def change_rule(self, idx):
        self.rule = idx
        self.response()

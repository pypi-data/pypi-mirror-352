import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class LinearClassification(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LinearClassification, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Linear Classification", 10, "Edit the RED grid and\nwatch the output meter\nrespond to the"
                                                       " new inputs.\n\nEdit the GREEN grids and\nthen click [Train] to\n"
                                                       "study a different problem.\n\nUse GREEN patterns as\ninputs by clicking\n"
                                                       "the arrow bottoms.",
                          PACKAGE_PATH + "Logo/Logo_Ch_10.svg", None, description_coords=(535, 120, 300, 250))

        self.wid_up = 1
        self.hei_up = 1.04
        self.nrows_up = 4
        self.ncols_up = 4
        inbetween_up = 0.12
        self.xx_up = np.arange(0, self.ncols_up, (self.wid_up + inbetween_up))
        self.yy_up = np.arange(0, self.nrows_up, (self.hei_up + inbetween_up))

        self.make_label("label_pattern1", "Target = 60", (50, 105, 150, 50))
        self.make_plot(1, (15, 130, 130, 130))
        self.axis1 = self.figure.add_axes([0, 0, 1, 1])
        self.pattern1 = [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
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
        self.canvas.draw()
        self.canvas.mpl_connect("button_press_event", self.on_mouseclick1)
        self.make_button("button1", "->", (55, 250, 50, 50), self.button1_pressed)

        # --

        self.make_label("label_pattern2", "Target = 0", (180, 105, 150, 50))
        self.make_plot(2, (140, 130, 130, 130))
        self.axis2 = self.figure2.add_axes([0, 0, 1, 1])
        self.pattern2 = [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1]
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
        self.canvas2.draw()
        self.canvas2.mpl_connect("button_press_event", self.on_mouseclick2)
        self.make_button("button2", "->", (55 + 125, 250, 50, 50), self.button2_pressed)

        # --

        self.make_label("label_pattern3", "Target = -60", (290, 105, 150, 50))
        self.make_plot(3, (260, 130, 130, 130))
        self.axis3 = self.figure3.add_axes([0, 0, 1, 1])
        self.pattern3 = [1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
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
        self.canvas3.draw()
        self.canvas3.mpl_connect("button_press_event", self.on_mouseclick3)
        self.make_button("button3", "->", (55 + 125 * 2, 250, 50, 50), self.button3_pressed)

        # ---

        self.make_plot(4, (15, 300, 130, 130))
        self.axis4 = self.figure4.add_axes([0, 0, 1, 1])
        self.pattern4 = [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0]
        self.pattern44 = np.flip(np.array(self.pattern4).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern44[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis4.add_patch(sq)
        self.axis4.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis4.axis("off")
        self.canvas4.draw()
        self.canvas4.mpl_connect("button_press_event", self.on_mouseclick4)
        self.make_button("button4", "->", (55, 420, 50, 50), self.button4_pressed)

        # ---

        self.make_plot(5, (140, 300, 130, 130))
        self.axis5 = self.figure5.add_axes([0, 0, 1, 1])
        self.pattern5 = [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0]
        self.pattern55 = np.flip(np.array(self.pattern5).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern55[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis5.add_patch(sq)
        self.axis5.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis5.axis("off")
        self.canvas5.draw()
        self.canvas5.mpl_connect("button_press_event", self.on_mouseclick5)
        self.make_button("button5", "->", (55 + 125, 420, 50, 50), self.button5_pressed)

        # --

        self.make_plot(6, (260, 300, 130, 130))
        self.axis6 = self.figure6.add_axes([0, 0, 1, 1])
        self.pattern6 = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0]
        self.pattern66 = np.flip(np.array(self.pattern6).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern66[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis6.add_patch(sq)
        self.axis6.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis6.axis("off")
        self.canvas6.draw()
        self.canvas6.mpl_connect("button_press_event", self.on_mouseclick6)
        self.make_button("button6", "->", (55 + 125 * 2, 420, 50, 50), self.button6_pressed)

        # --

        self.make_label("label_pattern7", "Test Input", (415, 275, 150, 50))
        self.make_plot(7, (380, 300, 130, 130))
        self.axis7 = self.figure7.add_axes([0, 0, 1, 1])
        self.pattern7 = self.pattern1[:]
        self.pattern77 = np.copy(self.pattern11)
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern77[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis7.add_patch(sq)
        self.axis7.axis([-0.1, self.ncols_up + 0.5, -0.1, self.nrows_up + 0.6])
        self.axis7.axis("off")
        self.canvas7.draw()
        self.canvas7.mpl_connect("button_press_event", self.on_mouseclick7)

        # --

        self.make_plot(8, (5, 470, 270, 200))
        self.axis8 = self.figure8.add_subplot(1, 1, 1)
        self.axis8.set_title("Errors")
        self.axis8.set_xlabel("Training Cycle")
        self.axis8.set_ylabel("Sum Squared Error")
        self.axis8.set_xlim(0, 200)
        self.axis8.set_ylim(1e-5, 1e5)
        self.axis8.set_yscale("log")
        self.error_plot, = self.axis8.plot([], color="red")
        self.figure8.set_tight_layout(True)

        # --

        self.make_plot(9, (260, 470, 250, 200))
        self.axis9 = self.figure9.add_subplot(1, 1, 1, polar=True)
        self.axis9.set_thetamin(-90)
        self.axis9.set_thetamax(90)
        self.axis9.set_title("Test Output", pad=1)
        self.axis9.set_xlabel("Windrow-Hoff Metter")
        self.axis9.set_yticks([])
        self.axis9.set_theta_zero_location("N")
        self.axis9.set_theta_direction(-1)
        self.axis9.set_xticks(np.array([-60, -30, 0, 30, 60]) * np.pi / 180)
        # self.angle = 60
        # r = np.arange(0, 0.9, 0.01)
        # theta = self.angle * np.pi / 180
        self.meter, = self.axis9.plot([], color="red")
        self.angles = []
        self.ani = None
        self.angle, self.angle_end = None, None
        self.canvas9.draw()

        # --

        # self.make_button("run_button", "Weights", (self.x_chapter_button, 420, self.w_chapter_button, self.h_chapter_button), self.on_run)
        self.make_button("run_button", "Train", (self.x_chapter_button, 355, self.w_chapter_button, self.h_chapter_button), self.response)

        self.response()

    def change_test_input(self, pattern):
        self.pattern7 = pattern[:]
        self.pattern77 = np.flip(np.array(self.pattern7).reshape((self.ncols_up, self.nrows_up)).T, axis=0)
        for patch in self.axis7.patches:
            patch.remove()
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                if self.pattern77[yi, xi] == 1:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                else:
                    sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                self.axis7.add_patch(sq)
        self.canvas7.draw()
        self.run_animation()

    def button1_pressed(self):
        self.change_test_input(self.pattern1)

    def button2_pressed(self):
        self.change_test_input(self.pattern2)

    def button3_pressed(self):
        self.change_test_input(self.pattern3)

    def button4_pressed(self):
        self.change_test_input(self.pattern4)

    def button5_pressed(self):
        self.change_test_input(self.pattern5)

    def button6_pressed(self):
        self.change_test_input(self.pattern6)

    # def on_run(self):
    #     print("!")

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

            # self.response()

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
            # self.response()

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
            # self.response()

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
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis4.add_patch(sq)
            self.canvas4.draw()
            # self.response()

    def on_mouseclick5(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis5.patches:
                patch.remove()
            if self.pattern55[yyy, xxx] == 1:
                self.pattern55[yyy, xxx] = 0
            else:
                self.pattern55[yyy, xxx] = 1
            self.pattern5 = np.flip(self.pattern55.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern55[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis5.add_patch(sq)
            self.canvas5.draw()
            # self.response()

    def on_mouseclick6(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis6.patches:
                patch.remove()
            if self.pattern66[yyy, xxx] == 1:
                self.pattern66[yyy, xxx] = 0
            else:
                self.pattern66[yyy, xxx] = 1
            self.pattern6 = np.flip(self.pattern66.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern66[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="green")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis6.add_patch(sq)
            self.canvas6.draw()
            # self.response()

    def on_mouseclick7(self, event):
        if event.xdata != None and event.xdata != None:
            d_x = [abs(event.xdata - xx - 0.5) for xx in self.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in self.yy_up]
            xxx, yyy = list(range(len(self.xx_up)))[np.argmin(d_x)], list(range(len(self.yy_up)))[np.argmin(d_y)]
            for patch in self.axis7.patches:
                patch.remove()
            if self.pattern77[yyy, xxx] == 1:
                self.pattern77[yyy, xxx] = 0
            else:
                self.pattern77[yyy, xxx] = 1
            self.pattern7 = np.flip(self.pattern77.T, axis=1).reshape(-1)
            for xi in range(len(self.xx_up)):
                for yi in range(len(self.yy_up)):
                    if self.pattern77[yi, xi] == 1:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="red")
                    else:
                        sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.hei_up, fill=True, color="khaki")
                    self.axis7.add_patch(sq)
            self.canvas7.draw()
            self.run_animation()

    def response(self):

        P = np.array([self.pattern1, self.pattern4, self.pattern5, self.pattern2, self.pattern3, self.pattern6]).T * 2 - 1
        T = np.array([[60, 60, 0, 0, -60, -60]])
        w, b = np.zeros((1, 16)), 0
        sse = []
        for i in range(200):
            q = int(np.fix(np.random.uniform(0, 1) * 6) + 1)
            p = P[:, q - 1]
            t = T[:, q - 1]
            a = np.dot(w, p) + b
            e = (t - a).item()
            w += 2 * 0.03 * e * p.T
            b += 2 * 0.03 * e
            sse.append(np.sum((T - np.dot(w, P) - b) ** 2))
        self.error_plot.set_data(range(len(sse)), sse)
        self.canvas8.draw()

        w_, b_ = np.array([[60, 0, -75, 0, -15, -15, -15, 0, 0, 0, 30, 0, 0, 0, 0, 0]]), 0
        self.angle = int((np.dot(w_, np.array([self.pattern7]).T * 2 - 1) + b_).item())
        self.draw_meter()
        self.canvas9.draw()

    def run_animation(self):
        w_, b_ = np.array([[60, 0, -75, 0, -15, -15, -15, 0, 0, 0, 30, 0, 0, 0, 0, 0]]), 0
        self.angle_end = (np.dot(w_, np.array([self.pattern7]).T * 2 - 1) + b_).item()
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        self.ani = FuncAnimation(self.figure9, self.on_animate, init_func=self.animate_init,
                                 frames=abs(self.angle - self.angle_end), interval=50, repeat=False, blit=False)
        self.canvas9.draw()

    def draw_meter(self):
        r = np.arange(0, 0.9, 0.01)
        theta = self.angle * np.pi / 180
        self.meter.set_data([theta], [r])

    def animate_init(self):
        self.angles = [self.angle]
        self.draw_meter()
        return self.meter,

    def on_animate(self, idx):
        if self.angle > self.angle_end:
            self.angle -= 1
        elif self.angle < self.angle_end:
            self.angle += 1
        self.draw_meter()
        return self.meter,

import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout

from nndesigndemos.get_package_path import PACKAGE_PATH

# v1 = v11 * e1 + v12 * e2
# v2 = v21 * e1 + v22 * e2
#
# y1 = y11 * e1 + y12 * e2
# y2 = y21 * e1 + y22 * e2
#
# T(v1) = y1 —> v11 * T(e1) + v12 * T(e2) = y11 * e1 + y12  * e2
# T(v2) = y2 —> v21 * T(e1) + v22 * T(e2) = y21 * e1 + y22 * e2
#               ----------------------------——————————————————————
# 			T(e1) = ( y11 * e1 + y12  * e2 - v12 * T(e2) ) / v11 = ( y21 * e1 + y22 * e2 - v22 * T(e2) ) / v21 —>
# 			—> - v12 * T(e2) = (v11 / v21)  * ( y21 * e1 + y22 * e2 - v22 * T(e2) ) - y11 * e1 - y12  * e2 —>
# 			—> T(e2) * (-v12 + v22 * v11 / v21) = (v11 / v21)  * ( y21 * e1 + y22 * e2) - y11 * e1 - y12  * e2 —>
# 			—> T(e2) = ( ( v11 * y21 / v21 - y11 ) * e1 + ( v11 * y22 / v21 - y12 ) * e2 ) / (-v12 + v22 * v11 / v21)
# 			—> T(e1) = (1/v11) * ( y11 - v12 * ( v11 * y21 / v21 - y11 ) / (-v12 + v22 * v11 / v21) ) * e1 +
# 						+ (1/v11) * ( y12 - v12 * ( v11 * y22 / v21 - y12 ) / (-v12 + v22 * v11 / v21) ) * e2
#
# A_div = -v12 + v22 * v11 / v21
#
# A = [ T(e1) T(e2) ] = [  (1/v11) * (y11 - v12 * ( v11 * y21 / v21 - y11 ) / A_div)    ( v11 * y21 / v21 - y11 ) / A_div   ]
# 				 [  (1/v11) * ( y12 - v12 * ( v11 * y22 / v21 - y12 ) / A_div)     ( v11 * y22 / v21 - y12 ) / A_div ]


class LinearTransformations(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LinearTransformations, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Linear Transformations", 6, "Click in the top graph to\ncreate a vector. Move\nthe mouse and "
                                                       "click again\nto create the transformed\nvector. Repeat for a\n"
                                                       "second vector.\n\nThese four vectors define\na linear transformation.\n"
                                                       "The eigenvectors of the\ntransformation will be\nshown in the bottom graph.\n"
                                                       "If the eigenvectors are\ncomplex they will not\nbe shown.\n\n"
                                                       "Click in the bottom graph\nand move the mouse to\nsee how other vectors\n"
                                                       "are transformed.",
                          PACKAGE_PATH + "Logo/Logo_Ch_6.svg", None, description_coords=(535, 140, 450, 350))

        self.cid1, self.cid2 = None, None
        self.cid3 = None
        self.A, self.eig_v1, self.eig_v2 = None, None, None

        self.make_plot(1, (100, 90, 300, 300))
        self.vectors = []
        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Original Vectors")
        self.axes_1.set_xlim(-1, 1)
        self.axes_1.set_ylim(-1, 1)
        self.line, = self.axes_1.plot([], linestyle="--", color="gray")
        self.line_data_x, self.line_data_y = [], []
        self.line2 = None
        self.line_data_x2, self.line_data_y2 = [], []
        # self.axes_1.set_xticks([-1, -0.5, 0, 0.5])
        # self.axes_1.set_yticks([-1, -0.5, 0, 0.5])
        # self.axes_1.set_xlabel("$x$")
        # self.axes_1.xaxis.set_label_coords(1, -0.025)
        # self.axes_1.set_ylabel("$y$")
        # self.axes_1.yaxis.set_label_coords(-0.025, 1)
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self.on_mouseclick)

        self.make_plot(2, (100, 380, 300, 300))
        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        self.axes_2.set_xlim(-1, 1)
        self.axes_2.set_ylim(-1, 1)
        self.axes_2.set_title("Transformed Vectors")
        self.point2, = self.axes_2.plot([], marker='*')
        self.line2, = self.axes_2.plot([], linestyle="--")
        self.text_2 = self.axes_2.text(-0.7, 0, "")
        self.line_data_x2, self.line_data_y2 = [], []
        # self.axes_2.set_xticks([-1, -0.5, 0, 0.5])
        # self.axes_2.set_yticks([-1, -0.5, 0, 0.5])
        # self.axes_2.set_xlabel("$x$")
        # self.axes_2.xaxis.set_label_coords(1, -0.025)
        # self.axes_2.set_ylabel("$y$")
        # self.axes_2.yaxis.set_label_coords(-0.025, 1)
        self.axes_2.plot([0] * 20, np.linspace(-1, 1, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_2.plot(np.linspace(-1, 1, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        self.canvas2.draw()
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick2)

        self.make_button("run_button", "Clear", (self.x_chapter_button, 500, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.on_run()

    def on_run(self):
        if self.cid3:
            self.canvas2.mpl_disconnect(self.cid3)
        if self.cid1:
            self.canvas.mpl_disconnect(self.cid1)
        if self.cid2:
            self.canvas.mpl_disconnect(self.cid2)
        self.vectors = []
        self.line_data_x, self.line_data_y = [], []
        for line in self.axes_1.lines:
            line.remove()
        self.axes_1.plot([0] * 20, np.linspace(-1, 1, 20), linestyle="dashed", linewidth=0.5, color="gray")
        self.axes_1.plot(np.linspace(-1, 1, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
        while self.axes_1.collections:
            for collection in self.axes_1.collections:
                collection.remove()
        self.line, = self.axes_1.plot([], linestyle="--", color="gray")
        self.line2, = self.axes_2.plot([], linestyle="--")
        self.text_2.set_text("")
        self.line_data_x2, self.line_data_y2 = [], []
        while self.axes_2.collections:
            for collection in self.axes_2.collections:
                collection.remove()
        self.canvas.draw()
        self.canvas2.draw()

    def on_mouseclick(self, event):
        if event.xdata != None and event.xdata != None:
            self.vectors.append((event.xdata, event.ydata))
            n_vectors = len(self.vectors)
            if n_vectors == 1:
                self.line_data_x, self.line_data_y = [event.xdata], [event.ydata]
                self.line.set_data(self.line_data_x, self.line_data_y)
                # self.temp_1 = (event.xdata, event.ydata)
                self.axes_1.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1, label="Vector 1")
                self.cid1 = self.canvas.mpl_connect("motion_notify_event", self.on_mousepressed1)
            elif n_vectors == 2:
                # self.temp_2 = (event.xdata, event.ydata)
                self.axes_1.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1, label="Transformed 1", color="r")
                self.canvas.mpl_disconnect(self.cid1)
            elif n_vectors == 3:
                self.line_data_x2, self.line_data_y2 = [event.xdata], [event.ydata]
                self.line2.set_data(self.line_data_x2, self.line_data_y2)
                self.axes_1.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1, label="Vector 2")
                self.cid2 = self.canvas.mpl_connect("motion_notify_event", self.on_mousepressed2)
            elif n_vectors == 4:
                self.axes_1.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1, label="Transformed 2", color="r")
                self.canvas.mpl_disconnect(self.cid2)
                v1, y1, v2, y2 = self.vectors[0], self.vectors[1], self.vectors[2], self.vectors[3]
                # A_div = -v12 + v22 * v11 / v21
                # A = [ T(e1) T(e2) ] =
                # [(1/v11) * (y11 - v12 * (v11 * y21 / v21 - y11) / A_div)   (v11 * y21 / v21 - y11) / A_div ]
                # [(1/v11) * (y12 - v12 * (v11 * y22 / v21 - y12) / A_div)  (v11 * y22 / v21 - y12) / A_div ]
                A_div = -v1[1] + v2[1] * v1[0] / v2[0]
                A_11 = (y1[0] - v1[1] * (v1[0] * y2[0] / v2[0] - y1[0]) / A_div) / v1[0]
                A_12 = (v1[0] * y2[0] / v2[0] - y1[0]) / A_div
                A_21 = (y1[1] - v1[1] * (v1[0] * y2[1] / v2[0] - y1[1]) / A_div) / v1[0]
                A_22 = (v1[0] * y2[1] / v2[0] - y1[1]) / A_div
                self.A = np.array([[A_11, A_12], [A_21, A_22]])
                e, v = np.linalg.eig(self.A)
                if "complex" in str(v.dtype):
                    self.text_2.set_text("Complex Eigenvectors!")
                else:
                    # print(v)
                    self.text_2.set_text("")
                    self.axes_2.quiver([0], [0], [v[0, 0]], [v[1, 0]], units="xy", scale=1, label="Eigenvector 1", color="g")
                    self.axes_2.quiver([0], [0], [v[0, 1]], [v[1, 1]], units="xy", scale=1, label="Eigenvector 2", color="g")
                self.canvas2.draw()
            else:
                return
            self.canvas.draw()

    def on_mousepressed1(self, event):
        if event.xdata != None and event.ydata != None:
            self.line_data_x.append(event.xdata)
            self.line_data_y.append(event.ydata)
            self.line.set_data(self.line_data_x, self.line_data_y)
            self.canvas.draw()
            self.line_data_x.pop()
            self.line_data_y.pop()

    def on_mousepressed2(self, event):
        if event.xdata != None and event.ydata != None:
            self.line_data_x2.append(event.xdata)
            self.line_data_y2.append(event.ydata)
            for line in self.axes_1.lines:
                line.remove()
            self.axes_1.plot([0] * 20, np.linspace(-1, 1, 20), linestyle="dashed", linewidth=0.5, color="gray")
            self.axes_1.plot(np.linspace(-1, 1, 20), [0] * 20, linestyle="dashed", linewidth=0.5, color="gray")
            self.axes_1.add_line(self.line)
            self.axes_1.plot(self.line_data_x2, self.line_data_y2, linestyle="--", color="gray")
            self.canvas.draw()
            self.line_data_x2.pop()
            self.line_data_y2.pop()

    def on_mouseclick2(self, event):
        if event.xdata != None and event.xdata != None and len(self.vectors) >= 4:
            if self.axes_2.collections:
                while len(self.axes_2.collections) > 2:
                    self.axes_2.collections[-1].remove()
            if self.cid3:
                self.canvas2.mpl_disconnect(self.cid3)
            self.axes_2.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1)
            v_transformed = np.dot(self.A, np.array([[event.xdata], [event.ydata]]))
            self.axes_2.quiver([0], [0], [v_transformed[0, 0]], [v_transformed[1, 0]], units="xy", scale=1, color="g")
            self.cid3 = self.canvas2.mpl_connect("motion_notify_event", self.on_mousepressed3)
            self.canvas2.draw()

    def on_mousepressed3(self, event):
        if event.xdata != None and event.ydata != None:
            self.axes_2.collections[-1].remove()
            self.axes_2.collections[-1].remove()
            self.axes_2.quiver([0], [0], [event.xdata], [event.ydata], units="xy", scale=1)
            # print("original vector 1:", self.temp_1)
            # print("new vector:", event.xdata, event.ydata)
            # print("........")
            v_transformed = np.dot(self.A, np.array([[event.xdata], [event.ydata]]))
            # print("original vector 1 transformed:", self.temp_2)
            # print("new vector transformed:", v_transformed)
            # print("\n-----\n")
            self.axes_2.quiver([0], [0], [v_transformed[0, 0]], [v_transformed[1, 0]], units="xy", scale=1, color="g")
            self.canvas2.draw()

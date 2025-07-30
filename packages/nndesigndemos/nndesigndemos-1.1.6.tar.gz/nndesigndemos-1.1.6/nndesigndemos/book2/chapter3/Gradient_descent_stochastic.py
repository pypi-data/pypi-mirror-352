from PyQt6 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class GradientDescentStochastic(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(GradientDescentStochastic, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Gradient Descent Stochastic", 3, "\nClick anywhere on the\ngraph to start an initial guess."
                                                            "\nThen the steepest descent\ntrajectory will be shown.\n\n"
                                                            "Modify the learning rate\nby moving the slide bar.\n\n"
                                                            "Experiment with different\ninitial guesses and\nlearning rates.",
                          PACKAGE_PATH + "Chapters/3_D/Logo_Ch_3.svg", None, 2,
                          icon_move_left=120, description_coords=(535, 105, 450, 250))

        self.data = []

        self.make_plot(1, (100, 100, 290, 290))
        self.make_plot(2, (100, 390, 290, 290))
        self.figure.set_tight_layout(True)
        self.figure2.set_tight_layout(True)

        self.make_slider("slider_lr", QtCore.Qt.Orientation.Horizontal, (0, 30), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 1,
                         (self.x_chapter_usual, 360, self.w_chapter_slider, 50), self.slider, "label_lr",
                         "Learning rate: 0.01", (self.x_chapter_usual + 40, 360 - 25, self.w_chapter_slider, 50))
        self.lr = float(self.slider_lr.value() / 100)

        self.graph()

    def slider(self):
        self.lr = float(self.slider_lr.value() / 100)
        self.label_lr.setText("Learning rate: {}".format(self.lr))
        self.graph()

    def on_mouseclick(self, event):
        """Add an item to the plot"""
        if event.xdata != None and event.xdata != None:
            self.data.append((event.xdata, event.ydata))
            self.a1.plot(np.array([self.data[-1][0]]), np.array([self.data[-1][1]]), 'bo')
            self.graph()
            self.canvas2.draw()

    def graph(self):

        self.figure.clf()
        aa = self.figure.add_subplot(projection='3d')

        self.figure2.clf()
        self.a1 = self.figure2.add_subplot(111)
        # self.a1.clear()  # Clear the plot

        hh = np.array([[-1, 2, 0, - 1], [2, - 1, - 1, 0]])
        t = np.array( [-1, -1, 1, 1]).reshape(-1,1)
        jj = np.dot(hh , np.transpose(hh))
        jt = np.dot(hh , t)
        a = 2 * jj
        b = -2 * jt
        c = np.dot(np.transpose(t),t)
        tt = np.arange(0.01, 1, 0.01) * 2 * np.pi
        circ_x1 = np.sin(tt) * .01 * (3 / 2)
        circ_y1 = np.cos(tt) * .01 * (3 / 2)
        circ_x2 = np.sin(tt) * .02 * (3 / 2)
        circ_y2 = np.cos(tt) * .02 * (3 / 2)
        x10 = np.array([-1])
        x20 = np.array([-2.95])
        y = np.linspace(-3,0,61)
        x = y
        X1, X2 = np.meshgrid(x, y)
        F = (a[0, 0] * np.power(X1, 2) + (a[0, 1] + a[1, 0]) * (X1 * X2) + a[1, 1] * np.power(X2, 2)) / 2 + b[0] * X1 + b[1] * X2 + c
        xc = circ_x2 + x10
        yc = circ_y2 + x20
        disp_freq = 1
        max_epoch = 80
        err_goal = -3.999

        if self.data == []:
            x1 = x10
            x2 = x20
        else:
            x1 = np.array([self.data[-1][0]])
            x2 = np.array([self.data[-1][1]])

        for i in range(max_epoch):
            Lx1 = x1
            Lx2 = x2
            select = np.random.randint(4)
            p = hh[:, select].reshape(-1,1)
            e = t[select] - np.dot(np.array([x1.flatten(), x2.flatten()]).reshape(1, 2), p).flatten()
            grad = 2 * e * p
            grad1 = np.dot(a,np.array([x1.flatten(), x2.flatten()]).reshape(2, 1))+b

            dx1 = self.lr * grad[0]
            dx2 = self.lr * grad[1]

            x1 = x1 + dx1
            x2 = x2 + dx2

            SSE = (a[0, 0] * np.power(x1, 2) + (a[0, 1] + a[1, 0]) * (x1 * x2) + a[1, 1] * np.power(x2, 2)) / 2 + b[0] * x1 + b[1] * X2 + c


            self.a1.plot(np.concatenate((Lx1, x1), 0), np.concatenate((Lx2, x2), 0), 'bo-', markersize=1)
            F1 = (a[0, 0] * np.power(x1, 2) + (a[0, 1] + a[1, 0]) * (x1 * x2) + a[1, 1] * np.power(x2, 2)) / 2 + b[0] * x1 + b[1] * x1 + c
            # aa.plot(x1,x2,F1.flatten(),'ro', markersize=4)
            aa.scatter3D(x1,x2,F1.flatten(),s=40, c='Red', marker='o')

        # aa.plot_surface(X1, X2, F,color='g')
        #aa.plot_wireframe(X1, X2, F, rcount=30,ccount=30)

        # aa.plot_surface(X1, X2, F)
        aa.plot_wireframe(X1, X2, F, rcount=30, ccount=30)
        # aa.plot_wireframe(self.P1, self.P2, z11,  rcount=10,ccount=10)
        self.a1.contour(X1, X2, F)

        self.a1.contour(X1, X2, F)
        self.a1.set_xlabel(r'$\mathrm{w}_{1,1}$')
        self.a1.set_ylabel(r'$\mathrm{w}_{1,2}$')
        self.a1.yaxis.tick_right()

        # Setting limits so that the point moves instead of the plot.
        #a.set_xlim(-4, 4)
        #a.set_ylim(-2, 2)

        # add grid and axes
        aa.grid(True, which='both')

        self.canvas.draw()
        self.canvas2.draw()
        self.canvas2.mpl_connect('button_press_event', self.on_mouseclick)

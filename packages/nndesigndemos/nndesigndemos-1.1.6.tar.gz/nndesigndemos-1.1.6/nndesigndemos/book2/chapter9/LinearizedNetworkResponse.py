import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib as mpl
from matplotlib import cm
from matplotlib.colors import Normalize

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.book2.chapter9.RadialProblemSimple import Multilayer


class LinearizedNetworkResponse(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LinearizedNetworkResponse, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Linearized Network Response", 9,
                          "Click a location in the left\ngraph where you want to\nlinearize the network\nresponse.",
                          PACKAGE_PATH + "Logo/Logo_Ch_21.svg", None, 2, description_coords=(535, 95, 450, 250))

        # Create the weights for the radial function
        w1 = np.array([[-0.2], [-0.2]])
        b1 = np.array([[2.], [-2.]])
        w2 = np.array([[-320, 320]])
        b2 = np.array([243.7])

        w1c = np.array([[-0.2489], [-0.3541]])
        b1c = np.array([[1.2931], [-2.6491]])
        w2c = np.array([[-6.6898, 69.3431]])
        b2c = np.array([1.6693])

        w1p = np.concatenate(
            (np.concatenate((w1, np.zeros(w1.shape)), axis=1), np.concatenate((np.zeros(w1.shape), w1), axis=1)))
        b1p = np.concatenate((b1, b1))
        w2p = np.concatenate(
            (np.concatenate((w2, np.zeros(w2.shape)), axis=1), np.concatenate((np.zeros(w2.shape), w2), axis=1)))
        b2p = np.concatenate((b2, b2))
        w3p = np.ones((1, 2))
        b3p = np.array([0])
        b2p = np.expand_dims(b2p, axis=1)
        b3p = np.expand_dims(b3p, axis=1)
        wf1 = w1p
        bf1 = b1p
        wf2 = np.matmul(np.matmul(w1c, w3p), w2p)
        bf2 = np.matmul(np.matmul(w1c, w3p), b2p) + np.matmul(w1c, b3p) + b1c
        wf3 = w2c
        bf3 = b2c

        netweights = [wf1, wf2, wf3]
        netbiases = [bf1, bf2, bf3]

        # Put the weights into a multilayer network object
        self.net = Multilayer(netweights, netbiases)

        # Make a grid of input points, in order to see the shape of the network response
        x = np.arange(-2, 2.1, 0.1)
        y = np.arange(-2, 2.1, 0.1)

        self.xx, self.yy = np.meshgrid(x, y)

        xxv = self.xx.reshape((1681, 1))
        yyv = self.yy.reshape((1681, 1))
        self.pxy = np.concatenate((xxv, yyv), axis=1)

        # Find the network response over the grid
        anet = self.net.sim(self.pxy.transpose())

        # Put the output in the grid shape
        self.cc = anet[-1].reshape((41, 41))

        # Make a grid of input points where you want to see the gradient direction
        x1 = np.arange(-1.5, 2.0, 0.5)
        y1 = np.arange(-1.5, 2.0, 0.5)

        xx1, yy1 = np.meshgrid(x1, y1)

        xxv1 = xx1.reshape((49, 1))
        yyv1 = yy1.reshape((49, 1))
        pxy1 = np.concatenate((xxv1, yyv1), axis=1)

        # Compute the gradient at the grid points
        ag = self.net.sim(pxy1.transpose())
        gd = self.net.grad(ag, 0).transpose()


        self.make_plot(3, (5, 230, 260, 260))
        self.figure3.subplots_adjust(left=0.15, right=0.95, bottom=0.2, top=0.95)
        self.make_plot(4, (250, 230, 260, 260))
        self.figure4.subplots_adjust(left=0.15, right=0.975, bottom=0.175, top=0.95)

        self.axes_3 = self.figure3.add_subplot(1, 1, 1)
        self.axes_3.contour(self.xx, self.yy, self.cc, [0.3, 0.4, 0.5, 0.6, 0.7], colors='black', linewidths=1, zorder=2)
        self.axes_3_circle_plot = self.axes_3.contour(self.xx, self.yy, self.cc, [], colors='blue', linewidths=3, zorder=3)
        self.axes_3.set(xlim=(-2, 2), ylim=(-2, 2))
        self.axes_3.set_xticks([-2, 0, 2])
        self.axes_3.set_yticks([-2, 0, 2])
        self.axes_3.set_aspect('equal', 'box')

        self.axes_3.set_xlabel("$a1$")
        # self.axes_3.xaxis.set_label_coords(0.5, 0)
        self.axes_3.set_ylabel("$a2$")
        self.axes_3.yaxis.set_label_coords(-0.1, 0.5)

        for i in range(len(gd)):
            grad1 = gd[i]
            grad1 = grad1 / np.linalg.norm(grad1) / 2
            start1 = pxy1[i]

            if i != 24:  # Skip the middle point, where the gradient is zero
                self.axes_3.arrow(start1[0], start1[1], grad1[0] / 2, grad1[1] / 2, head_width=0.06, width=0.006, color='black',
                          zorder=4)

        self.canvas3.mpl_connect('button_press_event', self.on_mouseclick)
        self.canvas3.draw()


        self.axes_4 = self.figure4.add_subplot(projection='3d')

        self.norm = Normalize(self.cc.min(), self.cc.max())

        colors = cm.inferno(self.norm(self.cc))
        rcount, ccount, _ = colors.shape

        surf = self.axes_4.plot_surface(self.xx, self.yy, self.cc, rcount=rcount, ccount=ccount,
                               facecolors=colors, shade=False, linewidth=0.25)

        surf.set_facecolor((0, 0, 0, 0))

        fsize = 14

        self.axes_4.view_init(15, 250)
        self.axes_4.set_zticks([0.3, 0.5, .7])
        # self.axes_4.zaxis.set_tick_params(labelsize=fsize)
        self.axes_4.set_xlim((-2.0, 2.0))
        self.axes_4.set_ylim((-2.0, 2.0))
        self.axes_4.set_xticks([-2, 0, 2])
        # self.axes_4.xaxis.set_tick_params(labelsize=fsize)
        self.axes_4.set_yticks([-2, 0, 2])
        # self.axes_4.yaxis.set_tick_params(labelsize=fsize)
        self.axes_4.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
        self.axes_4.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
        self.axes_4.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

        # self.axes_4.tick_params(axis='x', labelsize=14)
        # self.axes_4.tick_params(axis='y', labelsize=14)
        # self.axes_4.zaxis.set_tick_params(labelsize=fsize)

        self.axes_4.set_xlabel("$a1$")
        self.axes_4.set_ylabel("$a2$")
        self.axes_4.set_zlabel("$V(a)$")

        self.canvas4.draw()

        self.contour_plot = self.surf1_plot = self.scat_plot = self.canvas3_scat_plot = None


    def on_mouseclick(self, event):
        if event.xdata != None and event.ydata != None:
            if self.contour_plot:
                self.contour_plot.remove()
                self.surf1_plot.remove()
                self.scat_plot.remove()
                self.canvas3_scat_plot.remove()

            xy_radius = np.sqrt(event.xdata ** 2 + event.ydata ** 2)
            xy_radius_range = np.sqrt(self.xx ** 2 + self.yy ** 2)
            self.contour_plot = self.axes_3.contour(self.xx, self.yy, xy_radius_range, [xy_radius], colors='blue', linewidths=2, zorder=3)
            self.canvas3_scat_plot = self.axes_3.scatter(event.xdata, event.ydata, marker='*', color='maroon', s=100, zorder=5)
            self.canvas3.draw()

            # Linearize the radial function at a point
            # Select the point where the linearization will occur
            linpoint = np.array([event.xdata, event.ydata])
            linpoint = np.expand_dims(linpoint, axis=0)

            # Compute the network output and the gradient at the point
            ag1 = self.net.sim(linpoint.transpose())
            gd1 = self.net.grad(ag1, 0)

            # Find the weight and bias of the linear network
            wlin = gd1
            blin = ag1[-1]

            # Find the linear response at the grid points
            alin = np.matmul(self.pxy, wlin) + blin - np.matmul(linpoint, wlin)

            clin = alin.reshape((41, 41))

            # Don't plot the linear function outside the bounds of the radial function
            clin[clin > self.cc.max()] = np.nan
            clin[clin < self.cc.min()] = np.nan

            # Make a surface plot of the radial function and the linear function
            mpl.rcParams['lines.markersize'] = 20

            colors1 = cm.inferno(self.norm(clin))
            rcount1, ccount1, _ = colors1.shape

            self.surf1_plot = self.axes_4.plot_surface(self.xx, self.yy, clin, rcount=rcount1, ccount=ccount1,
                                    facecolors=colors1, shade=False, linewidth=0.5)
            self.surf1_plot.set_facecolor((0, 0, 0, 0))

            # Put a star at the point where the linearization occurs
            self.scat_plot = self.axes_4.scatter(linpoint[0, 0], linpoint[0, 1], blin[0, 0], marker='*', color='black', s=100, zorder=5)
            self.scat_plot.set_sizes([200])
            self.canvas4.draw()

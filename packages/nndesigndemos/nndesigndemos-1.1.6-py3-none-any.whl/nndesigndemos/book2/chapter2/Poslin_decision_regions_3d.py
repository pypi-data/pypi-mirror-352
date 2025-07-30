from PyQt6 import QtWidgets
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
import ast

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.book2.chapter2.Poslin_decision_regions_base import PoslinDecisionRegionsBase


class PoslinDecisionRegions3D(PoslinDecisionRegionsBase):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PoslinDecisionRegions3D, self).__init__(w_ratio, h_ratio, dpi, post_title=' 2D')

        self.make_plot(1, (135, 240, 250, 250))
        self.update_values()

    def graph(self):
        self.figure.clf()
        ax = self.figure.add_subplot(projection='3d')

        p1 = np.linspace(-1, 3, 41)
        p2 = np.linspace(-1, 3, 41)
        P1, P2 = np.meshgrid(p1, p2)
        n1, n2 = P1.shape
        nump = n1 * n2
        pp1 = np.reshape(P1, nump, order='F')
        pp2 = np.reshape(P2, nump, order='F')
        p = np.concatenate((pp1.reshape(-1, 1).T, pp2.reshape(-1, 1).T), axis=0)
        func = np.vectorize(self.func1, otypes=[float])

        a1 = np.dot(self.w2.T, func(np.dot(self.w1, p) + np.dot(self.b1, np.ones((1, nump))))) + np.dot(self.b2, np.ones((1, nump)))
        aa = np.reshape(a1, (n1, n2), order='F')
        z11 = 0 * aa

        ax.plot_surface(P1, P2, aa)
        ax.plot_wireframe(P1, P2, z11, rcount=10, ccount=10)

        ax.grid(True, which='both')

        self.canvas.draw()

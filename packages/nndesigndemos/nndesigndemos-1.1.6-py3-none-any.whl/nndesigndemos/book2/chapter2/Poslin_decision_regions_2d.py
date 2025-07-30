import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.book2.chapter2.Poslin_decision_regions_base import PoslinDecisionRegionsBase


class PoslinDecisionRegions2D(PoslinDecisionRegionsBase):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PoslinDecisionRegions2D, self).__init__(w_ratio, h_ratio, dpi, post_title=' 2D')

        self.make_plot(1, (135, 240, 250, 250))
        self.update_values()

    def graph(self):
        self.figure.clf()
        a = self.figure.add_subplot(111)

        a.grid(True, which='both')

        p1 = np.linspace(-1, 3, 41)
        p2 = np.linspace(-1, 3, 41)
        P1, P2 = np.meshgrid(p1, p2)
        n1, n2 = P1.shape
        nump = n1 * n2
        pp1 = np.reshape(P1, nump, order='F')
        pp2 = np.reshape(P2, nump, order='F')
        p = np.concatenate((pp1.reshape(-1, 1).T, pp2.reshape(-1, 1).T), axis=0)
        func = np.vectorize(self.func1, otypes=[float])

        a1 = np.dot(self.w2.T, func(np.dot(self.w1, p) + np.dot(self.b1, np.ones((1, nump))))) + np.dot(self.b2, np.ones( (1, nump)))
        aa = np.reshape(a1, (n1, n2), order='F')

        a.contourf(P1, P2, aa, [0, 1000])

        a.grid(True, which='both')
        a.axhline(y=0, color='k')
        a.axvline(x=0, color='k')
        self.canvas.draw()

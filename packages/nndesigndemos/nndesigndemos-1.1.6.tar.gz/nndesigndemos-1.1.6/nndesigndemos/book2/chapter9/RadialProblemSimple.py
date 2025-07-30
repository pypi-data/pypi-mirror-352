import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.colors import Normalize


def logsig(n):
    return 1/(1+np.exp(-n))


def dlogsig(a):
    return a*(1-a)


# Define the Multilayer network class
class Multilayer():
    def __init__(self, weights, biases):
        self.weights = weights
        self.biases = biases
    # Simulate the network
    def sim(self, p):
        a = [p]
        atemp = p
        for w, b in zip(self.weights, self.biases):
            atemp = logsig(np.matmul(w,atemp) + b)
            a.append(atemp)
        return a
    # Compute the gradient of the network output (at category) with respect to the network input
    def grad(self, a, category):
        ww = self.weights.copy()
        aa = a.copy()
        ai = aa.pop()
        gradp = np.zeros(ai.shape)
        gradp[category, :] = 1

        # Compute the derivative across the last activation function
        gradp = dlogsig(ai) * gradp
        while aa:
            w = ww.pop()
            ai = aa.pop()
            if aa:
                # Compute derivative across weight and activation for middle layers
                gradp = dlogsig(ai) * (np.matmul(w.transpose(), gradp))
            else:
                # Compute derivative across the first weight
                gradp = np.matmul(w.transpose(), gradp)

        return gradp


if __name__ == '__main__':

    # Create the weights for the radial function
    w1 = np.array([ [-0.2], [-0.2]])
    b1 = np.array([ [2.], [-2.]])
    w2 = np.array([[-320, 320]])
    b2 = np.array([243.7])

    w1c = np.array([[-0.2489], [-0.3541]])
    b1c = np.array([[1.2931], [-2.6491]])
    w2c = np.array([[-6.6898,  69.3431]])
    b2c = np.array([1.6693])

    w1p = np.concatenate((np.concatenate((w1, np.zeros(w1.shape)),axis=1), np.concatenate((np.zeros(w1.shape),w1), axis=1)))
    b1p = np.concatenate((b1,b1))
    w2p = np.concatenate((np.concatenate((w2, np.zeros(w2.shape)),axis=1), np.concatenate((np.zeros(w2.shape),w2), axis=1)))
    b2p = np.concatenate((b2,b2))
    w3p = np.ones((1,2))
    b3p = np.array([0])
    b2p = np.expand_dims(b2p, axis=1)
    b3p = np.expand_dims(b3p, axis=1)
    wf1 = w1p
    bf1 = b1p
    wf2 = np.matmul(np.matmul(w1c,w3p),w2p)
    bf2 = np.matmul(np.matmul(w1c,w3p),b2p) + np.matmul(w1c,b3p) + b1c
    wf3 = w2c
    bf3 = b2c

    netweights = [wf1, wf2, wf3]
    netbiases =  [bf1, bf2, bf3]

    # Put the weights into a multilayer network object
    net = Multilayer(netweights, netbiases)

    # Make a grid of input points, in order to see the shape of the network response
    x = np.arange(-2, 2.1, 0.1)
    y = np.arange(-2, 2.1, 0.1)

    xx, yy = np.meshgrid(x, y)

    xxv = xx.reshape((1681,1))
    yyv = yy.reshape((1681,1))
    pxy = np.concatenate((xxv, yyv), axis=1)

    # Find the network response over the grid
    anet = net.sim(pxy.transpose())

    # Put the output in the grid shape
    cc = anet[-1].reshape((41,41))

    # Make a grid of input points where you want to see the gradient direction
    x1 = np.arange(-1.5, 2.0, 0.5)
    y1 = np.arange(-1.5, 2.0, 0.5)

    xx1, yy1 = np.meshgrid(x1, y1)

    xxv1 = xx1.reshape((49,1))
    yyv1 = yy1.reshape((49,1))
    pxy1 = np.concatenate((xxv1, yyv1), axis=1)

    # Compute the gradient at the grid points
    ag = net.sim(pxy1.transpose())
    gd = net.grad(ag, 0).transpose()

    fig, ax = plt.subplots(1, 1)
    ax.contour(xx, yy, cc, [0.3, 0.4, 0.5, 0.6, 0.7], colors='black', zorder=2)
    ax.contour(xx, yy, cc, [0.5], colors='red', linewidths=5, zorder=3)
    ax.set(xlim=(-2, 2), ylim=(-2, 2))
    ax.set_xticks([-2,  0,  2])
    ax.set_yticks([-2,  0,  2])
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.set_aspect('equal', 'box')

    # Plot arrows with the gradient direction at each point on top of the contour plot
    for i in range(len(gd)):
        grad1 = gd[i]
        grad1 = grad1/np.linalg.norm(grad1)/2
        start1 = pxy1[i]
        end1 = start1 + grad1

        if i!=24: # Skip the middle point, where the gradient is zero
            ax.arrow(start1[0], start1[1], grad1[0]/2, grad1[1]/2, head_width = 0.08, width = 0.008, color = 'black', zorder=4)

    fig.show()


    # Plot the 3D projection of the network response
    # These are the angles of the view of the response
    del1 = 15
    del2 = 255

    # Make a surface plot of the radial function and the linear function
    mpl.rcParams['lines.markersize'] = 20
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    norm = Normalize(cc.min(), cc.max())

    colors = cm.plasma(norm(cc))
    rcount, ccount, _ = colors.shape
    surf = ax.plot_surface(xx, yy, cc, rcount=rcount, ccount=ccount,
                           facecolors=colors, shade=False, linewidth=0.25)

    # Linearize the radial function at a point

    # Select the point where the linearization will occur
    linpoint = np.array([0.0, -1.0])
    linpoint = np.expand_dims(linpoint, axis=0)

    # Compute the network output and the gradient at the point
    ag1 = net.sim(linpoint.transpose())
    gd1 = net.grad(ag1, 0)

    # Find the weight and bias of the linear network
    wlin = gd1
    blin = ag1[-1]

    # Find the linear response at the grid points
    alin = np.matmul(pxy, wlin) + blin - np.matmul(linpoint, wlin)

    clin = alin.reshape((41,41))

    # Don't plot the linear function outside the bounds of the radial function
    clin[clin > cc.max()] = np.nan
    clin[clin < cc.min()] = np.nan

    colors1 = cm.plasma(norm(clin))
    rcount1, ccount1, _ = colors1.shape

    surf1 = ax.plot_surface(xx, yy, clin, rcount=rcount1, ccount=ccount1,
                            facecolors=colors1, shade=False, linewidth=0.5)

    surf1.set_facecolor((0,0,0,0))

    fsize = 14
    surf.set_facecolor((0,0,0,0))

    # Put a star at the point where the linearization occurs
    scat = ax.scatter(linpoint[0,0], linpoint[0,1], blin[0,0], marker='*', color='black', zorder=5)
    scat.set_sizes([200])
    ax.view_init(del1, del2)
    ax.set_zticks([0.3, 0.5, .7])
    ax.zaxis.set_tick_params(labelsize=fsize)
    ax.set_xlim((-2.0, 2.0))
    ax.set_ylim((-2.0, 2.0))
    ax.set_xticks([-2,  0,  2])
    ax.xaxis.set_tick_params(labelsize=fsize)
    ax.set_yticks([-2,  0,  2])
    ax.yaxis.set_tick_params(labelsize=fsize)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.zaxis.set_tick_params(labelsize=fsize)
    fig.show()

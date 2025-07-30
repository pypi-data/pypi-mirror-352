import numpy as np
import matplotlib.pyplot as plt

from nndesigndemos.book2.chapter4.DropoutDir.trainscg0 import trainscg0, preProcessing
from nndesigndemos.book2.chapter4.DropoutDir.simnet import simnet


def plot_contour(net1, Pd, Tl, fig, ax):

    # Plot decision boundary
    mx = [1.02, 1.02]
    mn = [-1, -1]
    xlim = [mn[0], mx[0]]
    ylim = [mn[1], mx[1]]

    dx = (mx[0] - mn[0]) / 101
    dy = (mx[1] - mn[1]) / 101
    xpts = np.arange(xlim[0], xlim[1], dx)
    ypts = np.arange(ylim[0], ylim[1], dy)

    if net1:
        X, Y = np.meshgrid(xpts, ypts)

        testInput = np.vstack([X.ravel(), Y.ravel()])
        net1['doflag'] = 0
        testOutputs = simnet(net1, testInput)
        testOutputs = testOutputs[1][0, :] - testOutputs[1][1, :]

        F = testOutputs.reshape(X.shape)
    else:
        F = np.zeros((101, 101))

    ax.contourf(xpts, ypts, F, levels=[-1, 0, 1], colors=['white', 'lightgreen'])

    # # Add a colorbar
    # fig.colorbar(contour, ax=ax)

    # Plot all points from Pd
    ax.plot(Pd[0, :], Pd[1, :], 'x', markersize=5, color='#1f77b4') # , label='All P points'

    # Identify indices where T(1,:) is non-zero
    ind = np.nonzero(Tl[0, :])[0]

    # Plot points with condition T(1, :)
    ax.plot(Pd[0, ind], Pd[1, ind], 'or', markersize=5) # , label='T(1,:) non-zero points'

    # Add reference lines
    ax.plot([-1, 1], [0, 0], 'k')  # Horizontal line
    ax.plot([0, 0], [-1, 1], 'k')    # Vertical line

    # Customize axis properties
    ax.set_aspect('equal', adjustable='box')  # Equivalent to plt.axis('square')
    ax.set_xlabel("p1")
    ax.set_ylabel("p2")

    ax.legend()


def testTrainSCG():
    # Check the last "yield tr['perf'][epoch]" line of the trainscg0 function
    # if an error occurs when we run the current code. A python function can
    # only be a generator function or a regular function. If the yield line
    # is not commented, it would be a generator function; Otherwise, a regular
    # function. The generator function with yield line is for the demo. And the
    # regular function without yield is for the code running here. So just
    # comment on the yield line to make the code work here.
    net0, Pd, Tl = preProcessing()

    net1, tr = trainscg0(net0, Pd, Tl)

    plt.plot(tr['perf'])  # Automatically uses index as x-axis if only y-data is provided
    plt.xlabel("Epoch")  # Label for the x-axis
    plt.ylabel("Value")  # Label for the y-axis
    plt.title("Line Plot of Data")  # Title of the plot
    plt.grid(True)  # Optional: adds a grid to the plot for readability

    # Display the plot
    plt.show()
    # exit()

    # Create a figure and an axis
    fig, ax = plt.subplots()
    plot_contour(net1, Pd, Tl, fig, ax)
    plt.show()

if __name__ == '__main__':
    # Run the function
    testTrainSCG()

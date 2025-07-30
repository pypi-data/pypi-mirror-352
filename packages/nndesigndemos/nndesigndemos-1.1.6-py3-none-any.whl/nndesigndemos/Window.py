from PyQt6 import QtWidgets, QtGui
from functools import partial

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH

# ----------------------------------------------------- Book 1 ---------------------------------------------------------
# ------ Chapter 2 --------
from nndesigndemos.book1.chapter2.One_input_neuron import OneInputNeuron
from nndesigndemos.book1.chapter2.Two_input_neuron import TwoInputNeuron
# ------ Chapter 3 --------
from nndesigndemos.book1.chapter3.Perceptron_classification import PerceptronClassification
from nndesigndemos.book1.chapter3.Hamming_classification import HammingClassification
from nndesigndemos.book1.chapter3.Hopfield_classification import HopfieldClassification
# ------ Chapter 4 --------
from nndesigndemos.book1.chapter4.Perceptron_rule import PerceptronRule
from nndesigndemos.book1.chapter4.Decision_boundary import DecisionBoundaries
# ------ Chapter 5 --------
from nndesigndemos.book1.chapter5.Gram_Schmidt import GramSchmidt
from nndesigndemos.book1.chapter5.Reciprocal_basis import ReciprocalBasis
# ------ Chapter 6 --------
from nndesigndemos.book1.chapter6.Linear_transformations import LinearTransformations
from nndesigndemos.book1.chapter6.Eigenvector_game import EigenvectorGame
# ------ Chapter 7 --------
from nndesigndemos.book1.chapter7.Supervised_Hebb import SupervisedHebb
# ------ Chapter 8 --------
from nndesigndemos.book1.chapter8.Taylor_series_1 import TaylorSeries1
from nndesigndemos.book1.chapter8.Taylor_series_2 import TaylorSeries2
from nndesigndemos.book1.chapter8.Directional_derivatives import DirectionalDerivatives
from nndesigndemos.book1.chapter8.Quadratic_function import QuadraticFunction
# ------ Chapter 9 --------
from nndesigndemos.book1.chapter9.Steepest_descent_quadratic import SteepestDescentQuadratic
from nndesigndemos.book1.chapter9.Comparison_of_methods import ComparisonOfMethods
from nndesigndemos.book1.chapter9.Newtons_method import NewtonsMethod
from nndesigndemos.book1.chapter9.Steepest_descent import SteepestDescent
# ------ Chapter 10 --------
from nndesigndemos.book1.chapter10.Adaptive_noise_cancellation import AdaptiveNoiseCancellation
from nndesigndemos.book1.chapter10.EEG_noise_cancellation import EEGNoiseCancellation
from nndesigndemos.book1.chapter10.Linear_classification import LinearClassification
# ------ Chapter 11 -------
from nndesigndemos.book1.chapter11.Function_approximation import FunctionApproximation
from nndesigndemos.book1.chapter11.Network_function import NetworkFunction
from nndesigndemos.book1.chapter11.Generalization import Generalization
# ------ Chapter 12 -------
from nndesigndemos.book1.chapter12.Steepest_descent_backprop_1 import SteepestDescentBackprop1
from nndesigndemos.book1.chapter12.Steepest_descent_backprop_2 import SteepestDescentBackprop2
from nndesigndemos.book1.chapter12.Momentum import Momentum
from nndesigndemos.book1.chapter12.Variable_learning_rate import VariableLearningRate
from nndesigndemos.book1.chapter12.Conjugate_gradient_line_search import ConjugateGradientLineSearch
from nndesigndemos.book1.chapter12.Conjugate_gradient import ConjugateGradient
from nndesigndemos.book1.chapter12.Marquardt_step import MarquardtStep
from nndesigndemos.book1.chapter12.Marquardt import Marquardt
# ------ Chapter 13 -------
from nndesigndemos.book1.chapter13.Early_stopping import EarlyStopping
from nndesigndemos.book1.chapter13.Regularization import Regularization
from nndesigndemos.book1.chapter13.Bayesian_regularization import BayesianRegularization
from nndesigndemos.book1.chapter13.Early_stoppping_regularization import EarlyStoppingRegularization
# ------ Chapter 14 -------
from nndesigndemos.book1.chapter14.FIR_network import FIRNetwork
from nndesigndemos.book1.chapter14.IIR_network import IIRNetwork
from nndesigndemos.book1.chapter14.Dynamic_derivatives import DynamicDerivatives
from nndesigndemos.book1.chapter14.Recurrent_network_training import RecurrentNetworkTraining
# ------ Chapter 15 -------
from nndesigndemos.book1.chapter15.Unsupervised_hebb_v3 import UnsupervisedHebb
from nndesigndemos.book1.chapter15.Effects_of_decay_rate import EffectsOfDecayRate
from nndesigndemos.book1.chapter15.Hebb_with_decay_v3 import HebbWithDecay
from nndesigndemos.book1.chapter15.Graphical_instar import GraphicalInstar
from nndesigndemos.book1.chapter15.Outstar_v3 import OutStar
# ------ Chapter 16 -------
from nndesigndemos.book1.chapter16.Competitive_classification import CompetitiveClassification
from nndesigndemos.book1.chapter16.Competitive_learning import CompetitiveLearning
from nndesigndemos.book1.chapter16.OneD_feature_map import OneDFeatureMap
from nndesigndemos.book1.chapter16.TwoD_feature_map import TwoDFeatureMap
from nndesigndemos.book1.chapter16.Lvq1 import LVQ1
from nndesigndemos.book1.chapter16.Lvq2 import LVQ2
# ------ Chapter 17 -------
from nndesigndemos.book1.chapter17.Network_function_radial import NetworkFunctionRadial
from nndesigndemos.book1.chapter17.Pattern_classification import PatternClassification
from nndesigndemos.book1.chapter17.Linear_least_squares import LinearLeastSquares
from nndesigndemos.book1.chapter17.Orthogonal_least_squares import OrthogonalLeastSquares
from nndesigndemos.book1.chapter17.Nonlinear_optimization import NonlinearOptimization
# ------ Chapter 18 -------
from nndesigndemos.book1.chapter18.Leaky_integrator import LeakyIntegrator
from nndesigndemos.book1.chapter18.Shunting_network import ShuntingNetwork
from nndesigndemos.book1.chapter18.Grossberg_layer_1 import GrossbergLayer1
from nndesigndemos.book1.chapter18.Grossberg_layer_2 import GrossbergLayer2
from nndesigndemos.book1.chapter18.Adaptive_weights import AdaptiveWeights
# ------ Chapter 19 -------
from nndesigndemos.book1.chapter19.Art1_layer1 import ART1Layer1
from nndesigndemos.book1.chapter19.Art1_layer2 import ART1Layer2
from nndesigndemos.book1.chapter19.Orienting_subsystem import OrientingSubsystem
from nndesigndemos.book1.chapter19.Art1_algorithm import ART1Algorithm
# ------ Chapter 20 -------
from nndesigndemos.book1.chapter20.Dynamical_system import DynamicalSystem
# ------ Chapter 21 -------
from nndesigndemos.book1.chapter21.Hopfield_network import HopfieldNetwork

# ----------------------------------------------------- Book 2 ---------------------------------------------------------
# ------ Chapter 2 --------
from nndesigndemos.book2.chapter2.Poslin_network_function import PoslinNetworkFunction
from nndesigndemos.book2.chapter2.Poslin_decision_regions import PoslinDecisionRegions
from nndesigndemos.book2.chapter2.Poslin_decision_regions_2d import PoslinDecisionRegions2D
from nndesigndemos.book2.chapter2.Poslin_decision_regions_3d import PoslinDecisionRegions3D
from nndesigndemos.book2.chapter2.Cascaded_function import CascadedFunction
# ------ Chapter 3 --------
from nndesigndemos.book2.chapter3.Gradient_descent import GradientDescent
from nndesigndemos.book2.chapter3.Gradient_descent_stochastic import GradientDescentStochastic
# ------ Chapter 4 --------
from nndesigndemos.book2.chapter4.Scaling import Scaling
from nndesigndemos.book2.chapter4.Initialization_effect import InitEffect
from nndesigndemos.book2.chapter4.Dropout import Dropout
# ------ Chapter 5 --------
from nndesigndemos.book2.chapter5.Cheatsheet5 import Cheatsheet5
# ------ Chapter 6 --------
from nndesigndemos.book2.chapter6.Cheatsheet6 import Cheatsheet6
# ------ Chapter 8 --------
from nndesigndemos.book2.chapter8.Convolution_networks_ani import ConvolAnimation as Convol
# from nndesigndemos.book2.chapter8.Convolution_networks import Convol
# ------ Chapter 9 --------
from nndesigndemos.book2.chapter9.LinearizedNetworkResponse import LinearizedNetworkResponse
# ------ Chapter 10 --------
from nndesigndemos.book2.chapter10.Cheatsheet10 import Cheatsheet10
# ------ Chapter 11 --------
from nndesigndemos.book2.chapter11.Linear_sequence_processing import LinearSequenceProcessing


# -------------------------------------------------------------------------------------------------------------
xlabel, ylabel, wlabel, hlabel, add = 120, 5, 500, 100, 20
xautor, yautor = 385, 600

xcm1, ycm1, wcm1, hcm1, add1, subt = 190, 140, 250, 20, 140, 20
xcm2 = 198
xbtn1, ybtn1, wbtn1, hbtn1, add2 = 10, 635, 60, 30, 65

w_Logo1, h_Logo1, xL_g1, yL_g1, add_l = 100, 80, 90, 110, 140

BOOK1_CHAPTERS_DEMOS = {
    2: ["Neuron Model & Network Architecture", "Chapter 2 demos", "One-input Neuron", "Two-input Neuron"],
    3: ["An Illustrative Example", "Chapter 3 demos", "Perceptron classification", "Hamming classification", "Hopfield classification"],
    4: ["Perceptron Learning Rule", "Chapter 4 demos", "Decision boundaries", "Perceptron rule"],
    5: ["Signal & weight Vector Spaces", "Chapter 5 demos", "Gram schmidt", "Reciprocal basis"],
    6: ["Linear Transformations For N. Networks", "Chapter 6 demos", "Linear transformations", "Eigenvector game"],
    7: ["Supervised Hebb", "Chapter 7 demos", "Supervised Hebb"],
    8: ["Performance Surfaces & Optimum Points", "Chapter 8 demos", "Taylor series #1", "Taylor series #2", "Directional derivatives", "Quadratic function"],
    9: ["Performance Optimization", "Chapter 9 demos", "Steepest descent for Quadratic", "Method comparison", "Newton's method", "Steepest descent"],
    10: ["Widrow - Hoff Learning", "Chapter 10 demos", "Adaptive noise cancellation", "EEG noise cancellation", "Linear classification"],
    # 11: ["Backpropagation", "Chapter 11 demos", "Network Function", "Backpropagation Calculation", "Function Approximation", "Generalization"],
    11: ["Backpropagation", "Chapter 11 demos", "Network Function", "Function Approximation", "Generalization"],
    12: ["Variations on Backpropagation", "Chapter 12 demos", "Steepest Descent #1", "Steepest Descent #2", "Momentum", "Variable Learning Rate", "CG Line Search", "Conjugate Gradient", "Marquardt Step", "Marquardt"],
    13: ["Generalization", "Chapter 13 demos", "Early Stopping", "Regularization", "Bayesian Regularization", "Early Stopping-Regularization"],
    14: ["Dynamic Networks", "Chapter 14 demos", "FIR Network", "IIR Network", "Dynamic Derivatives", "Recurrent Network Training"],
    15: ["Associative Learning", "Chapter 15 demos", "Unsupervised Hebb", "Effects of Decay Rate", "Hebb with Decay", "Graphical Instar", "Outstar"],
    16: ["Competitive Networks", "Chapter 16 demos", "Competitive Classification", "Competitive Learning", "1-D Feature Map", "2-D Feature Map", "LVQ 1", "LVQ 2"],
    17: ["Radial Basis Function", "Chapter 17 demos", "Network Function Radial", "Pattern Classification", "Linear Least Squares", "Orthogonal Least Squares", "Non Linear Optimization"],
    18: ["Grossberg Network", "Chapter 18 demos", "Leaky Integrator", "Shunting Network", "Grossberg Layer 1", "Grossberg Layer 2", "Adaptive Weights"],
    19: ["Adaptive Resonance Theory", "Chapter 19 demos", "ART1 Layer 1", "ART1 Layer 2", "Orienting Subsystem", "ART1 Algorithm"],
    20: ["Stability", "Chapter 20 demos", "Dynamical System"],
    21: ["Hopfield Network", "Chapter 21 demos", "Hopfield Network"]
}

BOOK2_CHAPTERS_DEMOS = {
    2: ["Multilayer Networks", "Chapter 2 demos", "Poslin Network Function", "Poslin Decision Regions", "Poslin Decision Regions 2D", "Poslin Decision Regions 3D", "Cascaded Function"],
    3: ["Multilayer Network Train", "Chapter 3 demos", "Gradient Descent", "Gradient Descent Stochastic"],
    4: ["Supplemental Training", "Chapter 4 demos", 'Normalization & Initialization Scaling', 'Normalization & Initialization Effect', 'Dropout'],
    5: ["Python Intro", "Chapter 5 demos", "Cheatsheet"],
    6: ["TensorFlow Intro", "Chapter 6 demos", "Cheatsheet"],
    7: ["Chapter 7", "Chapter 7 demos", ],
    8: ["Convolution Networks", "Chapter 8 demos", "Convolution Networks demo"],
    9: ["PostTrain", "Chapter 9 demos", "Linearized Network Response"],
    10: ["PyTorch Intro", "Chapter 10 demos", "Cheatsheet"],
    11: ["Linear Sequence", "Chapter 11 demos", "Linear Sequence Processing"],
    12: ["LSTM", "Chapter 12 demos", ],
}
# -------------------------------------------------------------------------------------------------------------


class MainWindowNN(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        """ Main Window for the Neural Network Design Book. Inherits basic layout from NNDLayout """
        super(MainWindowNN, self).__init__(w_ratio, h_ratio, dpi, chapter_window=False, main_menu=1, draw_vertical=False)

        self.make_label("label_3", "Table of Contents", (380, ylabel + add, wlabel, hlabel), font_size=18)
        self.make_label("label4", "By Hagan, Jafari, Uría", (xautor, yautor, wlabel, hlabel))

        font_size = 14
        if self.running_on_windows:
            font_size = int(font_size * 0.8)
        elif self.running_on_linux:
            font_size = int(font_size * 0.8)
        else:
            font_size = int(font_size * (self.w_ratio + self.h_ratio) / 2)

        # ---- Chapter icons and dropdown menus ----

        # Creates attributed for each window as None until clicked
        for i in range(2, 22):
            for j in BOOK1_CHAPTERS_DEMOS[i][2:]:
                setattr(self, "chapter{}_window{}".format(i, j), None)

        self.icon1 = QtWidgets.QLabel(self)
        self.comboBox1 = QtWidgets.QComboBox(self)
        self.comboBox1.connected = False  # Need to create this attribute so that we don't have more than one connected function
        self.comboBox1.setGeometry(xcm1 * self.w_ratio, ycm1 * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box1 = QtWidgets.QLabel(self)
        self.label_box1.setGeometry(xcm2 * self.w_ratio, (ycm1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box1.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon2 = QtWidgets.QLabel(self)
        self.comboBox2 = QtWidgets.QComboBox(self)
        self.comboBox2.connected = False
        self.comboBox2.setGeometry(xcm1 * self.w_ratio, (ycm1 + add1) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box2 = QtWidgets.QLabel(self)
        self.label_box2.setGeometry(xcm2 * self.w_ratio, (ycm1 + add1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box2.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon3 = QtWidgets.QLabel(self)
        self.comboBox3 = QtWidgets.QComboBox(self)
        self.comboBox3.connected = False
        self.comboBox3.setGeometry(xcm1 * self.w_ratio, (ycm1 + 2 * add1) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box3 = QtWidgets.QLabel(self)
        self.label_box3.setGeometry(xcm2 * self.w_ratio, (ycm1 + 2 * add1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box3.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon4 = QtWidgets.QLabel(self)
        self.comboBox4 = QtWidgets.QComboBox(self)
        self.comboBox4.connected = False
        self.comboBox4.setGeometry(xcm1 * self.w_ratio, (ycm1 + 3 * add1) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box4 = QtWidgets.QLabel(self)
        self.label_box4.setGeometry(xcm2 * self.w_ratio, (ycm1 + 3 * add1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box4.setFont(QtGui.QFont("Times New Roman", font_size))

        # self.show_chapters()

        # ---- Buttons at the bottom to switch between blocks of chapters ----

        self.button1 = QtWidgets.QPushButton(self)
        self.button1.setText("2-5")
        self.button1.setGeometry(xbtn1 * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button1.clicked.connect(partial(self.show_chapters, "2-5"))

        self.button2 = QtWidgets.QPushButton(self)
        self.button2.setText("6-9")
        self.button2.setGeometry((xbtn1 + add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button2.clicked.connect(partial(self.show_chapters, "6-9"))

        self.button3 = QtWidgets.QPushButton(self)
        self.button3.setText("10-13")
        self.button3.setGeometry((xbtn1 + 2 * add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button3.clicked.connect(partial(self.show_chapters, "10-13"))

        self.button4 = QtWidgets.QPushButton(self)
        self.button4.setText("14-17")
        self.button4.setGeometry((xbtn1 + 3 * add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button4.clicked.connect(partial(self.show_chapters, "14-17"))

        self.button5 = QtWidgets.QPushButton(self)
        self.button5.setText("18-21")
        self.button5.setGeometry((xbtn1 + 4 * add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button5.clicked.connect(partial(self.show_chapters, "18-21"))

        self.center()

        self.show_chapters()

    def show_chapters(self, chapters="2-5"):
        """ Updates the icons and dropdown menus based on a block of chapters (chapters) """

        chapters = chapters.split("-")
        chapter_numbers = list(range(int(chapters[0]), int(chapters[1]) + 1))
        chapter_functions = [self.chapter2, self.chapter3, self.chapter4, self.chapter5, self.chapter6, self.chapter7,
                             self.chapter8, self.chapter9, self.chapter10, self.chapter11, self.chapter12, self.chapter13,
                             self.chapter14, self.chapter15, self.chapter16, self.chapter17, self.chapter18, self.chapter19,
                             self.chapter20, self.chapter21]

        idx = 0
        for icon in [self.icon1, self.icon2, self.icon3, self.icon4]:
            icon.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Logo/book_logos/{}.svg".format(chapter_numbers[idx])).pixmap(
                w_Logo1 * self.w_ratio, h_Logo1 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            icon.setGeometry(xL_g1 * self.w_ratio, (yL_g1 + idx * add_l) * self.h_ratio, w_Logo1 * self.w_ratio, h_Logo1 * self.h_ratio)
            icon.repaint()
            idx += 1

        idx = 0
        for label_box, comboBox in zip([self.label_box1, self.label_box2, self.label_box3, self.label_box4],
                                       [self.comboBox1, self.comboBox2, self.comboBox3, self.comboBox4]):
            label_box.setText(BOOK1_CHAPTERS_DEMOS[chapter_numbers[idx]][0])
            label_box.repaint()
            if comboBox.connected:
                comboBox.currentIndexChanged.disconnect()
            comboBox.clear()
            comboBox.addItems(BOOK1_CHAPTERS_DEMOS[chapter_numbers[idx]][1:])
            comboBox.currentIndexChanged.connect(chapter_functions[chapter_numbers[idx] - 2])
            comboBox.connected = True
            comboBox.repaint()
            idx += 1

        # QtWidgets.QApplication.processEvents()
        # QtWidgets.QApplication.processEvents()
        # QtWidgets.QApplication.processEvents()
        # self.show()

    def chapter2(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.chapter2_window1 = OneInputNeuron(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter2_window1.show()
        elif idx == 2:
            self.chapter2_window2 = TwoInputNeuron(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter2_window2.show()

    def chapter3(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.chapter3_window1 = PerceptronClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter3_window1.show()
        if idx == 2:
            self.chapter3_window2 = HammingClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter3_window2.show()
        elif idx == 3:
            self.chapter3_window3 = HopfieldClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter3_window3.show()

    def chapter4(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.chapter4_window1 = DecisionBoundaries(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter4_window1.show()
        elif idx == 2:
            self.chapter4_window2 = PerceptronRule(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter4_window2.show()

    def chapter5(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.chapter5_window1 = GramSchmidt(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter5_window1.show()
        elif idx == 2:
            self.chapter5_window2 = ReciprocalBasis(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter5_window2.show()

    def chapter6(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.chapter6_window1 = LinearTransformations(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter6_window1.show()
        elif idx == 2:
            self.chapter6_window2 = EigenvectorGame(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter6_window2.show()

    def chapter7(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.chapter7_window1 = SupervisedHebb(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter7_window1.show()

    def chapter8(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.chapter8_window1 = TaylorSeries1(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter8_window1.show()
        elif idx == 2:
            self.chapter8_window2 = TaylorSeries2(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter8_window2.show()
        elif idx == 3:
            self.chapter8_window3 = DirectionalDerivatives(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter8_window3.show()
        elif idx == 4:
            self.chapter8_window4 = QuadraticFunction(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter8_window4.show()

    def chapter9(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.chapter9_window1 = SteepestDescentQuadratic(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter9_window1.show()
        elif idx == 2:
            self.chapter9_window2 = ComparisonOfMethods(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter9_window2.show()
        elif idx == 3:
            self.chapter9_window3 = NewtonsMethod(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter9_window3.show()
        elif idx == 4:
            self.chapter9_window4 = SteepestDescent(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter9_window4.show()

    def chapter10(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.chapter10_window1 = AdaptiveNoiseCancellation(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter10_window1.show()
        elif idx == 2:
            self.chapter10_window2 = EEGNoiseCancellation(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter10_window2.show()
        elif idx == 3:
            self.chapter10_window3 = LinearClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter10_window3.show()

    def chapter11(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.chapter11_window1 = NetworkFunction(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter11_window1.show()
        # elif idx == 2:
        #     self.chapter_window2 = BackpropagationCalculation(self.w_ratio, self.h_ratio)
        #     self.chapter_window2.show()
        elif idx == 2:
            self.chapter11_window3 = FunctionApproximation(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter11_window3.show()
        elif idx == 3:
            self.chapter11_window4 = Generalization(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter11_window4.show()

    def chapter12(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.chapter12_window1 = SteepestDescentBackprop1(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window1.show()
        elif idx == 2:
            self.chapter12_window2 = SteepestDescentBackprop2(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window2.show()
        elif idx == 3:
            self.chapter12_window3 = Momentum(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window3.show()
        elif idx == 4:
            self.chapter12_window4 = VariableLearningRate(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window4.show()
        elif idx == 5:
            self.chapter12_window5 = ConjugateGradientLineSearch(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window5.show()
        elif idx == 6:
            self.chapter12_window6 = ConjugateGradient(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window6.show()
        elif idx == 7:
            self.chapter12_window7 = MarquardtStep(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window7.show()
        elif idx == 8:
            self.chapter12_window8 = Marquardt(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter12_window8.show()

    def chapter13(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.chapter13_window1 = EarlyStopping(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter13_window1.show()
        elif idx == 2:
            self.chapter13_window2 = Regularization(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter13_window2.show()
        elif idx == 3:
            self.chapter13_window3 = BayesianRegularization(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter13_window3.show()
        elif idx == 4:
            self.chapter13_window4 = EarlyStoppingRegularization(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter13_window4.show()

    def chapter14(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.chapter14_window1 = FIRNetwork(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter14_window1.show()
        elif idx == 2:
            self.chapter14_window2 = IIRNetwork(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter14_window2.show()
        elif idx == 3:
            self.chapter14_window3 = DynamicDerivatives(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter14_window3.show()
        elif idx == 4:
            self.chapter14_window4 = RecurrentNetworkTraining(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter14_window4.show()

    def chapter15(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.chapter15_window1 = UnsupervisedHebb(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter15_window1.show()
        elif idx == 2:
            self.chapter15_window2 = EffectsOfDecayRate(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter15_window2.show()
        elif idx == 3:
            self.chapter15_window3 = HebbWithDecay(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter15_window3.show()
        elif idx == 4:
            self.chapter15_window4 = GraphicalInstar(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter15_window4.show()
        elif idx == 5:
            self.chapter15_window5 = OutStar(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter15_window5.show()

    def chapter16(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.chapter16_window1 = CompetitiveClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window1.show()
        elif idx == 2:
            self.chapter16_window2 = CompetitiveLearning(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window2.show()
        elif idx == 3:
            self.chapter16_window3 = OneDFeatureMap(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window3.show()
        elif idx == 4:
            self.chapter16_window4 = TwoDFeatureMap(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window4.show()
        elif idx == 5:
            self.chapter16_window5 = LVQ1(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window5.show()
        elif idx == 6:
            self.chapter16_window6 = LVQ2(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter16_window6.show()

    def chapter17(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.chapter17_window1 = NetworkFunctionRadial(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter17_window1.show()
        elif idx == 2:
            self.chapter17_window2 = PatternClassification(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter17_window2.show()
        elif idx == 3:
            self.chapter17_window3 = LinearLeastSquares(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter17_window3.show()
        elif idx == 4:
            self.chapter17_window4 = OrthogonalLeastSquares(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter17_window4.show()
        elif idx == 5:
            self.chapter17_window5 = NonlinearOptimization(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter17_window5.show()

    def chapter18(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.chapter18_window1 = LeakyIntegrator(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter18_window1.show()
        elif idx == 2:
            self.chapter18_window2 = ShuntingNetwork(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter18_window2.show()
        elif idx == 3:
            self.chapter18_window3 = GrossbergLayer1(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter18_window3.show()
        elif idx == 4:
            self.chapter18_window4 = GrossbergLayer2(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter18_window4.show()
        elif idx == 5:
            self.chapter18_window5 = AdaptiveWeights(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter18_window5.show()

    def chapter19(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.chapter19_window1 = ART1Layer1(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter19_window1.show()
        elif idx == 2:
            self.chapter19_window2 = ART1Layer2(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter19_window2.show()
        elif idx == 3:
            self.chapter19_window3 = OrientingSubsystem(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter19_window3.show()
        elif idx == 4:
            self.chapter19_window4 = ART1Algorithm(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter19_window4.show()

    def chapter20(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.chapter20_window1 = DynamicalSystem(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter20_window1.show()

    def chapter21(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.chapter21_window1 = HopfieldNetwork(self.w_ratio, self.h_ratio, self.dpi)
            self.chapter21_window1.show()


class MainWindowDL(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        """ Main Window for the Neural Network Design - Deep Learning Book. Inherits basic layout from NNDLayout """
        super(MainWindowDL, self).__init__(w_ratio, h_ratio, dpi, chapter_window=False, main_menu=2, draw_vertical=False)

        self.make_label("label_3", "Table of Contents", (380, ylabel + add, wlabel, hlabel), font_size=18)
        self.make_label("label4", "By Hagan, Jafari, Qi", (xautor, yautor, wlabel, hlabel))

        font_size = 14
        if self.running_on_windows:
            font_size = int(font_size * 0.8)
        elif self.running_on_linux:
            font_size = int(font_size * 0.8)
        else:
            font_size = int(font_size * (self.w_ratio + self.h_ratio) / 2)

        # ---- Chapter icons and dropdown menus ----

        # Creates attributed for each window as None until clicked
        for i in range(2, len(BOOK2_CHAPTERS_DEMOS)+2):
            for j in BOOK2_CHAPTERS_DEMOS[i][2:]:
                setattr(self, "book2_chapter{}_window{}".format(i, j), None)

        self.icon1 = QtWidgets.QLabel(self)
        self.comboBox1 = QtWidgets.QComboBox(self)
        self.comboBox1.connected = False  # Need to create this attribute so that we don't have more than one connected function
        self.comboBox1.setGeometry(xcm1 * self.w_ratio, ycm1 * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box1 = QtWidgets.QLabel(self)
        self.label_box1.setGeometry(xcm2 * self.w_ratio, (ycm1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box1.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon2 = QtWidgets.QLabel(self)
        self.comboBox2 = QtWidgets.QComboBox(self)
        self.comboBox2.connected = False
        self.comboBox2.setGeometry(xcm1 * self.w_ratio, (ycm1 + add1) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box2 = QtWidgets.QLabel(self)
        self.label_box2.setGeometry(xcm2 * self.w_ratio, (ycm1 + add1 - subt) * self.h_ratio, wcm1 * self.w_ratio, hcm1 * self.h_ratio)
        self.label_box2.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon3 = QtWidgets.QLabel(self)
        self.comboBox3 = QtWidgets.QComboBox(self)
        self.comboBox3.connected = False
        self.comboBox3.setGeometry(xcm1 * self.w_ratio, (ycm1 + add1 * 2) * self.h_ratio, wcm1 * self.w_ratio,
                                   hcm1 * self.h_ratio)
        self.label_box3 = QtWidgets.QLabel(self)
        self.label_box3.setGeometry(xcm2 * self.w_ratio, (ycm1 + add1 * 2 - subt) * self.h_ratio, wcm1 * self.w_ratio,
                                    hcm1 * self.h_ratio)
        self.label_box3.setFont(QtGui.QFont("Times New Roman", font_size))

        self.icon4 = QtWidgets.QLabel(self)
        self.comboBox4 = QtWidgets.QComboBox(self)
        self.comboBox4.connected = False
        self.comboBox4.setGeometry(xcm1 * self.w_ratio, (ycm1 + add1 * 3) * self.h_ratio, wcm1 * self.w_ratio,
                                   hcm1 * self.h_ratio)
        self.label_box4 = QtWidgets.QLabel(self)
        self.label_box4.setGeometry(xcm2 * self.w_ratio, (ycm1 + add1 * 3 - subt) * self.h_ratio, wcm1 * self.w_ratio,
                                    hcm1 * self.h_ratio)
        self.label_box4.setFont(QtGui.QFont("Times New Roman", font_size))
        # self.show_chapters()

        # ---- Buttons at the bottom to switch between blocks of chapters ----

        self.button1 = QtWidgets.QPushButton(self)
        self.button1.setText("2-5")
        self.button1.setGeometry(xbtn1 * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button1.clicked.connect(partial(self.show_chapters, "2-5"))

        self.button2 = QtWidgets.QPushButton(self)
        self.button2.setText("6-9")
        self.button2.setGeometry((xbtn1 + add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button2.clicked.connect(partial(self.show_chapters, "6-9"))

        self.button3 = QtWidgets.QPushButton(self)
        self.button3.setText("10-12")
        self.button3.setGeometry((xbtn1 + 2 * add2) * self.w_ratio, ybtn1 * self.h_ratio, wbtn1 * self.w_ratio, hbtn1 * self.h_ratio)
        self.button3.clicked.connect(partial(self.show_chapters, "10-12"))

        self.center()

        self.show_chapters()

    def change_visibility(self, visible):
        self.icon4.setVisible(visible)
        self.label_box4.setVisible(visible)
        self.comboBox4.setVisible(visible)

    def show_chapters(self, chapters="2-5"):
        """ Updates the icons and dropdown menus based on a block of chapters (chapters) """

        if chapters in ["2-5", "6-9"]:
            icon_lst = [self.icon1, self.icon2, self.icon3, self.icon4]
            label_lst = [self.label_box1, self.label_box2, self.label_box3, self.label_box4]
            combo_lst = [self.comboBox1, self.comboBox2, self.comboBox3, self.comboBox4]
            self.change_visibility(True)
        elif chapters == "10-12":
            icon_lst = [self.icon1, self.icon2, self.icon3]
            label_lst = [self.label_box1, self.label_box2, self.label_box3]
            combo_lst = [self.comboBox1, self.comboBox2, self.comboBox3]
            self.change_visibility(False)

        chapters = chapters.split("-")
        chapter_numbers = list(range(int(chapters[0]), int(chapters[1]) + 1))

        chapter_functions = [
            self.chapter2, self.chapter3, self.chapter4, self.chapter5,
            self.chapter6, self.chapter7, self.chapter8, self.chapter9,
            self.chapter10, self.chapter11, self.chapter12,
        ]

        idx = 0
        for icon in icon_lst:  # TODO: Change logo path when we have them
            icon.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Logo/book2_logos/{}.svg".format(chapter_numbers[idx])).pixmap(
                w_Logo1, h_Logo1, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
            # icon.setGeometry(xL_g1, yL_g1 + idx * add_l, w_Logo1, h_Logo1)
            icon.setGeometry(xL_g1 * self.w_ratio, (yL_g1 + idx * add_l) * self.h_ratio, w_Logo1 * self.w_ratio, h_Logo1 * self.h_ratio)
            icon.repaint()
            idx += 1

        idx = 0
        for label_box, comboBox in zip(label_lst, combo_lst):
            label_box.setText(BOOK2_CHAPTERS_DEMOS[chapter_numbers[idx]][0])
            label_box.repaint()
            if comboBox.connected:
                comboBox.currentIndexChanged.disconnect()
            comboBox.clear()
            comboBox.addItems(BOOK2_CHAPTERS_DEMOS[chapter_numbers[idx]][1:])
            comboBox.currentIndexChanged.connect(chapter_functions[chapter_numbers[idx] - 2])
            comboBox.connected = True
            comboBox.repaint()
            idx += 1

        # self.show()
        # QtWidgets.QApplication.processEvents()
        # QtWidgets.QApplication.processEvents()
        # QtWidgets.QApplication.processEvents()

    def chapter2(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter2_window1 = PoslinNetworkFunction(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter2_window1.show()
        elif idx == 2:
            self.book2_chapter2_window2 = PoslinDecisionRegions(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter2_window2.show()
        elif idx == 3:
            self.book2_chapter2_window3 = PoslinDecisionRegions2D(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter2_window3.show()
        elif idx == 4:
            self.book2_chapter2_window4 = PoslinDecisionRegions3D(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter2_window4.show()
        elif idx == 5:
            self.book2_chapter2_window5 = CascadedFunction(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter2_window5.show()

    def chapter3(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter3_window1 = GradientDescent(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter3_window1.show()
        elif idx == 2:
            self.book2_chapter3_window2 = GradientDescentStochastic(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter3_window2.show()

    def chapter4(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter4_window1 = Scaling(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter4_window1.show()
        elif idx == 2:
            self.book2_chapter4_window2 = InitEffect(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter4_window2.show()
        elif idx == 3:
            self.book2_chapter4_window3 = Dropout(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter4_window3.show()

    def chapter5(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter5_window1 = Cheatsheet5(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter5_window1.show()

    def chapter6(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter6_window1 = Cheatsheet6(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter6_window1.show()

    def chapter7(self, idx):
        self.comboBox2.setCurrentIndex(0)

    def chapter8(self, idx):
        self.comboBox3.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter8_window1 = Convol(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter8_window1.show()

    def chapter9(self, idx):
        self.comboBox4.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter9_window1 = LinearizedNetworkResponse(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter9_window1.show()

    def chapter10(self, idx):
        self.comboBox1.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter10_window1 = Cheatsheet10(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter10_window1.show()

    def chapter11(self, idx):
        self.comboBox2.setCurrentIndex(0)
        if idx == 1:
            self.book2_chapter11_window1 = LinearSequenceProcessing(self.w_ratio, self.h_ratio, self.dpi)
            self.book2_chapter11_window1.show()

    def chapter12(self, idx):
        self.comboBox3.setCurrentIndex(0)

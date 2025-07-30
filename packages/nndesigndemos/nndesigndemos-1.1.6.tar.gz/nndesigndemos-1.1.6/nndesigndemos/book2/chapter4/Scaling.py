from PyQt6 import QtWidgets, QtCore
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.book2.chapter4.deephist import deephist


class Scaling(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Scaling, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Normalization & Initialization Scaling", 4,
                          "\nChoose a initialization\nscheme and whether to\nuse BatchNorm or not."
                          "\n\nThe distribution of input,\nnet input and output\nis shown on the left.\n\n",
                          PACKAGE_PATH + "Chapters/4_D/Logo_Ch_4.svg", None, 2,
                          icon_move_left=120, description_coords=(535, 105, 450, 250))

        plot_size = 200
        plot_x1 = 50
        plot_x2 = 280
        plot_y1 = 90
        plot_y2 = 280
        plot_y3 = 470

        self.make_plot('Input', (plot_x1, plot_y1, plot_size, plot_size))
        self.figureInput.set_tight_layout(True)

        self.make_plot('Output1', (plot_x1, plot_y2, plot_size, plot_size))
        self.figureOutput1.set_tight_layout(True)

        self.make_plot('Output2', (plot_x2, plot_y2, plot_size, plot_size))
        self.figureOutput2.set_tight_layout(True)

        self.make_plot('Output3', (plot_x1, plot_y3, plot_size, plot_size))
        self.figureOutput3.set_tight_layout(True)

        self.make_plot('Output4', (plot_x2, plot_y3, plot_size, plot_size))
        self.figureOutput4.set_tight_layout(True)

        self.make_slider("slider_n_examples", QtCore.Qt.Orientation.Horizontal, (1, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 20,
                         (self.x_chapter_usual, 310, self.w_chapter_slider, 50), self.change_n_examples, "label_n_examples",
                         "Number of examples: 2000", (self.x_chapter_usual + 20, 310 - 25, self.w_chapter_slider, 50))

        self.combobox_input_distrib = ["Normal", "Uniform"]
        self.make_combobox(2, self.combobox_input_distrib, (self.x_chapter_usual, 360, self.w_chapter_slider, 50),
                           self.change_input_distrib, "label_input_distrib", "Input distribution",
                           (self.x_chapter_usual + 30, 360-20, self.w_chapter_slider, 50))

        self.combobox_weight_inits = ["Small random", "Xavier", "Kaiming"]
        self.make_combobox(3, self.combobox_weight_inits, (self.x_chapter_usual, 420, self.w_chapter_slider, 50),
                           self.change_weight_init, "label_weight_init", "Weights init",
                           (self.x_chapter_usual + 30, 420-20, self.w_chapter_slider, 50))

        self.combobox_act_functions = ["tansig", "poslin"]
        self.make_combobox(3, self.combobox_act_functions, (self.x_chapter_usual, 480, self.w_chapter_slider, 50),
                           self.change_act_function, "label_act_function", "Activation function",
                           (self.x_chapter_usual + 30, 480-20, self.w_chapter_slider, 50))

        self.batch_norm = True
        self.make_checkbox('checkbox_batch_norm', 'Use Batch Norm', (self.x_chapter_usual + 15, 520, self.w_chapter_slider - 20, 50),
                           self.select_bn, True)

        self.make_button('button_random_seed', "Random", (self.x_chapter_usual + 40, 580, 100, 55), self.change_random_seed)

        self.n_examples = int(self.slider_n_examples.value() * 100)
        self.weight_init = self.combobox_weight_inits[0]
        self.input_distrib = self.combobox_input_distrib[0]
        self.act = self.combobox_act_functions[0]

        self.graph()

    def select_bn(self):
        if self.checkbox_batch_norm.checkState().value == 2 and not self.batch_norm:
            self.batch_norm = True
            self.graph()
        if self.checkbox_batch_norm.checkState().value == 0 and self.batch_norm:
            self.batch_norm = False
            self.graph()

    def graph(self):
        r = 6  # Input dimension
        layer_size = 4
        # print(
        #     'deephist(r, q, initial, input_distrib, act_func_key, layer_size, self.batch_norm)',
        #     r, self.n_examples, self.weight_init, self.input_distrib, self.act, layer_size, self.batch_norm
        # )
        a = deephist(r, self.n_examples, self.weight_init, self.input_distrib, self.act, layer_size, self.batch_norm)

        self.draw_hist(self.figureInput, a, 0, self.canvasInput, True)
        self.draw_hist(self.figureOutput1, a, 1, self.canvasOutput1)
        self.draw_hist(self.figureOutput2, a, 2, self.canvasOutput2)
        self.draw_hist(self.figureOutput3, a, 3, self.canvasOutput3)
        self.draw_hist(self.figureOutput4, a, 4, self.canvasOutput4)

    def draw_hist(self, figure, a, layer, canvas, is_input=False):
        figure.clf()
        sub_plot = figure.add_subplot(111)

        sub_plot.hist(a[layer].ravel(), bins=25)

        if is_input:
            xlim = [-10, 10]
        else:
            xlim = [-1, 1]

        # sub_plot.set_xlim(xlim)
        sub_plot.set_title(
            'Input layer' if is_input else f'Output layer{layer}'
        )
        canvas.draw()

    def change_n_examples(self):
        self.n_examples = int(self.slider_n_examples.value() * 100)
        self.label_n_examples.setText("Number of examples: {}".format(self.n_examples))
        self.graph()

    def change_weight_init(self, idx):
        self.weight_init = self.combobox_weight_inits[idx]
        self.graph()

    def change_act_function(self, idx):
        self.act = self.combobox_act_functions[idx]
        self.graph()

    def change_input_distrib(self, idx):
        self.input_distrib = self.combobox_input_distrib[idx]
        self.graph()

    def change_random_seed(self):
        self.graph()

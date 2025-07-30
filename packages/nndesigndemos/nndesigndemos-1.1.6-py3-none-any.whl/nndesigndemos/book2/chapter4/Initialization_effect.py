from PyQt6 import QtWidgets, QtCore
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.book2.chapter4.deephist import deephist


class InitEffect(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(InitEffect, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Normalization & Initialization Effects", 4,
                          "\nChoose a initialization\nscheme and whether to\nuse BatchNorm or not."
                          "\n\nThe distribution of input,\nnet input and output\nis shown on the left.\n\n",
                          PACKAGE_PATH + "Chapters/4_D/Logo_Ch_4.svg", None, 2,
                          icon_move_left=120, description_coords=(535, 105, 450, 250))

        self.make_plot(1, (10, 180, 500, 500))
        self.figure.set_tight_layout(True)

        self.batch_norm = True
        self.make_checkbox('checkbox_batch_norm', 'Use Batch Norm', (310, 150, self.w_chapter_slider - 20, 50),
                           self.select_bn, True)

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

        self.max_layers = 100
        self.n_layers = 1
        self.make_slider("slider_n_layers", QtCore.Qt.Orientation.Horizontal, (1, self.max_layers), QtWidgets.QSlider.TickPosition.TicksBelow, 1, self.n_layers,
                         (self.x_chapter_usual, 540, self.w_chapter_slider, 50), self.change_n_layers, "label_n_layers",
                         f"Number of layers: {self.n_layers}", (self.x_chapter_usual + 20, 540 - 25, self.w_chapter_slider, 50))

        self.make_button('button_random_seed', "Random", (self.x_chapter_usual + 40, 580, 100, 55), self.change_random_seed)

        self.n_examples = int(self.slider_n_examples.value() * 100)
        self.weight_init = self.combobox_weight_inits[0]
        self.input_distrib = self.combobox_input_distrib[0]
        self.act = self.combobox_act_functions[0]

        self.a = []

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
        # print(
        #     'deephist(r, q, initial, input_distrib, act_func_key, layer_size), self.batch_norm',
        #     r, self.n_examples, self.weight_init, self.input_distrib, self.act, self.max_layers, self.batch_norm
        # )
        self.a = deephist(r, self.n_examples, self.weight_init, self.input_distrib, self.act, self.max_layers, self.batch_norm)

        # print('len(self.a)', len(self.a))

        self.draw_graph()

    def draw_graph(self):
        self.figure.clf()  # Clear the plot
        self.sub_plot = self.figure.add_subplot(111)

        self.sub_plot.hist(self.a[self.n_layers].ravel(), bins=25)
        xlim = [-1, 1]
        self.sub_plot.set_xlim(xlim)
        self.sub_plot.set_ylim([0, self.n_examples//2])
        self.sub_plot.set_title(f'Output layer {self.n_layers}')
        self.canvas.draw()

    def change_n_examples(self):
        self.n_examples = int(self.slider_n_examples.value() * 100)
        self.label_n_examples.setText("Number of examples: {}".format(self.n_examples))
        self.graph()

    def change_n_layers(self):
        self.n_layers = self.slider_n_layers.value()
        self.label_n_layers.setText(f"Number of layers: {self.n_layers}")
        self.draw_graph()

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
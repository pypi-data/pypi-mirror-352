import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6 import QtWidgets, QtCore
from matplotlib.animation import FuncAnimation

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH

from nndesigndemos.book2.chapter4.DropoutDir.trainscg0 import trainscg0, preProcessing
from nndesigndemos.book2.chapter4.DropoutDir.testTrainSCG import plot_contour


class Dropout(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Dropout, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Dropout", 4, "Use sliders to change the\ndropout value, the number\nof neurons in the hidden\nlayer, the Noise Standard\nDeviation of the training\npoints.\n\n"
                                                "Use the checkbox to turn\noff and turn on the dropout.\n\n"
                                               "Click [Train] to train on\nthe training points.\n\n",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, 2, description_coords=(535, 40, 450, 440))

        self.make_plot(1, (100, 90, 300, 300))
        self.make_plot(2, (100, 380, 300, 300))
        self.figure2.subplots_adjust(left=0.225, right=0.975, bottom=0.175, top=0.9)

        self.train_error, self.error_train = [], None
        self.ani_1 = None

        self.axes_1 = self.figure.add_subplot(1, 1, 1)
        self.axes_1.set_title("Performance Indexes", fontdict={'fontsize': 10})
        self.train_e, = self.axes_1.plot([], [], linestyle='-', color="b", label="train error")
        self.axes_1.legend(loc='upper right', bbox_to_anchor=(1.0, 0.8))
        self.axes_1.plot(1, 100, marker="*", markersize=7)
        self.axes_1.plot(300, 100, marker="*", markersize=7)
        self.axes_1.plot(1, 1, marker="*", markersize=7)
        self.axes_1.plot(300, 1, marker="*", markersize=7)
        self.axes_1.set_yscale("log")
        self.figure.set_tight_layout(True)
        self.canvas.draw()

        self.do_low = 0.98
        self.S_row = 500
        self.stdv = 0.5

        self.no_dropout_checked = False
        self.do_low_old = None
        self.make_checkbox('checkbox_dropout', 'No Dropout', (self.x_chapter_usual + 10, 340, self.w_chapter_slider - 20, 50),
                           self.select_no_dropout, False)

        self.make_slider("slider_do_low", QtCore.Qt.Orientation.Horizontal, (90, 100), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 98,
                         (self.x_chapter_usual, 400-30, self.w_chapter_slider, 100), self.slide1,
                         "label_do_low", f"Dropout value: {self.do_low}", (self.x_chapter_usual + 10, 400-30, self.w_chapter_slider, 30))

        self.make_slider("slider_srow", QtCore.Qt.Orientation.Horizontal, (20, 80), QtWidgets.QSlider.TickPosition.TicksBelow, 2, 50,
                         (self.x_chapter_usual, 470-30, self.w_chapter_slider, 100), self.slide2,
                         "label_srow", f"Number of neurons: {self.S_row}", (self.x_chapter_usual + 10, 470-30, self.w_chapter_slider, 30))

        self.make_slider("slider_stdv", QtCore.Qt.Orientation.Horizontal, (0, 10), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 5,
                         (self.x_chapter_usual, 540-30, self.w_chapter_slider, 100), self.slide3,
                         "label_stdv", f"Noise standard deviation: {self.stdv}", (self.x_chapter_usual + 10, 540-30, self.w_chapter_slider, 30))

        self.animation_interval = 10
        self.full_batch = False

        self.run_button = QtWidgets.QPushButton("Train", self)
        self.run_button.setStyleSheet("font-size:13px")
        self.run_button.setGeometry(self.x_chapter_button * self.w_ratio, 580 * self.h_ratio, self.w_chapter_button * self.w_ratio, self.h_chapter_button * self.h_ratio)
        self.run_button.clicked.connect(self.on_run)

        self.make_button("pause_button", "Pause", (self.x_chapter_button, 610, self.w_chapter_button, self.h_chapter_button), self.on_stop)
        self.pause = True

        self.first_time_draw_plot2 = True
        self.draw_init_plot2()

    def draw_init_plot2(self):
        self.figure2.clf()
        self.net, self.Pd, self.Tl = preProcessing(self.do_low, self.S_row, self.stdv)
        self.axes_2 = self.figure2.add_subplot(1, 1, 1)
        plot_contour(None, self.Pd, self.Tl, self.figure2, self.axes_2)
        self.canvas2.draw()

    def select_no_dropout(self):
        if self.checkbox_dropout.checkState().value == 2 and not self.no_dropout_checked:
            self.no_dropout_checked = True
            self.do_low_old = self.do_low
            self.do_low = 1
            self.slider_do_low.setValue(100)
            self.slider_do_low.setDisabled(True)

        if self.checkbox_dropout.checkState().value == 0 and self.no_dropout_checked:
            self.no_dropout_checked = False
            self.do_low = self.do_low_old
            self.slider_do_low.setDisabled(False)
            self.slider_do_low.setValue(int(self.do_low * 100))

    def ani_stop(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.stop()

    def ani_start(self):
        if self.ani_1 and self.ani_1.event_source:
            self.ani_1.event_source.start()

    def on_stop(self):
        if self.pause:
            self.ani_stop()
            self.pause_button.setText("Unpause")
            self.pause = False
        else:
            self.ani_start()
            self.pause_button.setText("Pause")
            self.pause = True

    def on_animate_1(self, allYieldData):
        if len(allYieldData) == 1:
            self.error_train = allYieldData[0]
            self.train_error.append(self.error_train)
            epoch = len(self.train_error)
            self.train_e.set_data(list(range(epoch)), self.train_error)
        else:
            net1, Pd, Tl = allYieldData[0], allYieldData[1], allYieldData[2]
            plot_contour(net1, Pd, Tl, self.figure2, self.axes_2)
            self.canvas2.draw()

        return self.train_e,

    def on_run(self):
        self.pause_button.setText("Pause")
        self.pause = True
        self.ani_stop()
        self.train_error = []
        self.train_e.set_data([], [])
        self.canvas.draw()

        if self.first_time_draw_plot2:
            self.first_time_draw_plot2 = False
        else:
            self.draw_init_plot2()
        # print('on_run self.do_low, self.S_row, self.stdv', self.do_low, self.S_row, self.stdv)

        self.ani_1 = FuncAnimation(self.figure, self.on_animate_1, frames=trainscg0(self.net, self.Pd, self.Tl),
                                   interval=self.animation_interval, repeat=False, blit=True)

    def slide_base(self, label, content):
        label.setText(content)
        self.ani_stop()
        self.train_error = []
        self.canvas.draw()
        self.canvas2.draw()
        # print('self.do_low, self.S_row, self.stdv', self.do_low, self.S_row, self.stdv)

    def slide1(self):
        self.do_low = self.slider_do_low.value() / 100
        self.slide_base(self.label_do_low, f"Dropout value: {self.do_low}")

    def slide2(self):
        self.S_row = self.slider_srow.value() * 10
        self.slide_base(self.label_srow, f"Number of neurons: {self.S_row}")

    def slide3(self):
        self.stdv = self.slider_stdv.value() / 10
        self.slide_base(self.label_stdv, f"Noise standard deviation: {self.stdv}")

        self.first_time_draw_plot2 = True
        self.draw_init_plot2()

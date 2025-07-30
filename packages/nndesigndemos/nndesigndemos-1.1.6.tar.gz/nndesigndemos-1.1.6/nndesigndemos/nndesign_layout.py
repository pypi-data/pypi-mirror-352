import os
from PyQt6 import QtWidgets, QtGui, QtCore, QtMultimedia
from PyQt6.QtWidgets import QMainWindow, QApplication
# import warnings
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math

from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.nndesign_settings import OS_NAME


# -------------------------------------------------------------------------------------------------------------
# Original Size

WM_MAC_MAIN, HM_MAC_MAIN = 1280 - 750, 800 - 120  # For my Mac
WM_MAC_CHAPTER, HM_MAC_CHAPTER = 1280 - 580, 800 - 120  # For my Mac - original size

xlabel, ylabel, wlabel, hlabel, add = 30, 5, 500, 100, 20

x_info, y_info, w_info, h_info = 535, 100, 450, 250

wp_pic2_1, hp_pic2_1, x_pic2_1, y_pic2_1 = 120, 100, 560, 30
w_pic2_1, h_pic2_1 = wp_pic2_1, hp_pic2_1
wp_pic2_2, hp_pic2_2, x_pic2_2, y_pic2_2 = 500, 200, 130, 100
w_pic2_2, h_pic2_2 = 500, 200

# Lines
# Starting line point for my Mac. The ending point is determined by the w, h and ratio of screen compared to mine
xl1, yl1 = 10, 90
xl2 = 520
xl3, xl4 = 560, 700
yl4 = 670
x_chapter = 560
# -------------------------------------------------------------------------------------------------------------


class NNDLayout(QMainWindow):
    def __init__(self, w_ratio, h_ratio, dpi, chapter_window=True, main_menu=False, draw_vertical=True,
                 draw_horizontal=True, print_mouse_coords=False, fixed_size=False, do_not_scale=False,
                 overwrite_size=None):

        super(NNDLayout, self).__init__()

        self.running_on_windows = OS_NAME == "Windows"
        self.running_on_linux = OS_NAME == "Linux"

        self.print_mouse_coords = print_mouse_coords
        self.setMouseTracking(print_mouse_coords)

        self.dpi = dpi
        self.play_sound = True if os.environ["NNDESIGNDEMOS_PLAY_SOUND"] == "1" else False

        if do_not_scale:
            self.w_ratio, self.h_ratio = 1, 1
        else:
            self.w_ratio, self.h_ratio = w_ratio, h_ratio
        if chapter_window:
            self.wm, self.hm = WM_MAC_CHAPTER * w_ratio, HM_MAC_CHAPTER * h_ratio
        else:
            self.wm, self.hm = WM_MAC_MAIN * w_ratio, HM_MAC_MAIN * h_ratio
        if fixed_size:
            self.setFixedSize(WM_MAC_CHAPTER, HM_MAC_CHAPTER)
        else:
            self.setFixedSize(self.wm, self.hm)
        if overwrite_size is not None:
            self.setFixedSize(overwrite_size[0] * w_ratio, overwrite_size[1] * h_ratio)
        self.center()

        size_scaled = int(10 * (self.w_ratio + self.h_ratio) / 2)
        matplotlib.rcParams.update({'font.size': size_scaled, 'axes.titlesize': size_scaled, 'axes.labelsize': size_scaled,
                                    'xtick.labelsize': size_scaled, 'ytick.labelsize': size_scaled,
                                    'legend.fontsize': size_scaled, 'figure.titlesize': size_scaled})

        self.x_chapter_usual, self.w_chapter_button, self.h_chapter_button = 520, 170, 30
        self.x_chapter_button = 525
        self.x_chapter_slider_label = 590
        self.w_chapter_slider = 180

        self.label3, self.label4, self.label5, self.icon1, self.icon2 = None, None, None, None, None

        self.draw_vertical = draw_vertical
        self.draw_horizontal = draw_horizontal
        if main_menu == 1:
            self.setWindowTitle("Neural Network Design Demos")
            self.make_label("label1", "Neural Network", (xlabel, ylabel, wlabel, hlabel), font_size=18, italics=True)
            self.make_label("label2", "DESIGN", (xlabel, ylabel + add, wlabel, hlabel), font_size=18)

        if main_menu == 2:
            self.setWindowTitle("Neural Network Design: Deep Learning Demos")
            self.make_label("label1", "Neural Network", (xlabel, ylabel, wlabel, hlabel), font_size=18, italics=True)
            self.make_label("label2", "DESIGN: DEEP LEARNING", (xlabel, ylabel + add, wlabel, hlabel), font_size=18)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        qp.begin(self)
        self.draw_lines(qp)
        qp.end()

    def draw_lines(self, qp):
        if self.draw_horizontal:
            pen = QtGui.QPen(QtGui.QColor("darkblue"), 4, QtCore.Qt.PenStyle.SolidLine)
            qp.setPen(pen)
            # qp.drawLine(xl1 * self.w_ratio, yl1 * self.h_ratio, self.wm - xl1 * self.w_ratio, yl1 * self.h_ratio)
            qp.drawLine(xl1 * self.w_ratio, yl1 * self.h_ratio, xl2 * self.w_ratio, yl1 * self.h_ratio)
            qp.drawLine(xl3 * self.w_ratio, yl4 * self.h_ratio, xl4 * self.w_ratio, yl4 * self.h_ratio)

        if self.draw_vertical:
            pen = QtGui.QPen(QtGui.QColor("darkblue"), 4, QtCore.Qt.PenStyle.SolidLine)
            qp.setPen(pen)
            # qp.drawLine(self.wm - xl1 * self.w_ratio, yl1 * self.h_ratio + 35, self.wm - xl1 * self.w_ratio, 750 * self.h_ratio)
            qp.drawLine(xl2 * self.w_ratio, yl1 * self.h_ratio + 35, xl2 * self.w_ratio, yl4 * self.h_ratio)

    def fill_chapter(self, title, number, description, logo_path, icon_path=None, book_index=1, show_info=True, icon_move_left=0, icon_move_up=0,
                     description_coords=(x_info, y_info, w_info, h_info), icon_coords=(x_pic2_2, y_pic2_2, w_pic2_2, h_pic2_2),
                     icon_rescale=False):

        # Overrides logo_path in order to use the new logos and don't change the code in 70 different files...
        if book_index == 1:
            logo_path = PACKAGE_PATH + "Logo/book_logos/{}.svg".format(number)
        else:
            logo_path = PACKAGE_PATH + "Logo/book2_logos/{}.svg".format(number)

        len_ref = len("One-Input Neuron")
        len_current = len(title)
        self.make_label("label3", title, (xl2 - 135 - (len_current - len_ref) * 5.5, ylabel + add, wlabel, hlabel), font_size=18)
        self.make_label("label4", "Chapter {}".format(number), (x_chapter, 630, 150, 50), font_size=16)

        if show_info:
            # paragraphs = description.split("<p>")
            # y_pos = y_info
            self.make_label("label5", description, (description_coords[0], description_coords[1], description_coords[2], description_coords[3]))
            # for idx, paragraph in enumerate(paragraphs):
            #     self.make_label("label{}".format(idx + 5), paragraph, (x_info, y_pos, w_info, h_info))
            #     n_lines = len(paragraph.split("\n")) + 1
            #     y_pos += (n_lines * 10 + 20) * self.h_ratio

        self.icon1 = QtWidgets.QLabel(self)
        self.icon1.setPixmap(QtGui.QIcon(logo_path).pixmap(wp_pic2_1 * self.w_ratio, hp_pic2_1 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On))
        self.icon1.setGeometry(x_pic2_1 * self.w_ratio, y_pic2_1 * self.h_ratio, w_pic2_1 * self.w_ratio, h_pic2_1 * self.h_ratio)

        if icon_path:
            icon_coords = list(icon_coords)
            icon_coords[0] -= icon_move_left
            icon_coords[1] -= icon_move_up
            self.icon2 = QtWidgets.QLabel(self)
            if icon_rescale:
                pixmap = QtGui.QIcon(icon_path).pixmap(icon_coords[2] * self.w_ratio, icon_coords[3] * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
            else:
                pixmap = QtGui.QIcon(icon_path).pixmap(wp_pic2_2 * self.w_ratio, hp_pic2_2 * self.h_ratio, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
            # if icon_rescale:
            #     pixmap = pixmap.scaled(icon_coords[2] * self.w_ratio, icon_coords[3] * self.h_ratio)
            self.icon2.setPixmap(pixmap)
            self.icon2.setGeometry(icon_coords[0] * self.w_ratio, icon_coords[1] * self.h_ratio, icon_coords[2] * self.w_ratio, icon_coords[3] * self.h_ratio)
            # w_pic2_2 = 400
            # h_pic2_2 = 200
            # self.show_image("icon2", icon_path, (x_pic2_2 - icon_move_left, y_pic2_2, w_pic2_2, h_pic2_2))

    def center(self):
        qr = self.frameGeometry()
        app = QApplication.instance()

        cp = app.primaryScreen().availableGeometry().center()
        # cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mouseMoveEvent(self, event):
        if self.print_mouse_coords:
            print('Mouse coords: ( %d : %d )' % (event.x(), event.y()))

    # https://stackoverflow.com/questions/32035251/displaying-latex-in-pyqt-pyside-qtablewidget
    def mathTex_to_QPixmap(self, mathTex, fs):

        # ---- set up a mpl figure instance ----

        fig = Figure()
        fig.patch.set_facecolor('none')
        fig.set_canvas(FigureCanvas(fig))
        renderer = fig.canvas.get_renderer()

        # ---- plot the mathTex expression ----

        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.patch.set_facecolor('none')
        if self.dpi > 113.5:
            fs *= 113.5 / self.dpi  # My screen's dpi
            fs /= 2
        t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize=int(fs * (self.w_ratio + self.h_ratio) / 2))

        # ---- fit figure size to text artist ----

        fwidth, fheight = fig.get_size_inches()
        fig_bbox = fig.get_window_extent(renderer)

        text_bbox = t.get_window_extent(renderer)

        tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
        tight_fheight = text_bbox.height * fheight / fig_bbox.height

        fig.set_size_inches(tight_fwidth, tight_fheight)

        # ---- convert mpl figure to QPixmap ----

        buf, size = fig.canvas.print_to_buffer()
        qimage = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, size[0], size[1],
                                                      QtGui.QImage.Format_ARGB32))
        qpixmap = QtGui.QPixmap(qimage)

        return qpixmap

    def paint_latex_string(self, latex_label_attr_name, latex_sting, font_size, latex_coords):
        if self.running_on_windows:
            font_size *= 2
        elif self.running_on_linux:
            font_size *= 2
        latex_paint = self.mathTex_to_QPixmap(latex_sting, font_size)
        setattr(self, latex_label_attr_name, QtWidgets.QLabel(self))
        latex_label = getattr(self, latex_label_attr_name)
        latex_label.setPixmap(latex_paint)
        latex_label.setGeometry(latex_coords[0] * self.w_ratio, latex_coords[1] * self.h_ratio,
                                latex_coords[2] * self.w_ratio, latex_coords[3] * self.h_ratio)

    def paint_bracket(self, painter, x, y_1, y_2, w, add_small=16):
        painter.drawLine(x * self.w_ratio, y_1 * self.h_ratio, x * self.w_ratio, y_2 * self.h_ratio)
        painter.drawLine(x * self.w_ratio, y_1 * self.h_ratio, (x + add_small) * self.w_ratio, y_1 * self.h_ratio)
        painter.drawLine(x * self.w_ratio, y_2 * self.h_ratio, (x + add_small) * self.w_ratio, y_2 * self.h_ratio)
        painter.drawLine((x + w) * self.w_ratio, y_1 * self.h_ratio, (x + w) * self.w_ratio, y_2 * self.h_ratio)
        painter.drawLine((x + w - add_small) * self.w_ratio, y_1 * self.h_ratio, (x + w) * self.w_ratio, y_1 * self.h_ratio)
        painter.drawLine((x + w - add_small) * self.w_ratio, y_2 * self.h_ratio, (x + w) * self.w_ratio, y_2 * self.h_ratio)

    def show_image(self, image_attr_name, image_path, image_coords):
        setattr(self, image_attr_name, QtWidgets.QLabel(self))
        img = getattr(self, image_attr_name)
        img.setPixmap(QtGui.QPixmap(image_path).scaled(image_coords[2] * self.w_ratio, image_coords[3] * self.h_ratio))
        img.setGeometry(image_coords[0] * self.w_ratio, image_coords[1] * self.h_ratio,
                        image_coords[2] * self.w_ratio, image_coords[3] * self.h_ratio)

    def set_layout(self, layout_coords, widget):
        wid = QtWidgets.QWidget(self)
        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        wid.setGeometry(layout_coords[0] * self.w_ratio, layout_coords[1] * self.h_ratio,
                        layout_coords[2] * self.w_ratio, layout_coords[3] * self.h_ratio)
        layout.addWidget(widget)
        wid.setLayout(layout)

    def make_label(self, label_attr_name, label_str, label_coords, font_name="Times New Roman", font_size=14, italics=False):
        setattr(self, label_attr_name, QtWidgets.QLabel(self))
        label = getattr(self, label_attr_name)
        label.setText(label_str)
        if self.running_on_windows:
            label.setFont(QtGui.QFont(font_name, int(font_size * 0.78 * (self.w_ratio + self.h_ratio) / 2), italic=italics))
        elif self.running_on_linux:
            label.setFont(QtGui.QFont(font_name, int(font_size * 0.78 * (self.w_ratio + self.h_ratio) / 2), italic=italics))
        else:
            label.setFont(QtGui.QFont(font_name, int(font_size * (self.w_ratio + self.h_ratio) / 2), italic=italics))
        label.setGeometry(round(label_coords[0] * self.w_ratio), label_coords[1] * self.h_ratio,
                          label_coords[2] * self.w_ratio, label_coords[3] * self.h_ratio)

    def make_plot(self, plot_number, plot_coords=(90, 300, 370, 370)):
        if plot_number == 1:  # This  is to avoid breaking all the code where
            plot_number = ""  # I call the first plot figure instead of figure1
        setattr(self, "figure" + str(plot_number), Figure())
        # getattr(self, "figure" + str(plot_number)).set_tight_layout(True)
        # setattr(self, "figure" + str(plot_number), Figure(figsize=(4, 6)))
        setattr(self, "canvas" + str(plot_number), FigureCanvas(getattr(self, "figure" + str(plot_number))))
        # getattr(self, "canvas" + str(plot_number)).resize(plot_coords[2] * 0.8, plot_coords[3] * 0.8)
        # getattr(self, "canvas" + str(plot_number)).setParent(self)
        # setattr(self, "toolbar" + str(plot_number), NavigationToolbar(getattr(self, "canvas" + str(plot_number)), self))
        self.set_layout(plot_coords, getattr(self, "canvas" + str(plot_number)))
        # self.set_layout(plot_coords, getattr(self, "toolbar" + str(plot_number)))

    # def make_plot_v2(self, plot_number, plot_coords=(90, 300, 370, 370)):
    #     if plot_number == 1:  # This  is to avoid breaking all the code where
    #         plot_number = ""  # I call the first plot figure instead of figure1
    #     setattr(self, "canvas" + str(plot_number), Canvas(self, plot_coords[2], plot_coords[3]))
    #     setattr(self, "axes_1", getattr(self, "canvas" + str(plot_number)).axes)
    #     # setattr(self, "figure" + str(plot_number), getattr(self, "canvas" + str(plot_number)).fig)
    #     # self.set_layout(plot_coords, getattr(self, "canvas" + str(plot_number)))

    def make_combobox(self, combobox_number, combobox_items, combobox_coords, f_connect=None, label_attr_name=None, label_str="?",
                      label_coords=None, label_font_name="Times New Roman", label_font_size=14, label_italics=False):
        setattr(self, "comboBox" + str(combobox_number), QtWidgets.QComboBox(self))
        combobox = getattr(self, "comboBox" + str(combobox_number))
        # combobox.setSizeAdjustPolicy(0)
        combobox.setGeometry(combobox_coords[0] * self.w_ratio, combobox_coords[1] * self.h_ratio,
                             combobox_coords[2] * self.w_ratio, combobox_coords[3] * self.h_ratio)
        # combobox.setFixedSize((combobox_coords[2] - 10) * self.w_ratio, (combobox_coords[3] + 50) * self.h_ratio)
        # I'm able to adjust the font of the combobox in the right way, but I'm not able to increase the height of the combobox,
        # so I'm just going to increase the font when it's clicked instead
        # font = QtGui.QFont()
        # font.setPointSize(int(13 * (self.w_ratio + self.h_ratio) / 2))
        # combobox.setFont(font)
        # combobox.DropDownHeight = combobox_coords[3] * self.h_ratio
        # combobox.setStyleSheet("QListView::item {height:" + str(int(combobox_coords[3] * self.h_ratio)) + "px;}")
        combobox.addItems(combobox_items)
        # combobox.setStyleSheet("QLineEdit::item {font-size:" + str(int(18 * (self.w_ratio + self.h_ratio) / 2)) + "px;}")
        # combobox.setView(QtWidgets.QListView())
        if label_attr_name:
            if not label_coords:
                label_coords = (combobox_coords[0] + 80, combobox_coords[1] - 20, combobox_coords[2], combobox_coords[3])
            self.make_label(label_attr_name, label_str, label_coords, label_font_name, label_font_size, label_italics)
        # if combobox_coords[-1] > 50 * self.h_ratio:
        #     warnings.warn("Setting combobox with too high height ({}).".format(combobox_coords[-1] * self.h_ratio)
        #                   + " This may result in interactive problems")
        self.set_layout(combobox_coords, combobox)
        if f_connect:
            combobox.currentIndexChanged.connect(f_connect)

    def make_slider(self, slider_attr_name, slider_type, slider_range, slider_tick_pos, slider_tick_interval,
                    slider_value, slider_coords, f_connect=None, label_attr_name=None, label_str="?", label_coords=None,
                    label_font_name="Times New Roman", label_font_size=14, label_italics=False):  # , update_only_when_mouse_released=False):
        setattr(self, slider_attr_name, QtWidgets.QSlider(slider_type))
        slider = getattr(self, slider_attr_name)
        slider.setRange(slider_range[0], slider_range[1])
        slider.setTickPosition(slider_tick_pos)
        slider.setTickInterval(slider_tick_interval)
        slider.setValue(slider_value)
        if label_attr_name:
            if not label_coords:
                label_coords = (slider_coords[0] + 80, slider_coords[1] - 30, slider_coords[2], slider_coords[3])
            self.make_label(label_attr_name, label_str, label_coords, label_font_name, label_font_size, label_italics)
        # if slider_coords[-1] > 50 * self.h_ratio and slider_type == QtCore.Qt.Orientation.Horizontal:
        #     warnings.warn("Setting horizontal slider {} with too much height ({}).".format(
        #         slider_attr_name, slider_coords[-1] * self.h_ratio
        #     ) + " This may result in interactive problems")
        self.set_layout(slider_coords, slider)
        if f_connect:
            slider.valueChanged.connect(f_connect)
        # if update_only_when_mouse_released:
        #     self.f_connect = f_connect
        #     self.slider_temp = slider
        #     self.slider_temp.sliderPressed.connect(self.slider_disconnect)
        #     self.slider_temp.sliderReleased.connect(self.slider_reconnect)

    # def slider_disconnect(self):
    #     self.slider_temp.valueChanged.disconnect()

    # def slider_reconnect(self):
    #     self.slider_temp.valueChanged.connect(self.f_connect)
    #     self.slider_temp.valueChanged.emit(self.slider_temp.value())

    def make_button(self, button_attr_name, button_str, button_coords, f_connect, style_sheet="font-size:13px"):
        setattr(self, button_attr_name, QtWidgets.QPushButton(button_str, self))
        button = getattr(self, button_attr_name)
        button.setStyleSheet(style_sheet.replace("13", str(int(13 * (self.w_ratio + self.h_ratio) / 2))))
        button.setGeometry(button_coords[0] * self.w_ratio, button_coords[1] * self.h_ratio,
                           button_coords[2] * self.w_ratio, button_coords[3] * self.h_ratio)
        button.clicked.connect(f_connect)

    def make_checkbox(self, checkbox_attr_name, checkbox_str, checkbox_coords, f_connect, checked):
        setattr(self, checkbox_attr_name, QtWidgets.QCheckBox(checkbox_str))
        checkbox = getattr(self, checkbox_attr_name)
        checkbox.setGeometry(checkbox_coords[0] * self.w_ratio, checkbox_coords[1] * self.h_ratio,
                             checkbox_coords[2] * self.w_ratio, checkbox_coords[3] * self.h_ratio)
        if self.running_on_windows:
            checkbox.setStyleSheet("font-size: {}px".format(int(12 * 0.9)))
        elif self.running_on_linux:
            checkbox.setStyleSheet("font-size: {}px".format(int(12 * 0.9)))
        else:
            checkbox.setStyleSheet("font-size: {}px".format(int(12 * (self.w_ratio + self.h_ratio) / 2)))
        checkbox.stateChanged.connect(f_connect)
        self.set_layout(checkbox_coords, checkbox)
        checkbox.setChecked(1 if checked else 0)

    def make_input_box(self, input_box_attr_name, input_box_text, input_box_coords, func_text_changed=None):
        setattr(self, input_box_attr_name, QtWidgets.QLineEdit())
        input_box = getattr(self, input_box_attr_name)
        input_box.setText(input_box_text)
        if func_text_changed is not None:
            input_box.textChanged[str].connect(func_text_changed)
        # font = input_box.font()
        # font.setPointSize(int(20 * (self.w_ratio + self.h_ratio) / 2))
        # input_box.setFont(font)
        if self.running_on_windows:
            input_box.setStyleSheet("font: {}px".format(int(12 * 0.9)))
        elif self.running_on_linux:
            input_box.setStyleSheet("font: {}px".format(int(12 * 0.9)))
        else:
            input_box.setStyleSheet("font: {}px".format(int(12 * (self.w_ratio + self.h_ratio) / 2)))
        input_box.setGeometry(input_box_coords[0] * self.w_ratio, input_box_coords[1] * self.h_ratio,
                              input_box_coords[2] * self.w_ratio, input_box_coords[3] * self.h_ratio)
        # self.set_layout((input_box_coords[0] * 1.01, input_box_coords[1], input_box_coords[2] * 0.9, input_box_coords[3]), input_box)
        self.set_layout(input_box_coords, input_box)

    def get_slider_value_and_update(self, slider, slider_label, value_multiplier=1, round_pos=0):
        value = slider.value() * value_multiplier
        slider_label.setText(slider_label.text()[:slider_label.text().find(":") + 2] + str(round(value, round_pos)))
        return value

    def closeEvent(self, event):
        super().closeEvent(event)
        for attr in dir(self):
            # Stops all running matplotlib animations
            if type(getattr(self, attr)) == matplotlib.animation.FuncAnimation:
                if getattr(self, attr).event_source:
                    getattr(self, attr).event_source.stop()
            # Stops all running PyQt6 timers
            elif type(getattr(self, attr)) == QtCore.QTimer:
                getattr(self, attr).stop()

    @staticmethod
    def logsigmoid(n):
        return 1 / (1 + np.exp(-n))

    @staticmethod
    def logsigmoid_stable(n):
        n = np.clip(n, -100, 100)
        return 1 / (1 + np.exp(-n))

    @staticmethod
    def logsigmoid_der(n):
        return (1 - 1 / (1 + np.exp(-n))) * 1 / (1 + np.exp(-n))

    @staticmethod
    def purelin(n):
        return n

    @staticmethod
    def purelin_der(n):
        return np.array([1]).reshape(n.shape)

    @staticmethod
    def lin_delta(a, d=None, w=None):
        na, ma = a.shape
        if d is None and w is None:
            return -np.kron(np.ones((1, ma)), np.eye(na))
        else:
            return np.dot(w.T, d)

    @staticmethod
    def log_delta(a, d=None, w=None):
        s1, _ = a.shape
        if d is None and w is None:
            return -np.kron((1 - a) * a, np.ones((1, s1))) * np.kron(np.ones((1, s1)), np.eye(s1))
        else:
            return (1 - a) * a * np.dot(w.T, d)

    @staticmethod
    def tan_delta(a, d=None, w=None):
        s1, _ = a.shape
        if d is None and w is None:
            return -np.kron(1 - a * a, np.ones((1, s1))) * np.kron(np.ones((1, s1)), np.eye(s1))
        else:
            return (1 - a * a) * np.dot(w.T, d)

    @staticmethod
    def marq(p, d):
        s, _ = d.shape
        r, _ = p.shape
        return np.kron(p.T, np.ones((1, s))) * np.kron(np.ones((1, r)), d.T)

    @staticmethod
    def compet(n, axis=None):
        if axis is not None:
            max_idx = np.argmax(n, axis=axis)
            out = np.zeros(n.shape)
            for i in range(out.shape[1]):
                out[max_idx[i], i] = 1
            return out
        else:
            max_idx = np.argmax(n)
            out = np.zeros(n.shape)
            out[max_idx] = 1
            return out

    @staticmethod
    def poslin(n):
        return n * (n > 0)

    @staticmethod
    def hardlim(x):
        if x < 0:
            return 0
        else:
            return 1

    @staticmethod
    def hardlims(x):
        if x < 0:
            return -1
        else:
            return 1

    @staticmethod
    def satlin(x):
        if x < 0:
            return 0
        elif x < 1:
            return x
        else:
            return 1

    @staticmethod
    def satlins(x):
        if x < -1:
            return 0
        elif x < 1:
            return x
        else:
            return 1

    @staticmethod
    def logsig(x):
        return 1 / (1 + math.e ** (-x))

    @staticmethod
    def tansig(x):
        return 2 / (1 + math.e ** (-2 * x)) - 1

    def nndtansig(self, x):
        a = self.tansig(x)

    def initial_sound(self, sound_name, left_path):
        setattr(self, sound_name, QtMultimedia.QSoundEffect())
        getattr(self, sound_name).setSource(QtCore.QUrl.fromLocalFile(PACKAGE_PATH + left_path))


def open_link(link_str):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(link_str))

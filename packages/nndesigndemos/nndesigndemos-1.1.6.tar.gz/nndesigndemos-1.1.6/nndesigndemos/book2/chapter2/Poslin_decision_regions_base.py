from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class PoslinDecisionRegionsBase(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi, post_title):
        super(PoslinDecisionRegionsBase, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter(f"Poslin Decision Regions {post_title}", 2, "\nAlter the network's\n"
                                                        "parameters by entering\nvalues in the input fields.\n\n"
                                                        "Click [Update] to apply\nyour changes.\n\n"
                                                        "Click [Set Default] to\nrestore original values.\n\n"
                                                        "Choose the output transfer\nfunction f below.",
                          PACKAGE_PATH + "Chapters/2_D/Logo_Ch_2.svg", PACKAGE_PATH + "Figures/poslinNet2Ddemo.svg", 2,
                          icon_move_left=120, icon_move_up=30, description_coords=(535, 130, 450, 220))

        # self.make_plot(1, (10, 240, 250, 250))
        # self.make_plot(2, (260, 240, 250, 250))

        # Define default values for network parameters
        self.default_w1 = [["1", "1"], ["-1", "-1"], ["-1", "1"], ["1", "-1"]]
        self.default_w2 = [["-1"], ["-1"], ["-1"], ["-1"]]
        self.default_b1 = [["-1"], ["3"], ["1"], ["1"]]
        self.default_b2 = ["5"]

        input_width = 60
        input_height = 50
        w1_y_interval = 30
        w1_x_0 = 35
        w1_x_1 = w1_x_0 + 50
        w1_y_0 = 525
        w1_y_1 = w1_y_0 + w1_y_interval
        w1_y_2 = w1_y_1 + w1_y_interval
        w1_y_3 = w1_y_2 + w1_y_interval

        label_y = 497
        # W1 matrix label and input fields
        self.make_label("label_w1", "W1", (69, label_y, 100, 30), font_size=25)
        self.make_input_box("w1_00", self.default_w1[0][0], (w1_x_0, w1_y_0, input_width, input_height))
        self.make_input_box("w1_01", self.default_w1[0][1], (w1_x_1, w1_y_0, input_width, input_height))
        self.make_input_box("w1_10", self.default_w1[1][0], (w1_x_0, w1_y_1, input_width, input_height))
        self.make_input_box("w1_11", self.default_w1[1][1], (w1_x_1, w1_y_1, input_width, input_height))
        self.make_input_box("w1_20", self.default_w1[2][0], (w1_x_0, w1_y_2, input_width, input_height))
        self.make_input_box("w1_21", self.default_w1[2][1], (w1_x_1, w1_y_2, input_width, input_height))
        self.make_input_box("w1_30", self.default_w1[3][0], (w1_x_0, w1_y_3, input_width, input_height))
        self.make_input_box("w1_31", self.default_w1[3][1], (w1_x_1, w1_y_3, input_width, input_height))

        variable_interval = 110
        w2_x_0 = w1_x_1 + variable_interval
        # W2 matrix label and input fields
        self.make_label("label_w2", "W2", (w2_x_0+10, label_y, 100, 30), font_size=25)
        self.make_input_box("w2_00", self.default_w2[0][0], (w2_x_0, w1_y_0, input_width, input_height))
        self.make_input_box("w2_10", self.default_w2[1][0], (w2_x_0, w1_y_1, input_width, input_height))
        self.make_input_box("w2_20", self.default_w2[2][0], (w2_x_0, w1_y_2, input_width, input_height))
        self.make_input_box("w2_30", self.default_w2[3][0], (w2_x_0, w1_y_3, input_width, input_height))

        b1_x_0 = w2_x_0 + variable_interval
        # b1 matrix label and input fields
        self.make_label("label_b1", "b1", (b1_x_0+15, label_y, 100, 30), font_size=25)
        self.make_input_box("b1_00", self.default_b1[0][0], (b1_x_0, w1_y_0, input_width, input_height))
        self.make_input_box("b1_10", self.default_b1[1][0], (b1_x_0, w1_y_1, input_width, input_height))
        self.make_input_box("b1_20", self.default_b1[2][0], (b1_x_0, w1_y_2, input_width, input_height))
        self.make_input_box("b1_30", self.default_b1[3][0], (b1_x_0, w1_y_3, input_width, input_height))

        b2_x_0 = b1_x_0 + variable_interval
        # b2 matrix label and input fields
        self.make_label("label_b2", "b2", (b2_x_0+15, label_y, 100, 30), font_size=25)
        self.make_input_box("b2_00", self.default_b2[0], (b2_x_0, w1_y_0, input_width, input_height))
        
        # Update button
        self.make_button("update_button", "Update", (self.x_chapter_button, 430, self.w_chapter_button, self.h_chapter_button), self.update_values)
        
        # Set Default button - add to the right of the Update button
        self.make_button("default_button", "Set Default", 
                        (self.x_chapter_button, 480, self.w_chapter_button, self.h_chapter_button), 
                        self.set_default_values)

        self.combobox_funcs = [self.poslin, self.hardlim, self.hardlims, self.purelin, self.satlin, self.satlins, self.logsig, self.tansig]
        self.combobox_funcs_str = ["poslin", "hardlim", "hardlims", "purelin", "satlin", "satlins", "logsig", "tansig"]
        self.make_combobox(1, self.combobox_funcs_str, (self.x_chapter_usual, 370, self.w_chapter_slider, 50), self.change_transfer_f, "label_f", "f")
        self.func1 = self.poslin

    def set_default_values(self):
        """Reset all input fields to their default values and update the graph"""
        # Reset W1 values
        self.w1_00.setText(self.default_w1[0][0])
        self.w1_01.setText(self.default_w1[0][1])
        self.w1_10.setText(self.default_w1[1][0])
        self.w1_11.setText(self.default_w1[1][1])
        self.w1_20.setText(self.default_w1[2][0])
        self.w1_21.setText(self.default_w1[2][1])
        self.w1_30.setText(self.default_w1[3][0])
        self.w1_31.setText(self.default_w1[3][1])
        
        # Reset W2 values
        self.w2_00.setText(self.default_w2[0][0])
        self.w2_10.setText(self.default_w2[1][0])
        self.w2_20.setText(self.default_w2[2][0])
        self.w2_30.setText(self.default_w2[3][0])
        
        # Reset b1 values
        self.b1_00.setText(self.default_b1[0][0])
        self.b1_10.setText(self.default_b1[1][0])
        self.b1_20.setText(self.default_b1[2][0])
        self.b1_30.setText(self.default_b1[3][0])
        
        # Reset b2 value
        self.b2_00.setText(self.default_b2[0])
        
        self.update_values()

    def paintEvent(self, event):
        super(PoslinDecisionRegionsBase, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtGui.QColor("black"), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        y1 = 533
        y2 = 655

        width_small_bracket = 60
        
        # Draw brackets for W1 (4x2 matrix)
        self.paint_bracket(painter, 40, y1, y2, 100)
        
        # Draw brackets for W2 (4x1 matrix)
        self.paint_bracket(painter, 195, y1, y2, width_small_bracket)
        
        # Draw brackets for b1 (4x1 matrix)
        self.paint_bracket(painter, 305, y1, y2, width_small_bracket)
        
        # Draw brackets for b2 (1x1 value)
        self.paint_bracket(painter, 415, y1, y2, width_small_bracket)
        
        painter.end()

    def change_transfer_f(self, idx):
        self.func1 = self.combobox_funcs[idx]
        self.graph()

    def update_values(self):
        try:
            self.w1 = np.array([
                [float(self.w1_00.text()), float(self.w1_01.text())],
                [float(self.w1_10.text()), float(self.w1_11.text())],
                [float(self.w1_20.text()), float(self.w1_21.text())],
                [float(self.w1_30.text()), float(self.w1_31.text())]
            ])
            
            # Read values from input fields for W2
            self.w2 = np.array([
                [float(self.w2_00.text())],
                [float(self.w2_10.text())],
                [float(self.w2_20.text())],
                [float(self.w2_30.text())]
            ])
            
            # Read values from input fields for b1
            self.b1 = np.array([
                [float(self.b1_00.text())],
                [float(self.b1_10.text())],
                [float(self.b1_20.text())],
                [float(self.b1_30.text())]
            ])
            
            # Read values from input fields for b2
            self.b2 = np.array([float(self.b2_00.text())])
            # Update the graph with new parameters
            self.graph()
        except ValueError:
            # Show error if parsing fails
            QtWidgets.QMessageBox.critical(self, "Input Error", 
                "Please enter valid numeric values for all parameters.")

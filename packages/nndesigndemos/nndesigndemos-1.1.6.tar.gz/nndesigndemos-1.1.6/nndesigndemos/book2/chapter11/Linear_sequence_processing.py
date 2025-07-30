from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
import numpy as np
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from nndesigndemos.book2.chapter11.utils import averaging_network


class LinearSequenceProcessing(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(LinearSequenceProcessing, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        print(PACKAGE_PATH + "Figures/linear_sequence_processing.svg")

        self.fill_chapter(f"Linear Sequence Processing", 11, "\nAlter the network's\n"
                                                        "parameters by entering\nvalues in the input fields.\n\n"
                                                        "Click [Update] to apply\nyour changes.\n\n"
                                                        "Click [Set Default] to\nrestore original values.",
                          PACKAGE_PATH + "Logo/Logo_Ch_11.svg", None, 2,
                          icon_move_left=120, icon_move_up=30, description_coords=(535, 130, 450, 220))

        self.make_plot(1, (10, 400, 250, 250))
        self.make_plot(2, (260, 400, 250, 250))

        self.p_str = ['0', '1', '2', '3', '2', '1', '0', '0', '0']
        self.iw_str = ['0', '0.5', '0.5']

        self.p = np.array(self.p_str, dtype=int)
        self.iw = np.array(self.iw_str, dtype=float)

        self.n = len(self.p_str)

        self.initialize_table()
        
        # Update button
        self.make_button("update_button", "Update", (self.x_chapter_button, 430, self.w_chapter_button, self.h_chapter_button), self.update_values)
        
        # Set Default button
        self.make_button("default_button", "Set Default", 
                        (self.x_chapter_button, 480, self.w_chapter_button, self.h_chapter_button), 
                        self.set_default_values)

        self.set_default_values()
    

    def initialize_table(self):
        """Create and setup the sequence table"""
        self.table = QTableWidget(3, self.n, self)
        self.table.setGeometry(20, 130, 480, 250)
        
        self.table.setVerticalHeaderLabels(['p(t)', 'a(t)', 'TDL'])
        
        self.table.setCornerButtonEnabled(False)
        
        # Make table look nice
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Set font size
        font = self.table.font()
        font.setPointSize(12)
        self.table.setFont(font)

        self.table.show()

    def update_table(self):
        """Update table with current sequence data"""
        for i in range(self.n):
            item_p = QTableWidgetItem(str(self.p[i]))
            item_p.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
            self.table.setItem(0, i, item_p)
            
            item_a = QTableWidgetItem(str(self.a[i]))
            item_a.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
            item_a.setFlags(item_a.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)  # Make read-only
            item_a.setBackground(QtGui.QColor(240, 240, 240))  # Light gray background
            self.table.setItem(1, i, item_a)
        
            tdl_text = "\n\n".join([str(int(val)) for val in self.tdl_history[i]])
            item_tdl = QTableWidgetItem(tdl_text)
            item_tdl.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
            item_tdl.setFlags(item_tdl.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)  # Make read-only
            item_tdl.setBackground(QtGui.QColor(240, 240, 240))  # Light gray background
            self.table.setItem(2, i, item_tdl)

    def set_default_values(self):
        # Reset P values
        for i in range(self.n):
            item_p = QTableWidgetItem(self.p_str[i])
            item_p.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center text horizontally
            self.table.setItem(0, i, item_p)
        
        self.update_values()

    def update_values(self):
        try:
            for i in range(self.n):
                self.p[i] = int(self.table.item(0, i).text())
                        
            net = averaging_network(self.iw)
            self.a, self.tdl_history = net.process(self.p)

            # print("Input:", self.p)
            # print("Output:", self.a)

            self.graph()
            self.update_table()
            
        except ValueError:
            # Show error if parsing fails
            QtWidgets.QMessageBox.critical(self, "Input Error", 
                "Please enter valid integer values for all parameters.")

    def graph(self):
        min_value = min(min(self.p), min(self.a))
        max_value = max(max(self.p), max(self.a))
        self.plot_sequence(self.p, self.figure, self.canvas, r'Input Sequence $p(t)$', min_value, max_value)
        self.plot_sequence(self.a, self.figure2, self.canvas2, r'Output Sequence $a(t)$', min_value, max_value)

    def plot_sequence(self, array, figure, canvas, title, min_value, max_value):
        figure.clf()
        ax = figure.add_subplot(1, 1, 1)
        
        x = np.arange(len(array))
        
        # Create stem plot with blue markers and lines
        markerline, stemlines, baseline = ax.stem(x, array)
        
        # Set stem formatting (blue color)
        plt.setp(markerline, 'color', 'blue', 'markersize', 4)
        plt.setp(stemlines, 'color', 'blue', 'linewidth', 2)
        
        # Set axis limits
        ax.set_xlim(-0.5, len(array) - 0.5)
        y_max = max_value * 1.1 if max_value > 0 else 1  # Add 10% margin on top
        y_min = min_value * 1.1 if min_value < 0 else -0.1
        ax.set_ylim(y_min, y_max)
        
        # Set integer ticks for x-axis
        x_ticks = np.arange(0, len(array), max(1, len(array)//8))  # Show at most 8 ticks
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(int(tick)) for tick in x_ticks])
        
        # Set integer ticks for y-axis
        y_range = y_max - y_min
        y_interval = max(1, int(y_range // 5))  # Show about 5 ticks
        y_start = int(np.floor(y_min))
        y_end = int(np.ceil(y_max))
        y_ticks = np.arange(y_start, y_end + 1, y_interval)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([str(int(tick)) for tick in y_ticks])
        
        # Add title
        ax.set_title(title, fontsize=12, pad=5)
        
        # Update the canvas
        canvas.draw()

import numpy as np
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH
from PyQt6 import QtWidgets, QtCore
from nndesigndemos.book2.chapter8.utils import PatternPlot, gen_shape_matrix, generate_slash, gen_zero_matrix, matrix_size_down, matrix_size_up, KERNEL_SIZE_MAX


class Convol(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi, res_x_offset=0):
        super(Convol, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Convolution Network", 8,
                          "Change the input shape, \ninput size, kernel size,\nand stride below.\n\nUse checkboxs to change\npadding and value status.\n\nClick input or kernel images\nto change the input pattern\nor kernel pattern.",
                          PACKAGE_PATH + "Logo/Logo_Ch_7.svg", None, 2,)

        self.stride = 1
        self.pad_on = False
        self.padding_top_left = 0
        self.padding_bottom_right = 0
        self.label_on = False
        self.shape_idx = 0

        self.kernel_size = 2

        self.make_label("label_pattern1", "Input Pattern", (115, 105, 150, 50))
        self.make_plot(1, (15, 130, 270, 270))
        self.axis1 = self.figure.add_axes([0, 0, 1, 1])
        self.pattern1 = PatternPlot(self.axis1, gen_shape_matrix(6, self.shape_idx), self.label_on)
        self.canvas.show()
        self.canvas.mpl_connect("button_press_event", self.on_mouseclick1)

        self.make_label("label_pattern2", "Kernel", (380, 180, 150, 50))
        self.make_plot(2, (340, 205, 120, 120))
        self.axis2 = self.figure2.add_axes([0, 0, 1, 1])
        self.pattern2 = PatternPlot(self.axis2, generate_slash(self.kernel_size), self.label_on)
        self.canvas2.show()
        self.canvas2.mpl_connect("button_press_event", self.on_mouseclick2)

        self.make_label("label_pattern3", "Response Pattern", (210-res_x_offset, 405, 150, 50))
        self.make_plot(3, (150-res_x_offset, 430, 220, 220))
        self.axis3 = self.figure3.add_axes([0, 0, 1, 1])
        self.pattern3 = PatternPlot(self.axis3, self.get_response_matrix(), self.label_on, True, self.kernel_size)
        self.canvas3.show()

        # coords meaning: x, y, width, height
        self.make_combobox(1, ['Diamond', 'Square', 'Random', 'Custom'],
                           (self.x_chapter_usual, 310, self.w_chapter_slider, 100),
                           self.change_input_shape, "label_combobox", "Input shape",
                           (self.x_chapter_usual + 50, 310, 100, 50))

        self.make_slider("slider_n_input", QtCore.Qt.Orientation.Horizontal, (6, 20), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 6,
                         (self.x_chapter_usual, 400, self.w_chapter_slider, 50), self.change_input_size, "label_n_input",
                         "Input size: 6", (self.x_chapter_usual + 20, 400 - 25, self.w_chapter_slider, 50))

        self.make_slider("slider_n_kernel", QtCore.Qt.Orientation.Horizontal, (2, KERNEL_SIZE_MAX), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 2,
                         (self.x_chapter_usual, 460, self.w_chapter_slider, 50), self.change_kernel_size, "label_n_kernel",
                         "Kernel size: 2", (self.x_chapter_usual + 20, 460 - 25, self.w_chapter_slider, 50))

        self.make_slider("slider_n_strides", QtCore.Qt.Orientation.Horizontal, (1, 3), QtWidgets.QSlider.TickPosition.TicksBelow, 1, 1,
                         (self.x_chapter_usual, 520, self.w_chapter_slider, 50), self.use_stride, "label_n_strides",
                         "Stride(s): 1", (self.x_chapter_usual + 20, 520 - 25, self.w_chapter_slider, 50))

        self.make_checkbox('checkbox_pad', 'Padding', (self.x_chapter_usual, 560, self.w_chapter_slider, 40),
                           self.use_pad, False)

        self.make_checkbox('checkbox_label', 'Show values', (self.x_chapter_usual, 595, self.w_chapter_slider, 40),
                           self.use_label, False)
        
        self.is_animating = False
        self.animation_enabled = False

    def stop_animation(self):
        pass

    def prepare_animation_frames(self):
        pass

    def get_response_matrix(self, animation_frames=None):
        stride = self.stride
        pattern1 = self.pattern1
        pattern2 = self.pattern2
        self.size1 = pattern1.get_size()
        self.size2 = pattern2.get_size()

        self.size3 = (self.size1 - self.size2) // stride + 1
        output = gen_zero_matrix(self.size3)

        matrix1 = pattern1.matrix[::-1]
        matrix2 = pattern2.matrix[::-1]

        for i in range(0, self.size3 * stride, stride):
            for j in range(0, self.size3 * stride, stride):
                current_value = np.sum(matrix1[i:i + self.size2, j:j + self.size2] * matrix2)
                output[i // stride, j // stride] = current_value

                if animation_frames is not None:
                    animation_frames.append({
                        'input_pos': (i, j),
                        'output_pos': (i // stride, j // stride),
                        'value': current_value,
                        'output_matrix': output.copy()
                    })

        return output[::-1] if animation_frames is None else animation_frames

    def on_mouseclick_base(self, event, pattern, canvas, axis, pattern_idx):
        if event.xdata is not None and event.ydata is not None:
            # print('event', event, 'event.xdata', event.xdata)
            d_x = [abs(event.xdata - xx - 0.5) for xx in pattern.xx_up]
            d_y = [abs(event.ydata - yy - 0.5) for yy in pattern.yy_up]
            xxx, yyy = list(range(len(pattern.xx_up)))[np.argmin(d_x)], list(range(len(pattern.yy_up)))[np.argmin(d_y)]

            pattern.matrix[yyy, xxx] = 1 - pattern.matrix[yyy, xxx]

            new_pattern = self.draw_pattern12(pattern, axis, pattern.matrix, canvas)
            if pattern_idx == 1:
                self.pattern1 = new_pattern
            else:
                self.pattern2 = new_pattern

            self.draw_pattern3()

    def on_mouseclick1(self, event):
        self.on_mouseclick_base(event, self.pattern1, self.canvas, self.axis1, 1)

    def on_mouseclick2(self, event):
        self.on_mouseclick_base(event, self.pattern2, self.canvas2, self.axis2, 2)

    def draw_pattern12(self, pattern, axis, matrix, canvas):
        pattern.remove_text()
        pattern.remove_patch()
        pattern = PatternPlot(axis, matrix, self.label_on)
        canvas.draw()
        return pattern

    def draw_pattern3(self):
        if self.animation_enabled:
            self.prepare_animation_frames()
            return
        
        self.pattern3.remove_text()
        self.pattern3.remove_patch()
        self.pattern3 = PatternPlot(self.axis3, self.get_response_matrix(), self.label_on, True, self.kernel_size)
        self.canvas3.draw()

    def change_input(self, size):
        if self.is_animating:
            self.stop_animation()
        
        # if self.shape_idx == 3:
        #     matrix2 = gen_zero_matrix(self.pattern2.get_size())
        #     self.pattern2 = self.draw_pattern12(self.pattern2, self.axis2, matrix2, self.canvas2)

        matrix1 = gen_shape_matrix(size, self.shape_idx)
        if self.pad_on:
            matrix1 = self.gen_padding_matrix(matrix1, self.pattern2.get_size())

        self.pattern1 = self.draw_pattern12(self.pattern1, self.axis1, matrix1, self.canvas)
        self.draw_pattern3()

    def change_input_shape(self, idx):
        if self.is_animating:
            self.stop_animation()
        
        self.shape_idx = idx
        self.change_input(self.pattern1.get_size())

    def change_input_size(self):
        if self.is_animating:
            self.stop_animation()
        
        new_size = self.slider_n_input.value()
        self.label_n_input.setText(f"Input size: {new_size}")
        self.change_input(new_size)

    def change_kernel_size(self):
        if self.is_animating:
            self.stop_animation()
        
        self.kernel_size = self.slider_n_kernel.value()
        self.label_n_kernel.setText(f"Kernel size: {self.kernel_size}")

        # Changing kernel size causes response pattern size changes. To keep response size
        # as the same as input, we need to recalculate the input if it's in the padding status.
        # Steps: 1.reverse input to no padding status; 2.use new kernel size to pad input again.
        if self.pad_on:
            self.pad_on = False
            matrix1_reverse = self.gen_padding_matrix(self.pattern1.matrix, self.pattern2.get_size())
            self.pad_on = True
            matrix1_new = self.gen_padding_matrix(matrix1_reverse, self.kernel_size)
            self.pattern1 = self.draw_pattern12(self.pattern1, self.axis1, matrix1_new, self.canvas)

        matrix2 = generate_slash(self.kernel_size)

        self.pattern2 = self.draw_pattern12(self.pattern2, self.axis2, matrix2, self.canvas2)

        self.draw_pattern3()

    def gen_padding_matrix(self, old_matrix, kernel_size):
        if self.pad_on:
            self.padding_top_left = (kernel_size - 1) // 2
            self.padding_bottom_right = kernel_size // 2
            matrix = matrix_size_up(old_matrix, self.padding_bottom_right, self.padding_top_left)
        else:
            matrix = matrix_size_down(old_matrix, self.padding_bottom_right, self.padding_top_left)
            self.padding_top_left = 0
            self.padding_bottom_right = 0

        return matrix

    def use_pad(self):
        if self.is_animating:
            self.stop_animation()
        
        self.pad_on = True if self.checkbox_pad.checkState().value == 2 else False
        matrix = self.gen_padding_matrix(self.pattern1.matrix, self.pattern2.get_size())

        self.pattern1 = self.draw_pattern12(self.pattern1, self.axis1, matrix, self.canvas)
        self.draw_pattern3()

    def use_stride(self):
        if self.is_animating:
            self.stop_animation()
        
        self.stride = self.slider_n_strides.value()
        self.label_n_strides.setText(f"Stride(s): {self.stride}")
        self.draw_pattern3()

    def use_label(self):
        if self.is_animating:
            self.stop_animation()
            
        self.label_on = True if self.checkbox_label.checkState().value == 2 else False

        self.pattern1.label_display(self.label_on)
        self.pattern2.label_display(self.label_on)

        self.canvas.draw()
        self.canvas2.draw()

        if self.animation_enabled:
            self.prepare_animation_frames()
        else:
            self.pattern3.label_display(self.label_on)
            self.canvas3.draw()


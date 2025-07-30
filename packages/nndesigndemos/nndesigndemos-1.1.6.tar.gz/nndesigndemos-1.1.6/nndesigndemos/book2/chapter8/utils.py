import matplotlib.patches as patches
import numpy as np

# To do:
# try draw a box. apply the changes to the image
# https://www.color-hex.com

KERNEL_SIZE_MAX = 6


# Dynamically generate color ranges for the response pattern.
def interpolate_colors(start_hex, end_hex, steps):
    # Convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Convert RGB to hex
    def rgb_to_hex(rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)

    # Calculate the difference
    r_diff = (end_rgb[0] - start_rgb[0]) / steps
    g_diff = (end_rgb[1] - start_rgb[1]) / steps
    b_diff = (end_rgb[2] - start_rgb[2]) / steps

    # Generate the colors
    colors = []
    for i in range(steps + 1):
        r = int(start_rgb[0] + (r_diff * i))
        g = int(start_rgb[1] + (g_diff * i))
        b = int(start_rgb[2] + (b_diff * i))
        colors.append(rgb_to_hex((r, g, b)))

    return colors


def pick_items_with_intervals(lst, num_items):
    indices = np.linspace(0, len(lst) - 1, num_items, dtype=int)
    return [lst[i] for i in indices]


color_dic = {
    'input': ['khaki', 'green'],
    'output': interpolate_colors('#f8f7e2', '#2c2d2a', KERNEL_SIZE_MAX * KERNEL_SIZE_MAX),  # Generate color ranges
}


def generate_diamond(n):
    diamond = gen_zero_matrix(n)
    center = n // 2
    if n % 2 == 0:
        for i in range(center):
            left = center - i - 1
            right = center + i
            bottom = n - i - 1

            diamond[left, i] = 1
            diamond[right, i] = 1
            diamond[left, bottom] = 1
            diamond[right, bottom] = 1
    else:
        for i in range(n):
            for j in range(n):
                if abs(i - center) + abs(j - center) == center:
                    diamond[i, j] = 1

    return diamond


def generate_square(n, size):
    square = gen_zero_matrix(n)
    start = (n - size) // 2
    end = start + size

    # Create the boundary
    square[start:end, start] = 1  # Left side
    square[start:end, end - 1] = 1  # Right side
    square[start, start:end] = 1  # Top side
    square[end - 1, start:end] = 1  # Bottom side

    return square


def generate_slash(n):
    slash = gen_zero_matrix(n)
    for i in range(n):
        slash[i, i] = 1
    return slash


def gen_random_matrix(size):
    return np.random.randint(0, 2, size=(size, size))


def gen_zero_matrix(size):
    return np.zeros((size, size), dtype=int)


def gen_shape_matrix(size, idx):
    if idx == 0:
        matrix = generate_diamond(size)
    elif idx == 1:
        matrix = generate_square(size, size - 2)
    elif idx == 2:
        matrix = gen_random_matrix(size)
    elif idx == 3:
        matrix = gen_zero_matrix(size)
    else:
        raise Exception('Not possible')

    return matrix


class PatternPlot:
    def __init__(self, axis, matrix, label_on, response_pattern=False, kernel_size=None):

        self.axis = axis
        self.matrix = matrix
        self.size = len(matrix)
        if response_pattern:
            response_color_range = kernel_size * kernel_size + 1
            self.color_lst = pick_items_with_intervals(color_dic['output'], response_color_range)
        else:
            self.color_lst = color_dic['input']

        self.wid_up = 1
        inbetween_up = 0.1
        self.xx_up = np.arange(0, self.size * 1.1, (self.wid_up + inbetween_up))
        self.yy_up = np.arange(0, self.size * 1.1, (self.wid_up + inbetween_up))

        self.label_on = label_on
        self.texts = []
        self.plot(self.matrix)
        self.axis.axis([-0.1, self.size + 0.1 * self.size, -0.1, self.size + 0.1 * self.size])
        self.axis.axis("off")

        # Highlight rectangle for animation
        self.highlight_rect = None

    def get_size(self):
        return self.size

    def remove_text(self):
        for text in self.texts:
            text.remove()
        self.texts = []

    def add_text(self):
        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                text = self.axis.text(self.xx_up[xi] + self.wid_up / 2, self.yy_up[yi] + self.wid_up / 2,
                                      str(self.matrix[yi, xi]), color="black", ha='center', va='center', fontsize=12)
                self.texts.append(text)

    def plot(self, matrix):
        self.matrix = matrix

        for xi in range(len(self.xx_up)):
            for yi in range(len(self.yy_up)):
                color = self.color_lst[matrix[yi, xi]]
                sq = patches.Rectangle((self.xx_up[xi], self.yy_up[yi]), self.wid_up, self.wid_up, fill=True,
                                       color=color)
                self.axis.add_patch(sq)

        if self.label_on:
            self.remove_text()  # remove old and add new
            self.add_text()

    def highlight_area(self, start_x, start_y, kernel_size, canvas):
        """Highlights an area on the pattern for animation"""
        if self.highlight_rect:
            self.highlight_rect.remove()
            
        # Convert from matrix indices to plot coordinates
        plot_x = self.xx_up[start_x]
        plot_y = self.yy_up[start_y]
        width = kernel_size * (self.wid_up + 0.1) - 0.1
        height = kernel_size * (self.wid_up + 0.1) - 0.1
        
        self.highlight_rect = patches.Rectangle(
            (plot_x, plot_y), width, height, 
            fill=False, edgecolor='red', linestyle='--', linewidth=2
        )
        self.axis.add_patch(self.highlight_rect)
        canvas.draw()
        
    def clear_highlight(self, canvas):
        """Removes the highlight rectangle"""
        if self.highlight_rect:
            self.highlight_rect.remove()
            self.highlight_rect = None
            canvas.draw()
    
    def label_display(self, label_on):
        self.label_on = label_on
        if self.label_on:
            self.add_text()
        else:
            self.remove_text()

    def remove_patch(self):
        for patch in self.axis.patches:
            patch.remove()


def matrix_size_down(old_matrix, padding_bottom_right, padding_top_left):
    old_len = len(old_matrix)
    matrix = old_matrix[
             padding_bottom_right:old_len - padding_top_left,
             padding_top_left:old_len - padding_bottom_right
             ]
    return matrix


def matrix_size_up(old_matrix, padding_bottom_right, padding_top_left):
    matrix = np.pad(
        old_matrix,
        pad_width=(
            (padding_bottom_right, padding_top_left),  # reverse the order because the display is upside down
            (padding_top_left, padding_bottom_right)
        ),
        mode='constant',
        constant_values=0,
    )
    return matrix
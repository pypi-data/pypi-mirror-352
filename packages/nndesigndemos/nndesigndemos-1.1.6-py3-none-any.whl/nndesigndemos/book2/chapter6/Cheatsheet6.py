import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout, open_link
from nndesigndemos.get_package_path import PACKAGE_PATH


class Cheatsheet6(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Cheatsheet6, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("TensorFlow Intro Cheatsheet", 6, "Click on each cheatsheet to\nopen it.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, 2, description_coords=(535, 40, 450, 300))

        absolute_path = PACKAGE_PATH + "book2/chapter6/TensorFlow2Cheatsheet.pdf"

        if os.name == "nt":
            absolute_path = absolute_path.replace("\\", "/")
            file_uri = f"file:///{absolute_path}"
        else:
            file_uri = f"file://{absolute_path}"

        label_str = f'<a href="{file_uri}">0. TensorFlow Cheatsheet</a>'

        self.make_label("book1_link", label_str, (200, 350, 200, 50))
        self.book1_link.linkActivated.connect(open_link)

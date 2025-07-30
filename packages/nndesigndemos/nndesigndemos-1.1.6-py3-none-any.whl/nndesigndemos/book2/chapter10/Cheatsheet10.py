import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout, open_link
from nndesigndemos.get_package_path import PACKAGE_PATH


class Cheatsheet10(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Cheatsheet10, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("PyTorch Intro Cheatsheets", 10, "Click on each cheatsheet to\nopen it.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, 2, description_coords=(535, 40, 450, 300))

        all_files = [
            'cheatsheet_pytorch.pdf',
            'pytorch-cheatsheet-en.pdf',
        ]

        for i, file_name in enumerate(all_files):
            absolute_path = PACKAGE_PATH + "book2/chapter10/cheatsheets/" + file_name
            if os.name == "nt":
                absolute_path = absolute_path.replace("\\", "/")
                file_uri = f"file:///{absolute_path}"
            else:
                file_uri = f"file://{absolute_path}"

            label_str = f'<a href="{file_uri}">{i}. {file_name}</a>'
            label_attr_name = f"book{i}_link"
            self.make_label(label_attr_name, label_str, (200, 330 + 27 * i, 200, 50))
            label = getattr(self, label_attr_name)
            label.linkActivated.connect(open_link)

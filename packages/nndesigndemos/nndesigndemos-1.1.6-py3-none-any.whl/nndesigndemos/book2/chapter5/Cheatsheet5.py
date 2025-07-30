import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from nndesigndemos.nndesign_layout import NNDLayout, open_link
from nndesigndemos.get_package_path import PACKAGE_PATH


class Cheatsheet5(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(Cheatsheet5, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Python Intro Cheatsheets", 5, "Click on each cheatsheet to\nopen it.",
                          PACKAGE_PATH + "Logo/Logo_Ch_13.svg", None, 2, description_coords=(535, 40, 450, 300))

        all_files = [
            'Jupyter Notebook.pdf',
            'Base Python.pdf',
            'If While.pdf',
            'List.pdf',
            'Dictionaries.pdf',
            'Open-WriteFiles .pdf',
            'Functions.pdf',
            'Classes.pdf',
            'Code Debug.pdf',
            'Scipy-Linalgebra.pdf',
            'Numpy.pdf',
            'Pands1.pdf',
            'Pands2.pdf',
            'Matplotlib.pdf',
            'Matplotlib2.pdf',
            'Bokeh.pdf',
            'Django.pdf',
            'Data Structure 1.pdf',
            'Data Structure 2.pdf',
            'Data Structure 3.pdf',
        ]

        for i, file_name in enumerate(all_files):
            absolute_path = PACKAGE_PATH + "book2/chapter5/cheatsheets/" + file_name

            if os.name == "nt":
                absolute_path = absolute_path.replace("\\", "/")
                file_uri = f"file:///{absolute_path}"
            else:
                file_uri = f"file://{absolute_path}"

            label_str = f'<a href="{file_uri}">{i}. {file_name}</a>'
            label_attr_name = f"book{i}_link"
            self.make_label(label_attr_name, label_str, (200, 105 + 27 * i, 200, 50))
            label = getattr(self, label_attr_name)
            label.linkActivated.connect(open_link)

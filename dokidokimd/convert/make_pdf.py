from dokidokimd import PROJECT_NAME

import os
from os import listdir
from os.path import isfile, join
from fpdf import FPDF
from PIL import Image


class PDF:
    def __init__(self, name):
        self.name = name
        self.num_pages = 0
        self.images = None
        self.pages = list()
        self.builder = None

    def add_page(self, image_path, index=None):
        if index is None:
            self.pages.append(image_path)
        elif index is not None:
            self.pages.insert(index, image_path)

        self.num_pages += 1
        #self.builder.add_page(image, orientation)

    def remove_page(self, index=None):
        if index is None:
            self.pages.pop(self.num_pages-1)
            self.pages_orientation.pop(self.num_pages-1)
        elif index is not None:
            self.pages.pop(index)
            self.pages_orientation.pop(index)

        self.num_pages -= 1

    def make_pdf(self):
        cover = Image.open(self.pages[0])
        width, height = cover.size
        self.builder = FPDF(unit="pt", format=[width, height])

        self.builder.set_title(self.name)
        self.builder.set_author(PROJECT_NAME)

        for i in range(self.num_pages):
            width2, height2 = Image.open(self.pages[i]).size
            if width2 > height2:
                orientation = "L"
            else:
                orientation = "P"
            self.builder.add_page(orientation)

            x = y = 0
            if width2 != width and height2 != height:
                w = width2 / width
                h = height2 / height
                if w < h:
                    height2 = height
                    x = (width - width2/h)/2
                    width2 = 0
                else:
                    width2 = width
                    y = (height - height2/w)/2
                    height2 = 0

            if orientation is "L":
                self.builder.image(self.pages[i], y, x, width2, height2)
            else:
                self.builder.image(self.pages[i], x, y, width2, height2)

    def add_dir(self, dir_path, extension_filter=None):
        if extension_filter is None:
            files = [os.path.join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))]
        else:
            files = [os.path.join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f) and f.endswith("."+extension_filter))]

        for f in files:
            self.add_page(f)

        # self.builder.output()

    def save_pdf(self, path):
        self.builder.output(path, "F")

if __name__ == "__main__":
    pass
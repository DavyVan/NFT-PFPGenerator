import argparse
import os

from nft_generator.Printers import *
from nft_generator.constants import SUPPORTED_OUTPUT_FORMAT
from nft_generator.Layer import Layer
from nft_generator.Combination import Combination


class Collection:

    def __init__(self, argv):
        self.path = ""                  # type: str
        self.count = 0                  # type: int
        self.output_format = ""         # type: str
        self.output_path = ""           # type: str
        self.layers = []                # type: list[Layer]
        self.subdir_sep = ""            # type: str
        self.combinations = []          # type: list[Combination]

        self.__parse_args(argv)
        self.__check_and_get_subdirs()

    def __parse_args(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("path",
                            help="The path of working directory where you store all the resource images. Use '\\\\' on Windows.",
                            type=str)
        parser.add_argument("count", help="The total number of NFTs you want to generate.", type=int)
        parser.add_argument("-of", "--output-format", help="The output format. Default: png", default="png", type=str)
        parser.add_argument("-o", "--output-path", help="The output path. Default: current working directory",
                            default=".", type=str)
        parser.add_argument("--sep", help="The separator of layer folders. Default: <space>", default=" ", type=str)
        parser.add_argument("-m", "--meta-std", help="The metadata standard e.g. enjin or opensea. Default: opensea", default="opensea", type=str)
        parser.add_argument("-n", "--collection-name", help="The collection name.", default="Test-NFT", type=str)
        args = parser.parse_args()

        self.path = args.path       # will verify later
        print_info("Path: " + self.path)

        self.count = args.count
        if self.count <= 0:
            raise ValueError("Collection: count must be greater than zero.")
        print_info("Count: " + str(self.count))

        self.output_format = args.output_format
        if not self.__is_supported_output_format(self.output_format):
            raise ValueError("Collection: output format " + self.output_format + " is not supported.")
        print_info("Output_format: " + str(self.output_format).upper())

        self.output_path = args.output_path
        if self.output_path == ".":
            self.output_path = os.path.join(os.getcwd(), "output")
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)
        print_info("Output_path (created if not exists): " + self.output_path)

        self.subdir_sep = args.sep
        print_info("Layer folder separator: " + ("<space>" if self.subdir_sep == " " else self.subdir_sep))

        # TODO: -m & -n

        print_ok_with_prefix("Parsing arguments...")

    def __is_supported_output_format(self, ext: str) -> bool:
        return ext.lower() in SUPPORTED_OUTPUT_FORMAT

    def __check_and_get_subdirs(self):
        """
        检查根目录存在，检查子目录都被编号而且按顺序，会自动排除掉没有按照规则命名的文件夹
        子目录命名规则：<数字编号，位数不限>.<其他内容>
        即编号和文件夹名中间用点分割。要求编号从1开始且必须连续不能有空缺。
        """

        # check the root dir
        if not os.path.isdir(self.path):
            raise FileNotFoundError("Collection: The base directory does not exist.")

        # get all the entries, including files and subdirs
        entries = os.listdir(self.path)
        entry_selected = []         # type: list[Layer]
        for entry in entries:
            # only pick directories
            if not os.path.isdir(os.path.join(self.path, entry)):
                continue

            # retrieve the layer number and layer name
            splited = entry.split(self.subdir_sep, 1)
            if len(splited) == 0:
                continue
            # Check the first element
            if splited[0] == "" or not splited[0].isnumeric():
                continue
            layer_number = int(splited[0])
            # Check the second element
            layer_name = ""
            if len(splited) < 2 or splited[1] == "":
                layer_name = "Layer " + str(len(entry_selected)+1)
            else:
                layer_name = splited[1]

            # append new Layer
            entry_selected.append(Layer(layer_number, layer_name, os.path.join(self.path, entry)))

        if len(entry_selected) == 0:
            raise FileNotFoundError("Collection: did not find available folders")

        # sort and check the numbers if they are in sequence
        _sorted = sorted(entry_selected, key=lambda l: l.index)
        for i in range(len(_sorted)):
            if i+1 != _sorted[i].index:
                raise ValueError("Collection: The numbers of subdirs are not in sequence")

        self.layers = _sorted
        print_ok_with_prefix("Checking folders...")

    def print_layers(self):
        if len(self.layers) == 0:
            print_warning("No layer to print.")
        else:
            for l in self.layers:
                print(l.index, l.name, l.path)

    def generate(self):
        combinations_set = set()
        i = 0
        while i < self.count:
            combo = Combination()
            for l in self.layers:
                combo.add_item(l.get_item())

            # check duplication
            if combo in combinations_set:
                continue
            combinations_set.add(combo)
            self.combinations.append(combo)
            combo.commit()
            i += 1

        print_ok_with_prefix("Generate combinations...")

    def render(self):
        for i, c in enumerate(self.combinations):
            print(i)
            c.render(self.output_path, i+1, self.output_format)

    def print_stat(self):
        for l in self.layers:
            l.print_stat()

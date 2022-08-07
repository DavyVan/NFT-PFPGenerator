import os
import json
import time

from nft_generator.Printers import *
from nft_generator.Config import Config
from nft_generator.Layer import Layer
from nft_generator.Combination import Combination


class Collection:

    def __init__(self):
        self.config = Config()          # type: Config
        self.layers = []                # type: list[Layer]
        self.combinations = []          # type: list[Combination]

        self.__check_and_get_subdirs()

    def __check_and_get_subdirs(self):
        """
        检查根目录存在，检查子目录都被编号而且按顺序，会自动排除掉没有按照规则命名的文件夹
        子目录命名规则：<数字编号，位数不限>.<其他内容>
        即编号和文件夹名中间用点分割。要求编号从1开始且必须连续不能有空缺。
        """

        # check the root dir
        if not os.path.isdir(self.config.path):
            raise FileNotFoundError("Collection: The base directory does not exist.")

        # get all the entries, including files and subdirs
        entries = os.listdir(self.config.path)
        entry_selected = []         # type: list[Layer]
        for entry in entries:
            # only pick directories
            if not os.path.isdir(os.path.join(self.config.path, entry)):
                continue

            # retrieve the layer number and layer name
            splited = entry.split(self.config.subdir_sep, 1)
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
            entry_selected.append(Layer(layer_number, layer_name, os.path.join(self.config.path, entry)))

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
        while i < self.config.count:
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

        print_ok_with_prefix("Generating combinations...")

    def render(self):
        start = time.time_ns() // 1000000
        for i, c in enumerate(self.combinations):
            # print(i)
            c.render(i+1, self.config)
        end = time.time_ns() // 1000000
        print_info("Time spent: " + str(end - start) + "ms")
        print_ok_with_prefix("Rendered all images...")

    def print_stat(self):
        for l in self.layers:
            l.print_stat()

    def generate_metadata(self):
        # check metadata output path
        metadata_output_path = os.path.join(self.config.output_path, "metadata")
        if not os.path.isdir(metadata_output_path):
            os.makedirs(metadata_output_path)

        metadata_all = dict()
        metadata_all["name"] = self.config.metadata_name
        metadata_all["generator"] = "The NFT Generator"
        metadata_all["generator_author"] = "Quan Fan @ 2M/WM"
        metadata_collection = list()

        for i, c in enumerate(self.combinations):
            m = c.generate_metadata(i+1, self.config)
            metadata_collection.append(m)
            # write into separate file
            with open(os.path.join(self.config.output_path, "metadata", str(i+1) + ".json"), "w") as fd:
                json.dump(m, fd, indent=2, ensure_ascii=False)

        metadata_all["collection"] = metadata_collection
        with open(os.path.join(self.config.output_path, "metadata", "metadata.json"), "w") as fd:
            json.dump(metadata_all, fd, indent=2, ensure_ascii=False)

        print_ok_with_prefix("Generating metadata...")

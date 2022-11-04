import os
import json
import time
from multiprocessing.connection import Connection
import xlsxwriter
import pandas as pd
from send2trash import send2trash

from nft_generator.Printers import *
from nft_generator.Config import Config
from nft_generator.Layer import Layer
from nft_generator.Combination import Combination
from nft_generator.Errors import NFTGError as E
from nft_generator.Constants import EXCEL_SELECTED_YES_STR, EXCEL_SELECTED_NO_STR, EXCEL_SEQ_STR, EXCEL_SELECTED_STR


class Collection:

    def __init__(self, jsonstr: str = None):
        self.config = Config(jsonstr)       # type: Config
        self.layers = []                    # type: list[Layer]
        self.combinations = []              # type: list[Combination]
        self.__progress = 0                 # type: int

        self.__check_and_get_subdirs()

    def __check_and_get_subdirs(self):
        """
        检查根目录存在，检查子目录都被编号而且按顺序，会自动排除掉没有按照规则命名的文件夹
        子目录命名规则：<数字编号，位数不限>.<其他内容>
        即编号和文件夹名中间用点分割。要求编号从1开始且必须连续不能有空缺。
        """

        # check the root dir
        if not os.path.isdir(self.config.path):
            raise E(E.ERR_IO_PATH_NOT_EXIST)

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
            raise E(E.ERR_IO_NO_AVAL_LAYER)

        # sort and check the numbers if they are in sequence
        _sorted = sorted(entry_selected, key=lambda l: l.index)
        for i in range(len(_sorted)):
            if i+1 != _sorted[i].index:
                raise E(E.ERR_IO_LAYER_SEQ)
        self.layers = _sorted

        # check theoretical limit
        limit = 1
        for l in self.layers:
            limit *= len(l.items)
        if self.config.count > limit:
            raise E(E.ERR_RT_COUNT_EXCEED, limit)

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

    def render(self, fd: Connection = None):
        try:
            start = time.time_ns() // 1000000
            for i, c in enumerate(self.combinations):
                # print(i)
                c.render(i+self.config.starting_index, self.config)
                self.__progress += 1
                if fd is not None:
                    fd.send(json.dumps({
                        "success": True,
                        "message": "",
                        "data": i+1
                    }))
            end = time.time_ns() // 1000000
            if fd is not None:
                fd.send(json.dumps({
                    "success": True,
                    "message": "",
                    "data": -1
                }))
                fd.close()
            print_info("Time spent: " + str(end - start) + "ms")
            print_ok_with_prefix("Rendered all images...")
        except E as e:
            code, *others = e.args
            fd.send(json.dumps({
                "success": False,
                "message": E.errmsg(e),
                "data": others,
                "code": code
            }))
            fd.close()
        except Exception as e:
            fd.send(json.dumps({
                "success": False,
                "message": E.errmsg(e),
                "data": "",
                "code": 0
            }))
            fd.close()

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
            m = c.generate_metadata(i+self.config.starting_index, self.config)
            metadata_collection.append(m)
            # write into separate file
            with open(os.path.join(metadata_output_path, str(i+self.config.starting_index) + ".json"), "w") as fd:
                json.dump(m, fd, indent=2, ensure_ascii=False)

        metadata_all["collection"] = metadata_collection
        with open(os.path.join(metadata_output_path, "metadata%d.json" % self.config.starting_index), "w") as fd:
            json.dump(metadata_all, fd, indent=2, ensure_ascii=False)

        print_ok_with_prefix("Generating metadata...")

    def generate_excel(self):
        with xlsxwriter.Workbook(os.path.join(self.config.output_path, "stats%d.xlsx" % self.config.starting_index)) as workbook:
            worksheet = workbook.add_worksheet()

            # headings
            headings = ["编号", "是否选用"]
            for l in self.layers:
                headings.append(l.name)
            worksheet.write_row(0, 0, headings)

            # data
            for i, combo in enumerate(self.combinations):
                data = [i+self.config.starting_index, EXCEL_SELECTED_YES_STR]
                for item in combo.items:
                    data.append(item.item_name)
                worksheet.write_row(i+1, 0, data)

            # set validator(list) for col 1 (zero indexed)
            worksheet.data_validation(1, 1, len(self.combinations), 1, {
                "validate": "list",
                "source": [EXCEL_SELECTED_YES_STR, EXCEL_SELECTED_NO_STR]
            })

            # set filters
            worksheet.autofilter(0, 1, len(self.combinations), len(self.layers)+1)

    def get_progress(self) -> (int, int):
        """

        :return: (progress, total)
        """
        return self.__progress, self.config.count

    def inc_progress(self) -> (int, int):
        """
        Increase the progress counter and return it.
        :return: (increased_progress, total)
        """
        self.__progress += 1
        return self.__progress, self.config.count

    @classmethod
    def generate_metadata_from_excel(cls, excel_path: str, folder_path: str, collection_name: str, enable_delete: bool,
                                     enable_reorder: bool, metadata_std: str) -> int:
        df = pd.read_excel(excel_path, dtype=str)
        layer_labels = df.columns[2:]

        metadata_output_path = os.path.join(folder_path, "metadata")
        if not os.path.isdir(metadata_output_path):
            os.makedirs(metadata_output_path)

        # starting index
        starting_index = int(df.iloc[0][EXCEL_SEQ_STR])

        metadata_all = dict()
        metadata_all["name"] = collection_name
        metadata_all["generator"] = "The NFT Generator"
        metadata_all["generator_author"] = "Quan Fan @ 2M/WM"
        metadata_collection = list()
        count = starting_index

        for row in df.itertuples(index=False):
            if getattr(row, EXCEL_SELECTED_STR) == EXCEL_SELECTED_NO_STR:
                if enable_delete:
                    p = os.path.join(folder_path, str(getattr(row, EXCEL_SEQ_STR)) + ".png")
                    send2trash(p)
                    print_info("Moved file to trash: " + p)
                continue

            i = int(getattr(row, EXCEL_SEQ_STR))
            if enable_reorder and i != count:
                # rename file
                src = os.path.join(folder_path, str(getattr(row, EXCEL_SEQ_STR)) + ".png")
                dst = os.path.join(folder_path, str(count) + ".png")
                os.rename(src, dst)
                print_info("Renamed file: %s -> %s" % (src, dst))
                i = count

            # assemble metadata
            m = dict()
            m["name"] = "%s #%d" % (collection_name, i)
            m["description"] = ""
            m["image"] = "%d.%s" % (i, "png")
            if metadata_std == "opensea":
                attrs = list()
                for l in layer_labels:
                    attrs.append({"trait_type": l, "value": getattr(row, l)})
                m["attributes"] = attrs
            elif metadata_std == "enjin":
                props = dict()
                for l in layer_labels:
                    props[l] = getattr(row, l)
                m["properties"] = props

            metadata_collection.append(m)

            # write into separate file
            with open(os.path.join(metadata_output_path, str(i) + ".json"), "w") as fd:
                json.dump(m, fd, indent=2, ensure_ascii=False)

            count += 1

        metadata_all["collection"] = metadata_collection
        with open(os.path.join(metadata_output_path, "metadata%d.json" % starting_index), "w") as fd:
            json.dump(metadata_all, fd, indent=2, ensure_ascii=False)

        return count - starting_index


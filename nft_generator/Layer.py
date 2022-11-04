import os
import random

from nft_generator.LayerItem import LayerItem
from nft_generator.Constants import SUPPORTED_INPUT_FORMAT
from nft_generator.Printers import *
from nft_generator.Errors import NFTGError as E


class Layer:

    def __init__(self, index, name, path):
        self.index = index          # type: int
        self.name = name            # type: str
        self.path = path            # type: str
        self.items = []             # type: list[LayerItem]

        self.__check_resources()

    def __check_resources(self):
        files = os.listdir(self.path)
        for f in files:
            if not os.path.isfile(os.path.join(self.path, f)):
                print_warning("%s is not a file, skipped." % f)
                continue
            ext = os.path.splitext(f)[1].lstrip(".")
            if not self.__is_supported_file(ext):
                print_warning("%s is not a supported file, skipped." % f)
                continue
            self.items.append(LayerItem(self.name, os.path.join(self.path, f)))

        # raise if no item in this layer
        if len(self.items) == 0:
            raise E(E.ERR_IO_NO_ITEM_IN_LAYER, self.name, self.path)

        print_info("new Layer: NO.%d %s %d items, %s" % (self.index, self.name, len(self.items), self.path))

    def __is_supported_file(self, ext: str) -> bool:
        return ext.lower() in SUPPORTED_INPUT_FORMAT

    def get_item(self) -> LayerItem:
        """
        we do not update the counter here because we are not sure if the combination will finally be counted
        :return:
        """
        selected = random.randrange(len(self.items))
        return self.items[selected]

    def print_stat(self):
        for it in self.items:
            it.print_stat()

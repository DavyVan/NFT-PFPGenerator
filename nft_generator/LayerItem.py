import os

from nft_generator.Printers import *

class LayerItem:

    def __init__(self, layer_name: str, path: str):
        """
        This function does not check the path or file extension.
        :param layer_name: The layer name of which this file belongs to.
        :param path: The full file path
        """
        self.layer_name = layer_name            # type: str
        self.__counter = 0                      # type: int # This is the count exclusively for this item, used for stat
        self.path = path                        # type: str

        _, basename = os.path.split(path)
        name, ext = os.path.splitext(basename)         # may have a period as the first character
        self.ext = ext.lstrip(".")              # type: str # remove the prefix period
        self.item_name = name                   # type: str

    def increase_counter(self):
        self.__counter += 1

    def get_counter(self) -> int:
        return self.__counter

    def print_stat(self):
        print_info("%s %d" % (self.path, self.__counter))

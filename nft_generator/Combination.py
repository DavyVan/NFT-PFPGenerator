import cv2 as cv
import os

from nft_generator.LayerItem import LayerItem
from nft_generator.kernels import img_merge


class Combination:

    def __init__(self):
        self.items = []         # type: list[LayerItem] # keep the same order as the layer numbers

    def add_item(self, item: LayerItem):
        self.items.append(item)

    def __hash__(self):
        s = ""
        for item in self.items:
            s += item.layer_name + item.item_name
        return hash(s)

    def __eq__(self, other):
        if len(self.items) != len(other.items):
            return False
        if len(self.items) == 0 and len(other.items) == 0:
            return True

        flag = True
        for i in range(len(self.items)):
            if self.items[i].layer_name != other.items[i].layer_name or self.items[i].item_name != other.items[i].item_name:
                flag = False
        return flag

    def commit(self):
        """
        Update the counters inside LayerItem
        :return:
        """
        for it in self.items:
            it.increase_counter()

    def render(self, output_path: str, output_no: int, output_format: str):
        output_img = None
        if len(self.items) == 0:
            raise ValueError("Combination: Empty combination")
        elif len(self.items) == 1:
            raise ValueError("Combination: Only one layer in the combination")
        else:
            output_img = img_merge(self.items[-1].path, self.items[-2].path)            # the layers must be numbered from top to bottom
            if len(self.items) > 2:
                for i in range(len(self.items)-1, -1, -1):
                    output_img = img_merge(output_img, self.items[i].path)

        # write to file
        full_path = os.path.join(output_path, str(output_no)) + "." + output_format
        cv.imwrite(full_path, output_img)

    def __generate_metadata_enjin(self, basename: str, description: str, no: int, output_format: str) -> dict:
        ret = dict()
        ret["name"] = "%s #%d" % (basename, no)
        ret["description"] = description
        ret["image"] = "%d.%s" % (no, output_format)
        props = dict()
        for it in self.items:
            props[it.layer_name] = it.item_name
        ret["properties"] = props
        return ret

    def __generate_metadata_opensea(self, basename: str, description: str, no: int, output_format: str) -> dict:
        ret = dict()
        ret["name"] = "%s #%d" % (basename, no)
        ret["description"] = description
        ret["image"] = "%d.%s" % (no, output_format)
        attrs = list()
        for it in self.items:
            attrs.append({"trait_type": it.layer_name, "value": it.item_name})
        ret["attributes"] = attrs
        return ret

    def generate_metadata(self, std: str, basename: str, description: str, no: int, output_format: str) -> dict:
        if std == "enjin":
            return self.__generate_metadata_enjin(basename, description, no, output_format)
        elif std == "opensea":
            return self.__generate_metadata_opensea(basename, description, no, output_format)
        else:
            raise NotImplementedError("Combination: metadata standard is not implemented.")
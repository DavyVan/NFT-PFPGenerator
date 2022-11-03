import os

from nft_generator.LayerItem import LayerItem
from nft_generator.kernels import img_merge, imwrite
from nft_generator.Config import Config
from nft_generator.Errors import NFTGError as E


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

    def render(self, output_no: int, config: Config):
        output_img = None
        if len(self.items) == 0:
            raise E(E.ERR_RT_EMPTY_COMB)
        elif len(self.items) == 1:
            raise E(E.ERR_RT_ONE_LAYER_COMB)
        else:
            size = (config.resource_size_w, config.resource_size_h)
            output_img = img_merge(self.items[-1].path, self.items[-2].path, size)            # the layers must be numbered from top to bottom
            if len(self.items) > 2:
                for i in range(len(self.items)-1, -1, -1):
                    output_img = img_merge(output_img, self.items[i].path, size)

        # write to file
        full_path = os.path.join(config.output_path, str(output_no)) + "." + config.output_format
        imwrite(full_path, output_img)

    def __generate_metadata_enjin(self, no: int, config: Config) -> dict:
        ret = dict()
        ret["name"] = "%s #%d" % (config.metadata_name, no)
        ret["description"] = ""
        ret["image"] = "%d.%s" % (no, config.output_format)
        props = dict()
        for it in self.items:
            props[it.layer_name] = it.item_name
        ret["properties"] = props
        return ret

    def __generate_metadata_opensea(self, no: int, config: Config) -> dict:
        ret = dict()
        ret["name"] = "%s #%d" % (config.metadata_name, no)
        ret["description"] = ""
        ret["image"] = "%d.%s" % (no, config.output_format)
        attrs = list()
        for it in self.items:
            attrs.append({"trait_type": it.layer_name, "value": it.item_name})
        ret["attributes"] = attrs
        return ret

    def generate_metadata(self, no: int, config: Config) -> dict:
        if config.metadata_standard == "enjin":
            return self.__generate_metadata_enjin(no, config)
        elif config.metadata_standard == "opensea":
            return self.__generate_metadata_opensea(no, config)
        else:
            raise E(E.ERR_IO_METADATA)
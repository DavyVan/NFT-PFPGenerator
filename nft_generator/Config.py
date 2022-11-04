import argparse
import os
import json

from nft_generator.Printers import *
from nft_generator.Constants import SUPPORTED_OUTPUT_FORMAT, SUPPORTED_METADATA_STD
from nft_generator.Errors import NFTGError


class Config:

    def __init__(self, jsonstr: str = None):
        self.path = ""                      # type: str
        self.count = 0                      # type: int
        self.output_format = ""             # type: str
        self.output_path = ""               # type: str
        self.subdir_sep = ""                # type: str
        self.metadata_standard = ""         # type: str
        self.metadata_name = ""             # type: str
        self.resource_size_w = 0            # type: int
        self.resource_size_h = 0            # type: int

        self.__parse_args(jsonstr)

    def __is_supported_output_format(self, ext: str) -> bool:
        return ext.lower() in SUPPORTED_OUTPUT_FORMAT

    def __parse_args(self, jsonstr: str = None):
        """
        Will use json if present.
        :param jsonstr: The JSON string.
        :return:
        """
        if jsonstr is None or jsonstr == "":
            parser = argparse.ArgumentParser()
            parser.add_argument("path",
                                help="The path of working directory where you store all the resource images. Use '\\\\' on Windows.",
                                type=str)
            parser.add_argument("count", help="The total number of NFTs you want to generate.", type=int)
            parser.add_argument("-of", "--output-format", help="The output format. Default: png", default="png", type=str)
            parser.add_argument("-o", "--output-path", help="The output path. Default: current working directory",
                                default=".", type=str)
            parser.add_argument("--sep", help="The separator of layer folders. Default: <space>", default=" ", type=str)
            parser.add_argument("-m", "--meta-std", help="The metadata standard e.g. enjin or opensea. Default: opensea",
                                default="opensea", type=str)
            parser.add_argument("-n", "--collection-name", help="The collection name.", default="Test-NFT", type=str)
            parser.add_argument("--size", help="The dimensions of resource pictures (in pixels).", type=int)
            parser.add_argument("--starting", help="The starting index, which means that the # of the first NFT shall be this number.", default=1, type=int)
            args = parser.parse_args()

            self.path = args.path  # will verify later
            self.count = args.count
            self.output_format = args.output_format
            self.output_path = args.output_path
            self.subdir_sep = args.sep
            self.metadata_standard = args.meta_std.lower()
            self.metadata_name = args.collection_name
            self.resource_size_w = args.size
            self.resource_size_h = self.resource_size_w
            self.starting_index = args.starting
        else:
            jsondict = json.loads(jsonstr)

            try:
                self.path = jsondict["path"]
            except KeyError:
                raise NFTGError(NFTGError.ERR_IO_PATH_NOT_GIVEN)

            try:
                self.count = jsondict["count"]
            except KeyError:
                raise NFTGError(NFTGError.ERR_IO_COUNT)

            try:
                self.resource_size_w = jsondict["resource-size"]
                self.resource_size_h = self.resource_size_w
            except KeyError:
                raise NFTGError(NFTGError.ERR_IO_RESOURCE_SIZE)

            try:
                self.output_format = jsondict["output-format"]
            except KeyError:
                self.output_format = "png"

            try:
                self.output_path = jsondict["output-path"]
            except KeyError:
                self.output_path = "."

            try:
                self.subdir_sep = jsondict["sep"]
            except KeyError:
                self.subdir_sep = " "

            try:
                self.metadata_standard = jsondict["meta-std"]
            except KeyError:
                self.metadata_standard = "opensea"

            try:
                self.metadata_name = jsondict["collection-name"]
            except KeyError:
                self.metadata_name = "Test-NFT"

            try:
                self.starting_index = jsondict["starting-index"]
            except KeyError:
                self.starting_index = 1

        # path
        print_info("Path: " + self.path)

        # count
        if self.count <= 0:
            raise NFTGError(NFTGError.ERR_IO_COUNT)
        print_info("Count: " + str(self.count))

        # output_format
        if not self.__is_supported_output_format(self.output_format):
            raise NFTGError(NFTGError.ERR_IO_OUTPUT_FORMAT)
        print_info("Output_format: " + str(self.output_format).upper())

        # output_path
        if self.output_path == ".":
            self.output_path = os.path.join(os.getcwd(), "output")
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)
        print_info("Output_path (created if not exists): " + self.output_path)

        # sep
        print_info("Layer folder separator: " + ("<space>" if self.subdir_sep == " " else self.subdir_sep))

        # metadata_standard
        print_info("Metadata Standard: " + self.metadata_standard)

        # metadata_name
        print_info("Collection Name: " + self.metadata_name)

        # resource size
        if self.resource_size_w <= 0 or self.resource_size_h <= 0:
            raise NFTGError(NFTGError.ERR_IO_RESOURCE_SIZE)
        print_info("Resource Size: " + str(self.resource_size_w) + "x" + str(self.resource_size_h))

        # starting index
        if self.starting_index <= 0:
            raise NFTGError(NFTGError.ERR_IO_STARTING)
        print_info("Starting Index: %d" % self.starting_index)

        print_ok_with_prefix("Parsing arguments...")

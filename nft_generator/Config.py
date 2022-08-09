import argparse
import os
import json

from nft_generator.Printers import *
from nft_generator.constants import SUPPORTED_OUTPUT_FORMAT, SUPPORTED_METADATA_STD


class Config:

    def __init__(self, jsonstr: str = None):
        self.path = ""                      # type: str
        self.count = 0                      # type: int
        self.output_format = ""             # type: str
        self.output_path = ""               # type: str
        self.subdir_sep = ""                # type: str
        self.metadata_standard = ""         # type: str
        self.metadata_name = ""             # type: str

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
            args = parser.parse_args()

            self.path = args.path  # will verify later
            self.count = args.count
            self.output_format = args.output_format
            self.output_path = args.output_path
            self.subdir_sep = args.sep
            self.metadata_standard = args.meta_std.lower()
            self.metadata_name = args.collection_name
        else:
            jsondict = json.loads(jsonstr)
            self.path = jsondict["path"]
            self.count = jsondict["count"]
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

        # path
        print_info("Path: " + self.path)

        # count
        if self.count <= 0:
            raise ValueError("Collection: count must be greater than zero.")
        print_info("Count: " + str(self.count))

        # output_format
        if not self.__is_supported_output_format(self.output_format):
            raise ValueError("Collection: output format " + self.output_format + " is not supported.")
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
        if self.metadata_standard not in SUPPORTED_METADATA_STD:
            raise ValueError("Collection: the metadata standard is not supported.")

        # metadata_name
        if self.metadata_name == "":
            raise ValueError("Collection: collection name cannot be empty.")

        print_ok_with_prefix("Parsing arguments...")

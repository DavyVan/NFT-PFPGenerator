import argparse
import os

from nft_generator.Printers import *
from nft_generator.constants import SUPPORTED_OUTPUT_FORMAT, SUPPORTED_METADATA_STD


class Config:

    def __init__(self):
        self.path = ""                      # type: str
        self.count = 0                      # type: int
        self.output_format = ""             # type: str
        self.output_path = ""               # type: str
        self.subdir_sep = ""                # type: str
        self.metadata_standard = ""         # type: str
        self.metadata_name = ""             # type: str

        self.__parse_args()


    def __is_supported_output_format(self, ext: str) -> bool:
        return ext.lower() in SUPPORTED_OUTPUT_FORMAT

    def __parse_args(self):
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

        self.metadata_standard = args.meta_std.lower()
        if self.metadata_standard not in SUPPORTED_METADATA_STD:
            raise ValueError("Collection: the metadata standard is not supported.")

        self.metadata_name = args.collection_name
        if self.metadata_name == "":
            raise ValueError("Collection: collection name cannot be empty.")

        print_ok_with_prefix("Parsing arguments...")
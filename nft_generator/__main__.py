import sys

import cv2 as cv
import numpy as np
import time
import argparse
import random


from nft_generator.kernels import *
from nft_generator.Printers import *
from nft_generator.Collection import Collection


def merge_images(combination: list[str], output_path: str, output_no: int, output_format: str):
    """
    倒序合成所有图层并存储至指定位置。
    :param combination:
    :param output_path:
    :param output_no: 文件编号
    :param output_format: 文件格式
    :return:
    """

    output_img = None

    if len(combination) == 0:
        raise ValueError("Empty combination")
    elif len(combination) == 1:
        raise ValueError("Only one layer in the combination")
    elif len(combination) >= 2:
        output_img = img_merge(combination[-1], combination[-2])
        if len(combination) > 2:
            for i in range(len(combination)-3, -1, -1):
                output_img = img_merge(output_img, combination[i])
    output_full_path = os.path.join(output_path, str(output_no)) + "." + output_format
    cv.imwrite(output_full_path, output_img)

def main():
    collection = Collection(sys.argv)

    collection.generate()

    start = time.time_ns() // 1000000
    # collection.render()
    end = time.time_ns() // 1000000
    print_info("Time spent: " + str(end-start) + "ms")
    print_ok_with_prefix("Rendered all images...")

    collection.print_stat()


if __name__ == "__main__":
    main()

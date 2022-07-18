import cv2 as cv
import numpy as np
import time
import argparse
import random


from nft_generator.kernels import *
from nft_generator.Printers import *


def init_argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path of working directory where you store all the resource images. Use '\\\\' on Windows.", type=str)
    parser.add_argument("count", help="The total number of NFTs you want to generate.", type=int)
    parser.add_argument("-of", "--output-format", help="The output format. Default: png", default="png", type=str)
    parser.add_argument("-o", "--output-path", help="The output path. Default: current working directory", default=".", type=str)
    return parser.parse_args()


def check_and_get_subdirs(path: str) -> list:
    """
    检查根目录存在，检查子目录都被编号而且按顺序，会自动排除掉没有按照规则命名的文件夹
    子目录命名规则：<数字编号，位数不限>.<其他内容>
    即编号和文件夹名中间用点分割。要求编号从1开始且必须连续不能有空缺。
    :param path:
    :return: 符合条件的子目录列表，按编号顺序排序，只包含子目录名称，使用时需要join
    """

    # check the root dir
    if not os.path.isdir(path):
        raise FileNotFoundError("The base directory does not exist.")

    # get all the entries, including files and subdirs
    entries = os.listdir(path)
    entry_numbers = []
    entry_selected = []
    for entry in entries:
        if not os.path.isdir(os.path.join(path, entry)):
            continue

        entry_number, _ = os.path.splitext(entry)
        # must be not null, an integer
        if entry_number != "" and entry_number.isnumeric():
            # add it to the list
            entry_numbers.append(int(entry_number))
            entry_selected.append(entry)
            # print_info("Found subdir: " + entry)

    if len(entry_numbers) == 0:
        raise FileNotFoundError("Did not find available folders.")

    # check the numbers are in sequence
    combined = sorted(list(zip(entry_numbers, entry_selected)))
    ret = []
    for i in range(len(combined)):     # i starts from zero
        ret.append(combined[i][1])
        if i+1 != combined[i][0]:
            raise ValueError("The numbers of subdirs are not in sequence")
    return ret


def is_supported_file(ext: str) -> bool:
    supported_exts = [".png"]
    return ext in supported_exts


def is_supported_output_format(ext: str) -> bool:
    supported_format = ["png"]
    return ext.lower() in supported_format


def generate_combination(base: str, subdirs: list[str], count: int) -> list[list[str]]:
    """
    遍历所有子目录中的所有图片文件（仅支持png）并随机在每个目录中抽取一个图层生成count个组合
    选取是采用放回式抽取法，均匀分布
    :param subdirs:
    :return: combinations[i][filecount] = filepath_full，有count个元素
    """

    # walk all the subdirs and extract all supported image files
    files = []          # type: list[list[str]] # files[subdirindex][fileindex] = filename
    file_stats = []     # type: list[list[int]] # file_stats[subdirindex][fileindex] = usage_count
    for i_subdir in range(len(subdirs)):
        _files = os.listdir(os.path.join(base, subdirs[i_subdir]))
        _files_selected = []
        for i_file in range(len(_files)):
            if not os.path.isfile(os.path.join(base, subdirs[i_subdir], _files[i_file])):
                continue        # skip entries that are not files
            ext = os.path.splitext(_files[i_file])[1]
            if is_supported_file(ext):
                _files_selected.append(_files[i_file])
        files.append(_files_selected)
        file_stats.append([0] * len(_files_selected))

    # generate combinations
    combinations = []           # type: list[list[str]] # combinations[i][filecount] = filepath_full
    combinations_set = {()}     # init with an empty tuple
    for c in range(count):
        combination = []
        combination_index = []
        combination_tuple = tuple(combination)
        while combination_tuple in combinations_set:
            combination = []
            combination_index = []
            # randomly choose an image from each subdir
            for i_subdir in range(len(files)):
                i_file_rand = random.randrange(len(files[i_subdir]))
                combination.append(os.path.join(base, subdirs[i_subdir], files[i_subdir][i_file_rand]))
                combination_index.append(i_file_rand)
            combination_tuple = tuple(combination)
        # found
        combinations.append(combination)
        combinations_set.add(combination_tuple)
        # update stat
        for i_subdir in range(len(combination_index)):
            file_stats[i_subdir][combination_index[i_subdir]] += 1

    print_ok_with_prefix("Generate combinations...")

    # output stat
    for i_subdir in range(len(files)):
        for i_file in range(len(files[i_subdir])):
            print_info(os.path.join(base, subdirs[i_subdir], files[i_subdir][i_file]) + ": " + str(file_stats[i_subdir][i_file]))

    # return
    return combinations


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
    # parse and verify args
    args = init_argparser()

    path = args.path
    print_info("Path: " + path)             # will verify later

    count = args.count
    if count > 0:
        print_info("Count: " + str(count))

    output_format = args.output_format
    if is_supported_output_format(output_format):
        print_info("Output_format: " + str(output_format).upper())

    output_path = args.output_path
    if output_path == ".":
        output_path = os.path.join(os.getcwd(), "output")
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    print_info("Output_path (created if not exists): " + output_path)

    print_ok_with_prefix("Parsing arguments...")

    subdirs = check_and_get_subdirs(path)
    print_ok_with_prefix("Checking folders...")

    combinations = generate_combination(path, subdirs, count)

    start = time.time_ns() // 1000000
    for i in range(len(combinations)):
        print_info("Processing..." + str(i+1))
        merge_images(combinations[i], output_path, i+1, output_format)
    end = time.time_ns() // 1000000
    print_info("Time spent: " + str(end-start) + "ms")
    print_ok_with_prefix("Generate all images...")


if __name__ == "__main__":
    main()

import cv2 as cv
from PIL import Image
import numpy as np


def check_and_add_alpha_channel_png(img: np.ndarray) -> np.ndarray:
    x, y, chs = img.shape
    if chs == 4:
        return img      # do nothing
    elif chs == 3:
        ch0, ch1, ch2 = cv.split(img)
        ch3 = np.full((x, y), 255, dtype=np.uint8)
        return cv.merge((ch0, ch1, ch2, ch3))


def imread_utf8_png(file: str) -> np.ndarray:
    """
    opencv底层库在简体中文Windows下工作异常，所以使用此方法
    :param file:
    :return:
    """
    img = cv.imdecode(np.fromfile(file, dtype=np.uint8), cv.IMREAD_UNCHANGED)
    return check_and_add_alpha_channel_png(img)


def imwrite_utf8(file: str, img: np.ndarray, _format: str) -> None:
    if _format == "png":
        imwrite_utf8_png(file, img)


def imwrite_utf8_png(file: str, img: np.ndarray) -> None:
    pil_img = Image.fromarray(img, "RGBA")
    pil_img.save(file)  # file path includes extension .png

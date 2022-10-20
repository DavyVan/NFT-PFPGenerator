from multipledispatch import dispatch
from PIL import Image

from nft_generator.Printers import *


@dispatch(str, str)
def img_merge(file_back: str, file_front: str) -> Image.Image:
    """
    用于png合成png的kernel，一次合成两个图层
    :param file_back:
    :param file_front:
    :return:
    """

    img_front = Image.open(file_front)
    __check_alpha_channel(img_front)
    img_back = Image.open(file_back)
    __check_alpha_channel(img_back)

    try:
        return img_merge(img_back, img_front)
    except ValueError as e:
        print_error("img_merge_kernel_png_png: ")
        print_error(str(e.args))
        print_error("file_back: " + file_back)
        print_error("file_front: " + file_front)
        print_aborted()


@dispatch(Image.Image, str)
def img_merge(file_back: Image.Image, file_front: str) -> Image.Image:
    """
    用于ndarray合成png的kernel，一次合成两个图层
    :param file_back: 已经读取的，或者刚刚处理生成的图片数据
    :param file_front: 图片路径
    :return:
    """

    img_front = Image.open(file_front)
    __check_alpha_channel(img_front)
    img_back = file_back

    try:
        return img_merge(img_back, img_front)
    except ValueError as e:
        print_error("img_merge_kernel_ndarray_png: ")
        print_error(str(e.args))
        print_error("file_front: " + file_front)
        print_aborted()


@dispatch(Image.Image, Image.Image)
def img_merge(file_back: Image.Image, file_front: Image.Image) -> Image.Image:
    """
    用于图片合成的kernel，一次合成两个图层
    :param file_back: 底层图片的数据
    :param file_front: 上层图片的数据
    :return:
    """
    img_front = file_front
    img_back = file_back

    # check dims
    if img_back.size != img_front.size:
        raise ValueError("Dimensions of back and front image do not match.", img_back.size, img_front.size)

    img_out = Image.alpha_composite(img_back, img_front)

    """
        ########### Medium performance (opencv + numpy) ##########
    """
    # front_ch0, front_ch1, front_ch2, front_ch3 = cv.split(img_front)
    # back_ch0, back_ch1, back_ch2, back_ch3 = cv.split(img_back)
    # _a = (255 - front_ch3) / 255
    # _b = 1 - _a
    # out_ch0 = back_ch0 * _a     # the matrix is now float64
    # out_ch1 = back_ch1 * _a
    # out_ch2 = back_ch2 * _a
    # out_ch0 += front_ch0 * _b
    # out_ch1 += front_ch1 * _b
    # out_ch2 += front_ch2 * _b
    # # cast from float64 to uint8
    # out_ch0 = np.rint(out_ch0).astype(np.uint8)
    # out_ch1 = np.rint(out_ch1).astype(np.uint8)
    # out_ch2 = np.rint(out_ch2).astype(np.uint8)
    # out_ch3 = np.fmax(back_ch3, front_ch3)
    # out_ch3 = np.rint(out_ch3).astype(np.uint8)
    # img_out = cv.merge((out_ch0, out_ch1, out_ch2, out_ch3))

    """
        ########### The worst performance ##########
    """
    # white = np.full((nrows, ncols, 3), 255, np.ubyte)
    # for r in range(nrows):
    #     for c in range(ncols):
    #         if img_back[r][c][3] == 255:
    #             white[r][c][0] = img_back[r][c][0]
    #             white[r][c][1] = img_back[r][c][1]
    #             white[r][c][2] = img_back[r][c][2]
    #
    #         else:
    #             white[r][c][0] = white[r][c][0] * (255-img_back[r][c][3])/255
    #             white[r][c][1] = white[r][c][1] * (255-img_back[r][c][3])/255
    #             white[r][c][2] = white[r][c][2] * (255-img_back[r][c][3])/255
    #             white[r][c][0] += img_back[r][c][0] * (img_back[r][c][3] / 255)
    #             white[r][c][1] += img_back[r][c][1] * (img_back[r][c][3] / 255)
    #             white[r][c][2] += img_back[r][c][2] * (img_back[r][c][3] / 255)

    return img_out


def __check_alpha_channel(img: Image.Image):
    bands = img.getbands()
    if bands == ("R", "G", "B"):
        img.putalpha(255)


def imwrite(path: str, img: Image.Image) -> None:
    img.save(path)
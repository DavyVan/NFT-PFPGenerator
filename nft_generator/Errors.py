from typing import Final
from multipledispatch import dispatch


class NFTGError(Exception):
    ERR_NONE = 0  # type: Final[int]

    # input/output check, starts from 100
    ERR_IO_RESOURCE_SIZE    = 101  # type: Final[int]
    ERR_IO_PATH_NOT_GIVEN   = 102  # type: Final[int]
    ERR_IO_COUNT            = 103  # type: Final[int]
    ERR_IO_OUTPUT_FORMAT    = 104  # type: Final[int]
    ERR_IO_SIZE_MATCH       = 105  # type: Final[int]
    ERR_IO_METADATA         = 106  # type: Final[int]
    ERR_IO_PATH_NOT_EXIST   = 107  # type: Final[int]
    ERR_IO_NO_AVAL_LAYER    = 108  # type: Final[int]
    ERR_IO_LAYER_SEQ        = 109  # type: Final[int]

    # runtime: render
    ERR_RT_EMPTY_COMB       = 201  # type: Final[int]
    ERR_RT_ONE_LAYER_COMB   = 202  # type: Final[int]
    ERR_RT_REND_TERM_EARLY  = 203  # type: Final[int]
    ERR_RT_REND_INT         = 204  # type: Final[int]

    ERR_MSG = {
        # 101
        ERR_IO_RESOURCE_SIZE:
            "请提供一个正整数作为素材大小",
        # 102
        ERR_IO_PATH_NOT_GIVEN:
            "请提供素材文件夹路径",
        # 103
        ERR_IO_COUNT:
            "请提供一个正整数作为生成数量",
        # 104
        ERR_IO_OUTPUT_FORMAT:
            "输出格式不支持",
        # 105
        ERR_IO_SIZE_MATCH:
            "图片大小不一致",
        # 106
        ERR_IO_METADATA:
            "Metadata 标准不支持",
        # 107
        ERR_IO_PATH_NOT_EXIST:
            "输入文件夹不存在",
        # 108
        ERR_IO_NO_AVAL_LAYER:
            "没有找到可用的图层文件夹，请检查命名",
        # 109
        ERR_IO_LAYER_SEQ:
            "图层文件夹没有按顺序整理",
        # 201
        ERR_RT_EMPTY_COMB:
            "存在不包含任何图层的组合",
        # 202
        ERR_RT_ONE_LAYER_COMB:
            "存在只包含一个图层的组合",
        # 203
        ERR_RT_REND_TERM_EARLY:
            "渲染进程提前结束",
        # 204
        ERR_RT_REND_INT:
            "渲染过程存在中断",
    }  # type: Final[dict[int, str]]

    @classmethod
    @dispatch(int)
    def errmsg(cls, code: int) -> str:
        try:
            return cls.ERR_MSG[code]
        except KeyError:
            return "N/A"

    @classmethod
    @dispatch(Exception)
    def errmsg(cls, e: Exception) -> str:
        if isinstance(e, cls):
            code, *args = e.args
            if len(args) == 0:
                return cls.errmsg(code)
            else:
                ret = cls.errmsg(code) + "("
                for it in args:
                    ret += str(it) + ", "
                ret += ")"
                return ret
        else:
            return str(e)

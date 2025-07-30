# -*- coding: UTF-8 -*-
"""ISO修改阶段常量字段"""

# 错误提示
ERR_MSG_DICT = {
    0: "获取ISO Volume id 失败",
    5: "ISO挂载失败",
    10: "COPY ISO挂载目录失败",
    15: "卸载挂载的ISO失败",
    20: "删除ISO内文件失败",
    25: "向ISO内新增/替换文件失败",
    30: "重做源失败",
    35: "重新生成ISO失败",
    40: "将MD5签入ISO失败",
    45: "获取ISO MD5失败",
    50: "生成MD5文件失败",
    55: "获取ISO文件大小失败",
    100: "修改成功"
}

XML_GZ_SUFFIX = ".xml.gz"  # xml.gz 文件后缀
REPODATA = "repodata"  # repodata目录
REPMOD = "repomd"  # repo源内的 repomd.xml
XML_SUFFIX = ".xml"  # .xml后缀


class ISOErrorEnum(object):
    """SeriesEnum(object)"""
    BASE_REPOCLOSURE = "Mash仓库依赖缺失"
    ISO_REPOCLOSURE = "ISO内仓库依赖缺失"
    ISO_ALL_REPOCLOSURE = "ISO内(Addons+)依赖缺失"
    ISO_LORAX_HAS_ERROR = "LORAX镜像有错误"

# -*- coding: UTF-8 -*-
"""
@File    ：log.py
"""
import os

from logzero import setup_logger, INFO, LogFormatter


def zero_log(log_name, log_file=None, level=INFO):
    """定义日志使用为默认使用zero的logger，为每个任务以及主要运行步骤单独生成_logger"""
    """按照logzero格式自定义logger并去除颜色提示"""
    if log_file and not os.path.isdir(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    fmt = '%(color)s[%(levelname)1.1s %(asctime)s %(filename)16s:%(lineno)3d]%(end_color)s %(message)s'
    return setup_logger(
        name=log_name, logfile=log_file, maxBytes=int(10e6), backupCount=15, level=level,
        formatter=LogFormatter(color=True, fmt=fmt))

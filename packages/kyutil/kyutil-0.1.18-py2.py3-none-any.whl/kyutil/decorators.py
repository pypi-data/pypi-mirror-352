# -*- coding: UTF-8 -*-
# 计算所用时间
import time


def timer(func):
    """
    :param func: 需要传入的函数
    :return:
    """

    def _warp(*args, **kwargs):
        """
        :param args: func需要的位置参数
        :param kwargs: func需要的关键字参数
        :return: 函数的执行结果
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        elastic_time = time.time() - start_time
        print("执行了 %.3fs\t方法：'%s' " % (elastic_time, func.__name__))
        return result

    return _warp

# -*- coding: UTF-8 -*-
class ServiceException(Exception):
    def __init__(self, message, code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BizAssert(Exception):
    def __init__(self, message, code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

    @staticmethod
    def has_value(obj, msg="数据不能为空", code=20001):
        if not obj:
            raise ServiceException(msg, code=code)

    @staticmethod
    def not_value(obj, msg="数据已存在", code=60008):
        if obj:
            raise ServiceException(msg, code=code)

    @staticmethod
    def not_none(obj, msg="数据不能为空", code=60008):
        if obj is not None:
            raise ServiceException(msg, code=code)

    @staticmethod
    def is_true(obj, msg="数据不能为假", code=60008):
        if obj is not True:
            raise ServiceException(msg, code=code)

    @staticmethod
    def csrf(csrf, msg="表单不允许重复提交", cache=None):
        if not csrf:
            raise ServiceException(msg, code=40010)
        if cache and cache.get(f'csrf_{csrf}'):
            raise ServiceException(msg, code=40010)

    @staticmethod
    def have_attr(attr, kwargs, msg="字段不能为空"):
        if not kwargs.get(attr, ''):
            raise ServiceException(attr + msg, code=60008)

    @staticmethod
    def is_digital(val, msg="不是数字"):
        try:
            float(val)
        except ValueError:
            raise ServiceException(msg, code=60008)

    @staticmethod
    def is_equal(val1, val2, msg="数值不相等"):
        if val1 != val2:
            raise ServiceException(msg, code=60008)


class BuildException(Exception):
    """this is user's Exception for bash error"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        print("Build过程出错了！Msg：" + str(self.msg))
        return self.msg


class MashException(Exception):
    """this is user's Exception for bash error"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        print("Mash过程出错了！Msg：" + str(self.msg or ""))
        return self.msg

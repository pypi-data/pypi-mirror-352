# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : exceptions.py
# @Time     : 2023/11/14 23:08


class FastapixException(Exception):
    def __init__(self, message: str, code: int = 501, *args, **kwargs):
        self.message = message
        self.code = code
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"

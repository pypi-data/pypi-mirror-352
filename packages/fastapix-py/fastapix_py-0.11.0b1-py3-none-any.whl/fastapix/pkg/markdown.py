# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : markdown.py
# @Time     : 2024/11/8 下午12:49
# @Desc     :

def str2markdown(text: str) -> str:
    return text.replace('\n', '\n\n')


def fold_contents(text: str, title: str = '展开') -> str:
    return f"<details><summary>{title}</summary>{text}</details>"

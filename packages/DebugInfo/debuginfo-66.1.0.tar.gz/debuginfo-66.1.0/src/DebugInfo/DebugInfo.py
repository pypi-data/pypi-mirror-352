# -*- coding:UTF-8 -*-
# Copyright DouYaoYuan GNU GENERAL PUBLIC LICENSE, see LICENSE file.

"""
@author: dyy
@contact: douyaoyuan@126.com
@time: 2023/8/8 9:57
@file: DebugInfo.py
@desc: 提供字符打印相关的操作方法，例如彩色文字，字符对齐，表格整理和输出，光标控制，语义日期, 搜索接口, 交互接口, 秒表装饰器 等
"""

# region 导入依赖项
import os as _os
import io as _io
import sys as _sys
import json as _json
import platform as _platform
import re as _re
import shutil as _shutil
import subprocess as _subprocess
from datetime import timedelta as _timedelta
from datetime import datetime as _datetime
from datetime import date as _date
import time as _time
from typing import Callable as _Callable
from functools import wraps as _wraps
from copy import copy as _copy
from copy import deepcopy as _deepcopy
import socket as _socket
import chardet as _chardet
from wcwidth import wcwidth as _wcwidth
import colorama as _colorama
from colorama import Fore as _Fore
from colorama import Back as _Back
import pyperclip as _pyperclip
import paramiko as _paramiko
import requests as _requests
import argparse as _argparse

# 改变标准输出的默认编码，以utf8为默认的输出编码格式
_sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding='utf8')

_colorama.init(autoreset=True)

# region 公共方法
def 显示宽度(内容: str, 特殊字符宽度字典: dict[str, float] = None) -> int:
    """
    去除颜色控制字符，根据库 wcwidth 判断每个字符的模式，判断其占用的空格数量
    :param 内容: 需要计算显示宽度的字符串
    :param 特殊字符宽度字典: 如果有特殊字符宽度计算不准确,可以明确指定其宽度
    :return: 给定内容的显示宽度值，即等效的英文空格的数量
    """
    if not 内容:
        return 0
    颜色控制字匹配模式: str = r'\033\[(?:\d+;)*\d*m'
    脱色内容: str = _re.sub(颜色控制字匹配模式, '', str(内容))
    总显示宽度: float = 0

    if not 特殊字符宽度字典:
        特殊字符宽度字典 = {}

    if 脱色内容:
        for 字 in 脱色内容:
            if 字 in 特殊字符宽度字典.keys():
                总显示宽度 += 特殊字符宽度字典[字]
            else:
                总显示宽度 += _wcwidth(字)

        if 总显示宽度 >= 0:
            return int(总显示宽度)
        else:
            return 0
    else:
        return 0


def 窗口宽度(修正值: int or _Callable = None) -> int:
    """
    返回当前终端窗口所能显示的英文空格字符的数量
    :return: os.get_terminal_size().columns
    """
    if callable(修正值):
        return _shutil.get_terminal_size().columns + 修正值()
    elif type(修正值) in [int, float]:
        return _shutil.get_terminal_size().columns + int(修正值)
    else:
        return _shutil.get_terminal_size().columns


def 窗口高度(修正值: int or _Callable = None) -> int:
    """
    返回当前终端窗口所能显示的行数量
    :return: os.get_terminal_size().lines
    """
    if callable(修正值):
        return _shutil.get_terminal_size().lines + 修正值()
    elif type(修正值) in [int, float]:
        return _shutil.get_terminal_size().lines + int(修正值)
    else:
        return _shutil.get_terminal_size().lines


def 打开(file,
         mode='r',
         buffering: int=None,
         encoding: str=None,
         errors: str=None,
         newline: str=None,
         closefd: bool=True,
         opener: _Callable[[str, int], int]=None):
    """
    重新包装了内置的 open 函数, 本函数会在 encoding 为 None 时,会通过 chardet 包来猜测文本编码,以增大文档打开成功的概率
    """

    # region 检测入参
    if not encoding:
        encoding = _chardet.detect(open(file, 'rb').read())['encoding']
        encoding = encoding if encoding else 'utf8'
    # endregion

    return open(file=file,
                mode=mode,
                buffering=-1 if buffering is None else buffering,
                encoding=encoding,
                errors=errors,
                newline=newline,
                closefd=closefd,
                opener=opener)

# region terminal 文本色彩控制
def __字体上色(字体颜色, *values) -> str or list or tuple:
    if len(values) == 1 and type(values[0]) in [list, tuple]:
        if isinstance(values[0], list):
            return [__字体上色(字体颜色, 元素) for 元素 in values[0]]
        elif isinstance(values[0], tuple):
            return tuple(__字体上色(字体颜色, 元素) for 元素 in values[0])

    合成临时字符串: str = (' '.join(str(itm) for itm in values)).strip()

    def 检查字符串首是否有字体控制字(字符串: str) -> bool:
        检查结果: bool = False

        # 匹配字符串首部的连续的所有字符控制字
        颜色控制字匹配模式: str = r'^(?:\033\[\d+m)+'
        匹配字符串 = _re.match(颜色控制字匹配模式, 字符串)
        if 匹配字符串:
            if r'[3' in str(匹配字符串.group(0)) or r'[9' in str(匹配字符串.group(0)):
                检查结果 = True

        return 检查结果

    if 合成临时字符串:
        # 如果字符串首部尚不存在字体颜色控制字,则在字符串首部补充一个字体颜色控制字
        if not 检查字符串首是否有字体控制字(合成临时字符串):
            合成临时字符串 = '{}{}'.format(字体颜色, 合成临时字符串)

        # 检查原字符串尾部结束符
        if 合成临时字符串.endswith(_Fore.RESET + _Back.RESET):
            合成临时字符串 = 合成临时字符串[:-len(_Back.RESET + _Fore.RESET)] + _Back.RESET
        elif 合成临时字符串.endswith(_Fore.RESET):
            合成临时字符串 = 合成临时字符串[:-len(_Fore.RESET)]

        # 将 _Fore.RESET 部位替换成要求的字体颜色, 并在末尾补充一个Fore.RESET
        合成临时字符串 = 合成临时字符串.replace(_Fore.RESET, 字体颜色) + _Fore.RESET
    else:
        合成临时字符串 = ''
    return 合成临时字符串


def __背景上色(背景颜色, *values) -> str or list or tuple:
    if len(values) == 1 and type(values[0]) in [list, tuple]:
        if isinstance(values[0], list):
            return [__背景上色(背景颜色, 元素) for 元素 in values[0]]
        elif isinstance(values[0], tuple):
            return tuple(__背景上色(背景颜色, 元素) for 元素 in values[0])

    合成临时字符串: str = (' '.join(str(itm) for itm in values)).strip()

    def 检查字符串首是否有背景控制字(字符串: str) -> bool:
        检查结果: bool = False

        # 匹配字符串首部的连续的所有字符控制字
        颜色控制字匹配模式: str = r'^(?:\033\[\d+m)+'
        匹配字符串 = _re.match(颜色控制字匹配模式, 字符串)
        if 匹配字符串:
            if r'[4' in str(匹配字符串.group(0)) or r'[10' in str(匹配字符串.group(0)):
                检查结果 = True

        return 检查结果

    if 合成临时字符串:
        # 如果字符串首部尚不存在背景颜色控制字,则在字符串首部补充一个背景颜色控制字
        if not 检查字符串首是否有背景控制字(合成临时字符串):
            合成临时字符串 = '{}{}'.format(背景颜色, 合成临时字符串)

        # 检查原字符串尾部结束符
        if 合成临时字符串.endswith(_Back.RESET + _Fore.RESET):
            合成临时字符串 = 合成临时字符串[:-len(_Back.RESET + _Fore.RESET)] + _Fore.RESET
        elif 合成临时字符串.endswith(_Back.RESET):
            合成临时字符串 = 合成临时字符串[:-len(_Back.RESET)]

        # 将 _Back.RESET 部位替换成要求的背景颜色, 并在末尾补充一个Back.RESET
        合成临时字符串 = 合成临时字符串.replace(_Back.RESET, 背景颜色) + _Back.RESET
    else:
        合成临时字符串 = ''

    return 合成临时字符串


def 红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, *values)


def 浅红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[91m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTRED_EX, *values)


def 红底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[41m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.RED, *values)


def 浅红底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[101m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTRED_EX, *values)


def 红底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.RED, *values))


def 红底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.RED, *values))


def 红底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.RED, *values))


def 红底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.RED, *values))


def 红底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.RED, *values))


def 红底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[41m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.RED, *values))


def 红底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[41m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.RED, *values))


def 绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, *values)


def 浅绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[92m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTGREEN_EX, *values)


def 绿底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[42m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.GREEN, *values)


def 浅绿底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[102m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTGREEN_EX, *values)


def 绿底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.GREEN, *values))


def 绿底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.GREEN, *values))


def 绿底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.GREEN, *values))


def 绿底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.GREEN, *values))


def 绿底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.GREEN, *values))


def 绿底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.GREEN, *values))


def 绿底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[42m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.GREEN, *values))


def 黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, *values)


def 浅黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[93m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTYELLOW_EX, *values)


def 黄底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[43m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.YELLOW, *values)


def 浅黄底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[103m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTYELLOW_EX, *values)


def 黄底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[42m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.YELLOW, *values))


def 黄底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[43m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.YELLOW, *values))


def 黄底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[43m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.YELLOW, *values))


def 黄底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[43m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.YELLOW, *values))


def 黄底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[43m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.YELLOW, *values))


def 黄底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[43m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.YELLOW, *values))


def 黄底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[43m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.YELLOW, *values))


def 蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, *values)


def 浅蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[94m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTBLUE_EX, *values)


def 蓝底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[44m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.BLUE, *values)


def 浅蓝底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[104m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTBLUE_EX, *values)


def 蓝底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.BLUE, *values))


def 蓝底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.BLUE, *values))


def 蓝底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.BLUE, *values))


def 蓝底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.BLUE, *values))


def 蓝底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.BLUE, *values))


def 蓝底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[44m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.BLUE, *values))


def 蓝底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[44m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.BLUE, *values))


def 洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, *values)


def 浅洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[95m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTMAGENTA_EX, *values)


def 洋红底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[45m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.MAGENTA, *values)


def 浅洋红底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[105m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTMAGENTA_EX, *values)


def 洋红底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.MAGENTA, *values))


def 洋红底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.MAGENTA, *values))


def 洋红底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.MAGENTA, *values))


def 洋红底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.MAGENTA, *values))


def 洋红底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.MAGENTA, *values))


def 洋红底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[45m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.MAGENTA, *values))


def 洋红底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[45m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.MAGENTA, *values))


def 青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, *values)


def 浅青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[96m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTCYAN_EX, *values)


def 青底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[46m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.CYAN, *values)


def 浅青底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[106m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTCYAN_EX, *values)


def 青底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.CYAN, *values))


def 青底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.CYAN, *values))


def 青底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.CYAN, *values))


def 青底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.CYAN, *values))


def 青底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.CYAN, *values))


def 青底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[46m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.CYAN, *values))


def 青底白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m\033[46m' + 字符串 + '\033[49m\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, __背景上色(_Back.CYAN, *values))


def 白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[37m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.WHITE, *values)


def 浅白字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[97m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTWHITE_EX, *values)


def 白底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[47m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.WHITE, *values)


def 浅白底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[107m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTWHITE_EX, *values)


def 白底黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, __背景上色(_Back.WHITE, *values))


def 白底红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[31m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.RED, __背景上色(_Back.WHITE, *values))


def 白底绿字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[32m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.GREEN, __背景上色(_Back.WHITE, *values))


def 白底黄字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[33m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.YELLOW, __背景上色(_Back.WHITE, *values))


def 白底蓝字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[34m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLUE, __背景上色(_Back.WHITE, *values))


def 白底洋红字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[35m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.MAGENTA, __背景上色(_Back.WHITE, *values))


def 白底青字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[36m\033\[47m' + 字符串 + '\033[49m\033[39' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.CYAN, __背景上色(_Back.WHITE, *values))


def 黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[30m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.BLACK, *values)


def 浅黑字(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[90m' + 字符串 + '\033[39m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __字体上色(_Fore.LIGHTBLACK_EX, *values)


def 黑底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[40m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.BLACK, *values)


def 浅黑底(*values) -> str:
    r"""
    将指定的字符串，修饰成 ’\033\[100m' + 字符串 + '\033[49m' 的格式
    :param values: 待修饰的字符串
    :return: 修饰后的字符串
    """
    return __背景上色(_Back.LIGHTBLACK_EX, *values)


# endregion


# region terminal 光标控制
def 光标上移(行数: int = 0) -> None:
    r"""
    print('\033[{}A'.format(行数 + 1))
    """
    if 行数 > 0:
        print('\033[{}A'.format(行数 + 1))


def 光标下移(行数: int = 0) -> None:
    r"""
    print('\033[{}B'.format(行数))
    """
    if 行数 > 0:
        print('\033[{}B'.format(行数))


def 光标右移(列数: int = 0) -> None:
    r"""
    print('\033[{}C'.format(列数))
    """
    if 列数 > 0:
        print('\033[{}C'.format(列数))


def 清屏() -> None:
    r"""
    print('\033[{}J'.format(2))
    """
    print('\033[{}J'.format(2))


def 设置光标位置(行号: int, 列号: int) -> None:
    r"""
    print('\033[{};{}H'.format(行号, 列号))
    """
    if 行号 >= 0 and 列号 >= 0:
        print('\033[{};{}H'.format(行号, 列号))


def 保存光标位置() -> None:
    r"""
    print('\033[s')
    """
    print('\033[s')


def 恢复光标位置() -> None:
    r"""
    print('\033[u')
    """
    print('\033[u')


def 隐藏光标() -> None:
    r"""
    print('\033[?25l')
    """
    print('\033[?25l')


def 显示光标() -> None:
    r"""
    print('\033[?25h')
    """
    print('\033[?25h')


# endregion


def 在nt系统中() -> bool:
    if _os.name == 'nt' or _platform.system() == 'Windows':
        return True
    return False


def 在posix系统中() -> bool:
    if _os.name == 'posix':
        return True
    return False


def 在mac系统中() -> bool:
    if _os.name == 'mac' or _platform.system() == 'Darwin':
        return True
    return False


def 本地路径格式化(路径: str, 分隔符: str = None) -> tuple[str, str]:
    """
    将指定的路径中的 ~/ 本地绝对路径, 并移除尾部的 / 和 \
    :param 路径: 指定需要处理的路径
    :param 分隔符: 可以指定路径的分隔符,路径格式化完成后,使用指定的分隔符替换本地路径分隔符
    :return: 返回扩展和格式化后的路径, 以及路径分隔符
    """
    路径分隔符: str = '/' if 在posix系统中() else '\\'
    非法路径分隔符: str = '\\' if 在posix系统中() else '/'

    路径 = str(路径 if 路径 else '').strip().replace(非法路径分隔符, 路径分隔符).replace('～', '~')
    if 路径 and 路径[0] == '~':
        if len(路径) == 1:
            路径 = f"{_os.path.expanduser('~')}"
        elif 路径[1] == 路径分隔符:
            路径 = f"{_os.path.expanduser('~')}{路径[1:]}"

    分隔符 = str(分隔符 if 分隔符 else '').strip()
    if 分隔符 in ['\\', '/']:
        路径 = 路径.replace(路径分隔符, 分隔符)
        路径分隔符 = 分隔符

    # 去除路径尾部的分隔符
    if 路径 != 路径分隔符:
        路径 = 路径.rstrip(路径分隔符)

    return 路径, 路径分隔符


def 复制文本(文本: str, 画板: '打印模板' = None) -> bool:
    画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
    画板.执行位置(复制文本)

    文本 = str('' if 文本 is None else 文本)

    复制成功: bool = True
    try:
        _pyperclip.copy(文本)
    except Exception as exp:
        复制成功 = False
        画板.消息(红字('文本复制失败!!!'))
        画板.消息(str(exp))
        if 在posix系统中():
            画板.消息(黄字('您当前在 linux/Unix 系统中, 推荐您安装 xclip 后再试(sudo apt-get install xclip)'))

    return 复制成功


# endregion


class 分隔线模板:
    """
    用于生成分隔线，您可以通过 分隔线模板.帮助文档() 来打印相关的帮助信息
    """

    def __init__(self,
                 符号: str = '-',
                 提示内容: str = None,
                 总长度: int = 50,
                 适应窗口: bool = False,
                 提示对齐: str = 'c',
                 特殊字符宽度字典: dict[str, float] = None,
                 修饰方法: _Callable[[str], str] or list[_Callable[[str], str]] = None,
                 打印方法: _Callable[[str], any] = print):
        self.__符号: str = '-'
        if 符号 is not None:
            self.__符号: str = str(符号)

        self.__提示内容: str = ''
        if 提示内容 is not None:
            self.__提示内容: str = 提示内容

        self.__总长度: int = 50
        if isinstance(总长度, int) and 总长度 > 0:
            self.__总长度 = 总长度

        self.__适应窗口: bool = True if 适应窗口 else False

        self.__提示对齐: str = 'c'
        if isinstance(提示对齐, str) and len(提示对齐 := 提示对齐.strip()) > 0:
            self.__提示对齐 = 提示对齐[0]

        self.__特殊字符宽度字典: dict[str, float] = {}
        if 特殊字符宽度字典:
            self.__特殊字符宽度字典 = _copy(特殊字符宽度字典)

        self.__修饰方法: _Callable[[str], str] or list[_Callable[[str], str]] = None
        self.修饰方法 = 修饰方法

        self.__打印方法: callable = None if not callable(打印方法) else 打印方法

    # region 访问器
    @property
    def 修饰方法(self) -> list[callable]:
        if callable(self.__修饰方法):
            return [self.__修饰方法]
        elif isinstance(self.__修饰方法, list):
            return _copy(self.__修饰方法)
        else:
            return []

    @修饰方法.setter
    def 修饰方法(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]]):
        if callable(方法):
            self.__修饰方法 = 方法
        elif isinstance(方法, list):
            可修饰: bool = True
            for 方子 in 方法:
                if not callable(方子):
                    可修饰 = False
                    break
            if 可修饰:
                self.__修饰方法 = _copy(方法)
            elif len(方法) < 1:
                self.__修饰方法 = None

    @property
    def 适应窗口(self) -> bool:
        return self.__适应窗口

    @property
    def 副本(self) -> '分隔线模板':
        """
        生成一个新的 分隔线模板 对象， 并将复制当前对像内的必要成员信息
        :return: 一个新的 分隔线模板 对象
        """
        副本: 分隔线模板 = 分隔线模板()

        副本.__符号 = self.__符号
        副本.__提示内容 = self.__提示内容
        副本.__总长度 = self.__总长度
        副本.__适应窗口 = self.__适应窗口
        副本.__提示对齐 = self.__提示对齐
        副本.修饰方法 = self.__修饰方法
        副本.__打印方法 = self.__打印方法

        副本.__特殊字符宽度字典 = _copy(self.__特殊字符宽度字典)

        return 副本

    # endregion

    def 符号(self, 符号: str = None) -> '分隔线模板':
        """
        设置分隔线的组成符号
        :param 符号: -, ~, * 都是常用的分隔线符号
        :return: self
        """
        if 符号 is None:
            self.__符号 = '-'
        else:
            self.__符号 = str(符号)
        return self

    def 提示内容(self, 提示: str = None) -> '分隔线模板':
        """
        设置分隔线的提示内容
        :param 提示: 提示内容
        :return: self
        """
        if 提示 is None:
            self.__提示内容 = ''
        else:
            self.__提示内容 = str(提示)
        return self

    def 总长度(self, 长度: int = 50, 适应窗口: bool = None) -> '分隔线模板':
        """
        设置分隔线的总长度，这个长度小于提示内容字符长度时，会显示提示内容，否则填充分隔线符号到指定长度
        :param 长度: 默认是 50
        :param 适应窗口: 指示是否将分隔线的长度限制在终端宽度以内
        :return: self
        """
        if not str(长度).isdigit():
            self.__总长度 = 50
        else:
            长度 = int(长度)
            if 长度 > 0:
                self.__总长度 = 长度
            else:
                self.__总长度 = 50

        if 适应窗口 is not None:
            self.__适应窗口 = True if 适应窗口 else False

        return self

    def 文本对齐(self, 方式: str = None) -> '分隔线模板':
        """
        分隔线提示内容的位置，支持左对齐，居中对齐，右对齐
        :param 方式: l, c, r
        :return: self
        """
        if 方式 := str(方式).strip().lower():
            self.__提示对齐 = 方式[0]
        else:
            self.__提示对齐 = 'c'
        return self

    def 修饰(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]]) -> '分隔线模板':
        """
        传入一个方法，或者方法list，依次对分隔线进行修饰，例如颜色修饰方法，或者 toUpper， toLower 之类的方法
        :param 方法: 接收一个字符串入参，返回一个字符传结果
        :return:self
        """
        self.修饰方法 = 方法
        return self

    def 指定特殊字符宽度字典(self, 特殊字符宽度字典: dict[str, float] = None) -> '分隔线模板':
        """
        指定一个 dict[str, int] 对象,用于定义特殊字符的显示宽度, 即等效的英文空格数量
        :param 特殊字符宽度字典: dict[str, float] 对象
        :return: self
        """
        self.__特殊字符宽度字典 = {}
        if 特殊字符宽度字典:
            self.__特殊字符宽度字典 = _copy(特殊字符宽度字典)
        return self

    def 展示(self, 打印方法: _Callable[[str], None] = None) -> None:
        """
        以指定的打印方法打印分隔符字符串，如果不指定打印方法，则使用内容打印方法，默认为 print 方法
        :param 打印方法: 接收 str 参数，不关心返回值
        :return: None
        """
        if callable(打印方法):
            self.__打印方法 = 打印方法

        if callable(self.__打印方法):
            self.__打印方法(self.__str__().rstrip())
        else:
            print(self.__str__().rstrip())

    @staticmethod
    def 帮助文档(打印方法: _Callable[[str], None] = None) -> None:
        画板: 打印模板 = 打印模板()

        if not callable(打印方法):
            画板.添加一行('分隔线模板用于生成分隔线', '|')
            画板.添加一行('符号: 分隔线中除提示内容外的填充符号, -, ~, * 都是常用的符号', '|')
            画板.添加一行('提示内容: 分隔线中用于提供参数信息的文本,可以为空', '|')
            画板.添加一行('下面是参考线的结构示例:', '|')
            画板.添加一行(青字('┌---分隔线符号----|<-这是提示内容->|<--分隔线符号----┐'), '|')
            画板.添加一行(红字('-' * 18 + '这是一个分隔线示例' + '-*-' * 6), '|')
            画板.添加一行(红字('~ ' * 9 + '这是一个分隔线示例' + ' *' * 9), '|')
            画板.添加一行('分隔线可以控制 【总长度】， 【提示内容】，【修饰方法】，【打印方法】，以支持个性化定制', '|')
            画板.添加一行('模板已经重定义 __str__ 方法，生成分隔线字符串', '|')

            画板.分隔线.符号('=').提示内容('╗').文本对齐('r').总长度(画板.表格宽度()).修饰(黄字).展示()
            画板.展示表格()
            画板.分隔线.符号('=').提示内容('╝').文本对齐('r').总长度(画板.表格宽度()).展示()
        else:
            画板.添加一行('分隔线模板用于生成分隔线')
            画板.添加一行('符号: 分隔线中除提示内容外的填充符号, -, ~, * 都是常用的符号')
            画板.添加一行('提示内容: 分隔线中用于提供参数信息的文本,可以为空')
            画板.添加一行('下面是参考线的结构示例:')
            画板.添加一行(青字('┌---分隔线符号----|<-这是提示内容->|<--分隔线符号----┐'))
            画板.添加一行(红字('-' * 18 + '这是一个分隔线示例' + '-*-' * 6))
            画板.添加一行(红字('~ ' * 9 + '这是一个分隔线示例' + ' *' * 9))
            画板.添加一行('分隔线可以控制 【总长度】， 【提示内容】，【修饰方法】，【打印方法】，以支持个性化定制')
            画板.添加一行('模板已经重定义 __str__ 方法，生成分隔线字符串')

            画板.展示表格(打印方法=打印方法)

    def __str__(self) -> str:
        分隔线字符串: str
        分隔线字符串可用长度: int = self.__总长度
        if self.__适应窗口:
            # -2 的作用是为了在行尾穿出位置处理换行符,避免行间粘连问题
            窗口宽度值: int = 窗口宽度() - 2
            if 窗口宽度值 > 0:
                分隔线字符串可用长度 = min(self.__总长度, 窗口宽度值)
        分隔线字符串可用长度 = 分隔线字符串可用长度 if 分隔线字符串可用长度 > 0 else 50

        if not self.__符号 or 显示宽度(self.__符号, self.__特殊字符宽度字典) < 1:
            self.__符号 = '-'

        提示文本: str = ''
        if self.__提示内容:
            提示文本 = str(self.__提示内容).strip()

        提示文本显示宽度: int = 显示宽度(提示文本, self.__特殊字符宽度字典)
        符号显示宽度: int = 显示宽度(self.__符号, self.__特殊字符宽度字典)

        修饰符重复次数计算: float = max((分隔线字符串可用长度 - 提示文本显示宽度) / 符号显示宽度, 0)
        修饰符重复次数整部: int = 修饰符重复次数计算.__floor__()

        if self.__提示对齐 in 'lr' or 提示文本显示宽度 < 1:
            # 左对齐或者右对齐, 或者提示文本宽度为零场景下, 计算符号填充序列
            符号序列: str = self.__符号 * 修饰符重复次数整部
            if 修饰符重复次数计算 > 修饰符重复次数整部:
                for 符 in self.__符号:
                    符号序列 = f'{符号序列}{符}'
                    if 显示宽度(符号序列, self.__特殊字符宽度字典) + 提示文本显示宽度 >= 分隔线字符串可用长度:
                        break

            if 提示文本显示宽度 < 1:
                分隔线字符串 = f'{符号序列}'
            elif self.__提示对齐 == 'l':
                分隔线字符串 = f'{提示文本}{符号序列}'
            else:
                分隔线字符串 = f'{符号序列}{提示文本}'
        else:
            # 居中对齐场景
            左边修饰符: str = ''
            右边修饰符: str = ''
            if 修饰符重复次数计算 * 0.5 >= (修饰符重复次数计算 * 0.5).__floor__() + 0.5:
                # 该情况下, 左侧修饰符序列使用ceil 取整
                左边修饰符 = self.__符号 * (修饰符重复次数计算 * 0.5).__ceil__()
            elif 修饰符重复次数计算 >= 修饰符重复次数整部:
                # 该情况下, 左侧修饰符序列使用 floor 取整
                左边修饰符 = self.__符号 * (修饰符重复次数计算 * 0.5).__floor__()

            分隔线字符串 = f'{左边修饰符}{提示文本}'

            分隔线字符串显示宽度: int = 显示宽度(分隔线字符串, self.__特殊字符宽度字典)

            if 分隔线字符串显示宽度 < 分隔线字符串可用长度:
                右侧修饰符重复次数计算: float = max((分隔线字符串可用长度 - 分隔线字符串显示宽度) / 符号显示宽度, 0)
                右侧修饰符重复次数整部: int = 右侧修饰符重复次数计算.__floor__()

                右边修饰符 = self.__符号 * 右侧修饰符重复次数整部
                if 右侧修饰符重复次数计算 > 右侧修饰符重复次数整部:
                    for 符 in self.__符号:
                        右边修饰符 = f'{右边修饰符}{符}'
                        if 显示宽度(右边修饰符, self.__特殊字符宽度字典) + 分隔线字符串显示宽度 >= 分隔线字符串可用长度:
                            break

            右边修饰符修正: list[str] = []
            if 右边修饰符:
                if 右边修饰符:
                    # 右边修饰符需要做方向转换, 例如 > 转为 <
                    右边修饰符 = ''.join(reversed(右边修饰符))

                    def 镜像字符(字: str) -> str:
                        镜像字典: dict = {None: None, '<': '>', '>': '<', '/': '\\', '\\': '/',
                                          '(': ')', ')': '(',
                                          '《': '》', '》': '《', '«': '»', '»': '«',
                                          '〈': '〉', '‹': '›', '⟨': '⟩', '〉': '〈',
                                          '›': '‹', '⟩': '⟨', '（': '）', '）': '（',
                                          '↗': '↖', '↖': '↗', '↙': '↘', '↘': '↙', 'd': 'b',
                                          'b': 'd',
                                          '⇐': '⇒', '⇒': '⇐'}

                        if 字 and 字 in 镜像字典:
                            return 镜像字典[字]
                        else:
                            return 字

                    for 字符 in 右边修饰符:
                        右边修饰符修正.append(镜像字符(字符))

            if 右边修饰符修正:
                分隔线字符串 = f"{分隔线字符串}{''.join(右边修饰符修正)}"

        if not 分隔线字符串:
            分隔线字符串 = 提示文本

        修饰方法表: list[_Callable[[str], str]] = self.修饰方法
        if 修饰方法表:
            for 方法 in 修饰方法表:
                分隔线字符串 = 方法(分隔线字符串)

        return 分隔线字符串


class 语义日期模板:
    __数字小写字典: list = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    """
    用于生成语义日期，您可以通过 主义日期模板.帮助文档() 来打印相关的帮助信息
    """

    def __init__(self,
                 目标日期: _datetime or _date = _datetime.now(),
                 上下午语义: bool = False,
                 周序语义: bool = True,
                 打印方法: _Callable[[str], any] = print):
        self.__目标日期: _datetime
        if isinstance(目标日期, _datetime):
            self.__目标日期 = 目标日期
        elif isinstance(目标日期, _date):
            self.__目标日期 = _datetime(year=目标日期.year,
                                        month=目标日期.month,
                                        day=目标日期.day,
                                        hour=0,
                                        minute=0,
                                        second=0)
        else:
            self.__目标日期 = _datetime.now()

        self.__上下午语义: bool = True if 上下午语义 else False
        self.__周序语义: bool = True if 周序语义 else False
        self.__打印方法: _Callable[[str], any] = print if not callable(打印方法) else 打印方法

    # region 访问器
    @property
    def 上下午语义状态(self) -> bool:
        return True if self.__上下午语义 else False

    @property
    def 周序语义状态(self) -> bool:
        return True if self.__周序语义 else False

    @property
    def 目标日期周序值(self) -> str:
        周序值: int = self.__目标日期.weekday()
        周序小写: str = self.__数字小写字典[(周序值 % 7) + 1]
        if '七' == 周序小写:
            周序小写 = '日'
        return f'周{周序小写}'

    @property
    def 目标日期上下午(self) -> str:
        小时: int = self.__目标日期.time().hour
        if 0 <= 小时 < 6:
            return '凌晨'
        elif 6 <= 小时 < 9:
            return '早上'
        elif 9 <= 小时 < 11:
            return '上午'
        elif 11 <= 小时 < 13:
            return '中午'
        elif 13 <= 小时 < 18:
            return '下午'
        elif 18 <= 小时 < 20:
            return '傍晚'
        elif 20 <= 小时 <= 23:
            return '深夜'
        else:
            return ''

    @property
    def 偏离天数(self) -> int:
        """
        目标日期距离 today() 的天数
        :return: 天数
        """
        return (self.__目标日期.date() - _datetime.now().date()).days

    @property
    def 偏离周数(self) -> int:
        """
        目标日期距离 today() 的周数
        :return: 周数
        """
        目标日期对齐到周一: _datetime = self.__目标日期 + _timedelta(days=1 - self.__目标日期.isoweekday())
        基准日期对齐到周一: _datetime = _datetime.now() + _timedelta(days=1 - _datetime.now().isoweekday())
        对齐到周一的日期偏离天数: int = (目标日期对齐到周一.date() - 基准日期对齐到周一.date()).days
        return (对齐到周一的日期偏离天数 / 7).__floor__()

    @property
    def 偏离月数(self) -> int:
        """
        目标日期距离 today() 的月数
        :return: 月数
        """
        return (self.__目标日期.year - _datetime.now().year) * 12 + self.__目标日期.month - _datetime.now().month

    @property
    def 偏离年数(self) -> int:
        """
        目标日期距离 today() 的年
        :return:
        """
        return self.__目标日期.year - _datetime.now().year

    @property
    def 时间语义(self) -> str:
        目标日期时间戳: float = self.__目标日期.timestamp()
        当前时间时间戳: float = _datetime.now().timestamp()
        时间戳秒差: float = 目标日期时间戳 - 当前时间时间戳

        if 时间戳秒差 > 7200:
            return ''  # 如果目标日期在当前时间2h后,则不考虑时间语义
        elif 时间戳秒差 > 3600:
            return '1小时后'
        elif 时间戳秒差 > 1800:
            return '半小时后'
        elif 时间戳秒差 > 900:
            return '稍后'
        elif 时间戳秒差 > 0:
            return '马上'
        elif 时间戳秒差 > -1800:
            return '刚才'
        elif 时间戳秒差 > -3600:
            return '半小时前'
        elif 时间戳秒差 > -7200:
            return '1小时前'
        else:
            return ''

    @property
    def 语义(self) -> str:
        return self.__str__()

    @property
    def 目标日期(self) -> _datetime:
        return self.__目标日期

    @目标日期.setter
    def 目标日期(self, 日期: _datetime or _date):
        if isinstance(日期, _datetime):
            self.__目标日期 = 日期
        elif isinstance(日期, _date):
            self.__目标日期 = _datetime(year=日期.year,
                                        month=日期.month,
                                        day=日期.day,
                                        hour=0,
                                        minute=0,
                                        second=0)

    @property
    def 副本(self) -> '语义日期模板':
        return 语义日期模板(self.__目标日期, self.__上下午语义, self.__周序语义, self.__打印方法)

    # endregion

    def 体现上下午语义(self) -> '语义日期模板':
        self.__上下午语义 = True
        return self

    def 禁用上下午语义(self) -> '语义日期模板':
        self.__上下午语义 = False
        return self

    def 体现周序(self) -> '语义日期模板':
        self.__周序语义 = True
        return self

    def 禁用周序(self) -> '语义日期模板':
        self.__周序语义 = False
        return self

    def 设置目标日期(self, 日期: _datetime or _date = _datetime.now()) -> '语义日期模板':
        """
        设置语义日期的目标日期
        :param 日期: 目标日期， datetime 对象
        :return: self
        """
        self.目标日期 = 日期
        return self

    def 展示(self, 打印方法: _Callable[[str], None] = None):
        """
        展示语义日期
        :param 打印方法: 可以指定打印语义日期的方法，黰是 print
        :return: None
        """
        if callable(打印方法):
            打印方法(self.__str__())
        elif callable(self.__打印方法):
            self.__打印方法(self.__str__())
        else:
            print(self.__str__())

    @staticmethod
    def 帮助文档(打印方法: _Callable[[str], None] = None) -> None:
        画板: 打印模板 = 打印模板()

        if not callable(打印方法):
            画板.添加一行('语义日期模板用于生成指定日期的语义日期', '|')
            画板.添加一行('目标日期: 进行语义解析的目标日期，_datetime.date 对象', '|')
            画板.添加一行('模板已经重定义 __str__ 方法，生成语义日期字符串', '|')

            画板.分隔线.符号('=').提示内容('╗').文本对齐('r').总长度(画板.表格宽度()).修饰(黄字).展示()
            画板.展示表格()
            画板.分隔线.符号('=').提示内容('╝').文本对齐('r').总长度(画板.表格宽度()).展示()
        else:

            画板.添加一行('语义日期模板用于生成指定日期的语义日期')
            画板.添加一行('目标日期: 进行语义解析的目标日期，_datetime.date 对象')
            画板.添加一行('模板已经重定义 __str__ 方法，生成语义日期字符串')

            画板.展示表格(打印方法=打印方法)

    def __str__(self) -> str:
        语义: str = ''

        天数 = self.偏离天数
        周数 = self.偏离周数
        月数 = self.偏离月数
        年数 = self.偏离年数

        时间语义: str = self.时间语义 if self.__上下午语义 else ''
        上下午语义: str = self.目标日期上下午 if self.__上下午语义 else ''
        上下午语义 = f'[{上下午语义}]' if 上下午语义 else ''
        周序: str = self.目标日期周序值

        if 时间语义:
            语义 = 时间语义
        elif 天数 == -3:
            语义 = f'大前天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == -2:
            语义 = f'前天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == 0:
            语义 = f'今天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == -1:
            语义 = f'昨天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == 1:
            语义 = f'明天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == 2:
            语义 = f'后天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 天数 == 3:
            语义 = f'大后天'
            if self.__周序语义:
                语义 = f'{语义}({周序})'
            语义 = f'{语义}{上下午语义}'
        elif 周数 == -2:
            语义 = '上上周'
            if self.__周序语义:
                语义 = f'{语义}{周序[-1]}'
        elif 周数 == -1:
            语义 = '上周'
            if self.__周序语义:
                语义 = f'{语义}{周序[-1]}'
        elif 周数 == 1:
            语义 = '下周'
            if self.__周序语义:
                语义 = f'{语义}{周序[-1]}'
        elif 周数 == 2:
            语义 = '下下周'
            if self.__周序语义:
                语义 = f'{语义}{周序[-1]}'
        elif 月数 == -2:
            语义 = '上上月'
        elif 月数 == -1:
            语义 = '上月'
        elif 月数 == 1:
            语义 = '下月'
        elif 月数 == 2:
            语义 = '下下月'
        elif 年数 == -3:
            语义 = '大前年'
        elif 年数 == -2:
            语义 = '前年'
        elif 年数 == -1:
            语义 = '去年'
        elif 年数 == 1:
            语义 = '明年'
        elif 年数 == 2:
            语义 = '后年'
        elif 年数 == 3:
            语义 = '大后年'
        elif 年数 != 0:
            语义 = f'{年数.__abs__()}年{"前" if 年数 < 0 else "后"}'
        elif 月数 != 0:
            语义 = f'{月数.__abs__()}个月{"前" if 月数 < 0 else "后"}'
        elif 周数 != 0:
            语义 = f'{周数.__abs__()}周{"前" if 周数 < 0 else "后"}'
        elif 天数 != 0:
            语义 = f'{天数.__abs__()}天{"前" if 天数 < 0 else "后"}'
            if self.__周序语义:
                语义 = f'{语义}({周序})'

        return 语义


class 打印模板:
    """
    用于生成 打印模板 对像，您可以通过 打印模板.帮助文档() 来打印相关的帮助信息
    """

    def __init__(self,
                 调试状态: bool = False,
                 缩进字符: str = None,
                 打印头: str = None,
                 位置提示符: str = None,
                 特殊字符宽度字典: dict[str, float] = None,
                 表格列间距: list[int] or int = None,
                 打印方法: callable = print):
        self.__调试状态: bool = 调试状态
        self.__缩进字符: str = '' if 缩进字符 is None else 缩进字符
        self.__打印头: str = '|-' if 打印头 is None else 打印头
        self.__位置提示符: str = '->' if 位置提示符 is None else 位置提示符

        self.__表格: list[list or callable] = []
        self.__表格列对齐: list[str] = []
        self.__表格宽度: int = -1
        self.__表格列宽: list[int] = []
        self.__表格列宽控制表: list[int] or int = 0

        self.__特殊字符宽度字典: dict[str, float] = {}
        self.特殊字符宽度字典 = 特殊字符宽度字典

        self.__表格列间距: list[int] or int = 2
        self.表格列间距 = 表格列间距

        self.__打印方法 = print if not callable(打印方法) else 打印方法

    # region 访问器
    @property
    def 调试状态(self) -> bool:
        return self.正在调试

    @调试状态.setter
    def 调试状态(self, 状态: bool):
        self.__调试状态 = True if 状态 else False

    @property
    def 正在调试(self) -> bool:
        return True if self.__调试状态 else False

    @property
    def 缩进字符(self) -> str:
        return self.__缩进字符

    @缩进字符.setter
    def 缩进字符(self, 符号: str = None) -> None:
        if 符号 is None:
            self.__缩进字符 = ''
        else:
            self.__缩进字符 = str(符号)

    @property
    def 打印头(self) -> str:
        return self.__打印头

    @打印头.setter
    def 打印头(self, 符号: str = None) -> None:
        if 符号 is None:
            self.__打印头 = ''
        else:
            self.__打印头 = str(符号)

    @property
    def 位置提示符(self) -> str:
        return self.__位置提示符

    @位置提示符.setter
    def 位置提示符(self, 符号: str = None) -> None:
        """
        设置模板的执行位置消息的提示符
        :param 符号: *, >, ->
        :return:  None
        """
        if 符号 is None:
            self.__位置提示符 = ''
        else:
            self.__位置提示符 = str(符号)

    @property
    def 特殊字符宽度字典(self) -> dict[str, float]:
        return _copy(self.__特殊字符宽度字典)

    @特殊字符宽度字典.setter
    def 特殊字符宽度字典(self, 字典: dict[str, float]) -> None:
        if isinstance(字典, dict):
            self.__特殊字符宽度字典 = _copy(字典)
        else:
            self.__特殊字符宽度字典 = {}

    @property
    def 表格行数(self) -> int:
        if not self.__表格:
            return 0
        else:
            return len(self.__表格)

    @property
    def 表格列数(self) -> int:
        if not self.__表格:
            return 0
        else:
            return max(1, max([len(行) for 行 in self.__表格 if type(行) in [list, tuple]]))

    @property
    def 表格列间距(self) -> list[int]:
        if isinstance(self.__表格列间距, int):
            return [self.__表格列间距]
        elif isinstance(self.__表格列间距, list):
            return _copy(self.__表格列间距)
        else:
            return [2]

    @表格列间距.setter
    def 表格列间距(self, 列间距: list[int] or int):
        if isinstance(列间距, int) and 列间距 >= 0:
            self.__表格列间距 = 列间距
        elif isinstance(列间距, list):
            self.__表格列间距 = []
            for 间距 in 列间距:
                if isinstance(间距, int) and 间距 >= 0:
                    self.__表格列间距.append(间距)
                else:
                    self.__表格列间距.append(2)

        # 复位表格宽度值
        self.__表格宽度 = -1

        # 复位 表格宽度值
        self.__表格列宽 = []

    @property
    def 表格列宽(self) -> list[int]:
        if self.__表格列宽:
            return self.__表格列宽

        # 展开的表格
        展开的表格: list[list[str] or callable]
        # 表格各列显示宽度表
        各列显示宽度表: list[int]

        展开的表格, 各列显示宽度表 = self.__表格各列显示宽度表()

        self.__表格列宽 = 各列显示宽度表

        return self.__表格列宽

    @表格列宽.setter
    def 表格列宽(self, 表格列宽: list[int] or int):
        if isinstance(表格列宽, int):
            self.__表格列宽控制表 = 表格列宽
        elif isinstance(表格列宽, list):
            self.__表格列宽控制表 = []
            for 列宽 in 表格列宽:
                if isinstance(列宽, int) and 列宽 >= 0:
                    self.__表格列宽控制表.append(列宽)
                else:
                    self.__表格列宽控制表.append(0)

        # 复位表格宽度值
        self.__表格宽度 = -1

        # 复位 表格宽度值
        self.__表格列宽 = []

    @property
    def 表格列表(self) -> list[list[str]]:
        if not self.__表格:
            return []
        else:
            return _deepcopy(self.__表格)

    @property
    def 分隔线(self) -> 分隔线模板:
        新建分隔线: 分隔线模板 = 分隔线模板(特殊字符宽度字典=self.__特殊字符宽度字典)

        # 定义一个方法,用于分隔线的展示打印
        def 打印方法(消息: str):
            消息 = 消息 if 消息 else ''
            消息显示宽度: int = 显示宽度(内容=消息, 特殊字符宽度字典=self.__特殊字符宽度字典)
            if 新建分隔线.适应窗口:
                窗口宽度值: int = 窗口宽度()
                if 窗口宽度值 > 0:
                    可用宽度 = 窗口宽度值 - 显示宽度(f'{self.__缩进字符}{self.__打印头}',
                                                     特殊字符宽度字典=self.__特殊字符宽度字典)
                    if len(self.__缩进字符) > 1:
                        可用宽度 -= min(len(self.__缩进字符), 5)
                    elif len(f'{self.__缩进字符}{self.__打印头}') > 1:
                        可用宽度 -= min(len(f'{self.__缩进字符}{self.__打印头}'), 5)
                    else:
                        可用宽度 -= 2

                    if 消息显示宽度 > 可用宽度:
                        self.消息(新建分隔线.总长度(长度=可用宽度))
                    else:
                        self.消息(消息)
                else:
                    self.消息(消息)
            else:
                self.消息(消息)

        新建分隔线._分隔线模板__打印方法 = 打印方法

        return 新建分隔线

    @property
    def 调试分隔线(self) -> 分隔线模板:
        新建分隔线: 分隔线模板 = 分隔线模板(特殊字符宽度字典=self.__特殊字符宽度字典)

        # 定义一个方法,用于分隔线的展示打印
        def 打印方法(消息: str):
            if self.__调试状态:
                消息 = 消息 if 消息 else ''
                消息显示宽度: int = 显示宽度(内容=消息, 特殊字符宽度字典=self.__特殊字符宽度字典)
                if 新建分隔线.适应窗口:
                    窗口宽度值: int = 窗口宽度()
                    if 窗口宽度值 > 0:
                        可用宽度 = 窗口宽度值 - 显示宽度(f'{self.__缩进字符}{self.__打印头}',
                                                         特殊字符宽度字典=self.__特殊字符宽度字典)
                        if len(self.__缩进字符) > 1:
                            可用宽度 -= min(len(self.__缩进字符), 5)
                        elif len(f'{self.__缩进字符}{self.__打印头}') > 1:
                            可用宽度 -= min(len(f'{self.__缩进字符}{self.__打印头}'), 5)
                        else:
                            可用宽度 -= 2

                        if 消息显示宽度 > 可用宽度:
                            self.调试消息(新建分隔线.总长度(长度=可用宽度))
                        else:
                            self.调试消息(消息)
                    else:
                        self.调试消息(消息)
                else:
                    self.调试消息(消息)

        新建分隔线._分隔线模板__打印方法 = 打印方法

        return 新建分隔线

    @property
    def 语义日期(self) -> 语义日期模板:
        语义日期: 语义日期模板 = 语义日期模板(打印方法=self.消息)
        return 语义日期

    @property
    def 副本(self):
        副本: 打印模板 = 打印模板()

        # 复制基本字段
        副本.__调试状态 = self.__调试状态
        副本.__打印头 = self.__打印头
        副本.__缩进字符 = self.__缩进字符
        副本.__位置提示符 = self.__位置提示符
        副本.__表格宽度 = self.__表格宽度

        # 复制 特殊字符宽度字典
        副本.__特殊字符宽度字典 = _copy(self.__特殊字符宽度字典)

        # 复制表格内容
        副本.__表格 = _deepcopy(self.__表格)

        # 复制表格列宽控制表
        副本.表格列宽 = self.__表格列宽控制表

        # 复制表格列宽表
        if self.__表格列宽:
            副本.__表格列宽 = _copy(self.__表格列宽)

        # 复制表格列间距
        副本.表格列间距 = self.__表格列间距

        # 复制表格对齐控制表
        副本.__表格列对齐 = _copy(self.__表格列对齐)

        return 副本

    # endregion

    # region 表格操作
    def 准备表格(self, 对齐控制串: str = None, 列宽控制表: list[int] = None):
        """
        将表格的 list[list[str]] 清空,以准备接受新的表格内容
        :param 对齐控制串: 一个包含 l c r 左 中 右 的字符串或者其重复次数，分别控制对应列的对齐方式，l: 左对齐, c: 居中对齐, r: 右对齐, 例如 'l左cr'; 超出对齐控制串的列,由最后一个对齐控制字控制
        :param 列宽控制表: 一个整数列表, 用于控制对应最的最小列宽, 最大列宽由该列最长的字符内容决定
        :return: 返回次级方法
        """
        self.__表格 = []

        self.表格列宽 = 列宽控制表

        self.设置列对齐(对齐控制串=对齐控制串)

        class 次次级方法类:
            def 修饰行(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
                pass

        class 添加多行次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        class 添加空行次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        class 次级方法类:
            def 添加一行(self, *元素列表) -> 次次级方法类:
                pass

            def 添加一调试行(self, *元素列表) -> 次次级方法类:
                pass

            def 添加多行(self,
                         行列表: list or tuple,
                         拆分列数: int = -1,
                         拆分行数: int = -1,
                         修饰方法: _Callable[[str], str] = None) -> 添加多行次级方法类:
                pass

            def 添加多调试行(self,
                             行列表: list or tuple,
                             拆分列数: int = -1,
                             拆分行数: int = -1,
                             修饰方法: _Callable[[str], str] = None) -> 添加多行次级方法类:
                pass

            def 添加空行(self,
                         空行数量: int = 1) -> 添加空行次级方法类:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.添加一行 = self.添加一行
        次级方法.添加一调试行 = self.添加一调试行
        次级方法.添加多行 = self.添加多行
        次级方法.添加多调试行 = self.添加多调试行
        次级方法.添加空行 = self.添加空行

        return 次级方法

    def 设置列对齐(self, 对齐控制串: str = None):
        """
        设置表格的列对齐方式
        :param 对齐控制串: 一个包含 l c r 的字符串或者其重复次数，分别控制对应列的对齐方式，l: 左对齐, c: 居中对齐, r: 右对齐, 例如 'llcr'
        :return: 反回次级方法
        """

        # 定义一个 class, 用于分解控制串中的控制字与重复次数信息
        class __控制字元:
            def __init__(self,
                         控制字: str = 'l'):
                self.控制字: str = 控制字
                self.重复次数字串: str = '0'

            @property
            def 重复次数(self) -> int:
                if not self.重复次数字串:
                    return 0
                elif str.isdigit(self.重复次数字串):
                    if self.重复次数字串 == '0':
                        # 如果这个字元的重复次数字串没有被赋过值，则其需要重复一次，取 1 返回
                        return 1
                    else:
                        # 如果这个字元的重复次数字串已经被赋过值，则取其实际值返回
                        return int(self.重复次数字串)
                else:
                    return 0

        # 先做一个清空操作, 即该方法肯定会清除当前的设置项的
        self.__表格列对齐 = []

        if 对齐控制串 is not None:
            对齐控制串 = str(对齐控制串).strip().lower()
            if 对齐控制串:
                # 第一步,对齐控制串分解为字元列表
                字元列表: list[__控制字元] = []
                控制字: str
                for 字符 in 对齐控制串:
                    if str.isdigit(字符) and 字元列表:
                        # 如果这是一个数字,那这应该是前一个控制字元的重复次数参数
                        字元列表[-1].重复次数字串 = 字元列表[-1].重复次数字串 + 字符
                    else:
                        # 这是一个新的对齐控制字符
                        if 字符 == 'c' or 字符 == '中':
                            控制字 = 'c'
                        elif 字符 == 'r' or 字符 == '右':
                            控制字 = 'r'
                        else:
                            控制字 = 'l'

                        # 把这个新的对齐字追加到字元列表的后面
                        字元列表.append(__控制字元(控制字=控制字))

                if 字元列表:
                    for 字元 in 字元列表:
                        self.__表格列对齐 = self.__表格列对齐 + [字元.控制字] * 字元.重复次数

    def 设置列宽(self, 列宽控制表: list[int] or int = None):
        """
        设置表格的列宽参数
        :param 列宽控制表: 一个整数列表, 用于控制对应最的最小列宽, 最大列宽由该列最长的字符内容决定
        :return: 返回次级方法
        """
        # 先做一个清空操作, 即该方法肯定会清除当前的设置项的
        self.__表格列宽控制表 = 0

        self.表格列宽 = 列宽控制表

        class 设置对齐次级方法:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        class 次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

            def 设置列对齐(self, 对齐控制串: str = None) -> 设置对齐次级方法:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.展示表格 = self.展示表格
        次级方法.设置列对齐 = self.设置列对齐

        return 次级方法

    def 添加一行(self, *元素列表):
        """
        将给定的内容,,整理成一个 list[str] 对象添加到模板内表格的尾部
        但, 如果参数是一个 list 对象, 则该 list 对象被忖为 list[str] 对象后添加到表格的尾部
        :param 元素列表:
        :return:
        """
        if len(元素列表) == 1 and type(元素列表[0]) in [list, tuple]:
            self.__添加一行(元素列表[0])
        elif len(元素列表) > 0:
            self.__添加一行(元素列表)

        class 次级方法类:
            行号: int

            def 修饰行(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
                pass

            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.修饰行 = self.__修饰最后一行
        次级方法.展示表格 = self.展示表格
        if self.__表格:
            次级方法.行号 = max(len(self.__表格) - 1, 0)
        else:
            次级方法.行号 = -1

        return 次级方法

    def 添加空行(self, 空行数量: int = 1, 仅调试: bool = False):
        """
        将指定数量的 [''] 对象添加到表格的尾部
        :param 空行数量: 需要添加的 [''] 的数量
        :param 仅调试:  确认是否只在调试模式生效
        :return: 次级方法
        """
        if not isinstance(空行数量, int):
            空行数量 = -1
        if not isinstance(仅调试, bool):
            仅调试 = False

        确认添加空行: bool = (空行数量 > 0)
        if 仅调试 and not self.__调试状态:
            确认添加空行 = False

        if 确认添加空行:
            for 次数 in range(空行数量):
                self.__添加一行([''])

        class 次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()

        if 仅调试 and not self.__调试状态:
            次级方法.展示表格 = self.__空方法
        else:
            次级方法.展示表格 = self.展示表格

        return 次级方法

    def 添加分隔行(self,
                   填充字符: str = '-',
                   提示文本: str = None,
                   提示对齐: str = 'c',
                   修饰方法: _Callable[[str], str] = None,
                   重复: bool = None,
                   适应窗口: bool = None) -> None:
        """
        为表格添加一行分隔线,或者指定一个内容,这一行的内容不会参与到表格宽度或者列宽度参数的计算中, 这一行更多的像是文本,而不是表格
        :param 填充字符: 这一行需要填充的字符: '-', '*', '~', ...
        :param 提示文本: 分隔行上的提示文本内容
        :param 提示对齐: 分隔行上的提示文本的对齐方式, 支持 l, c, r 选项
        :param 修饰方法: 可以为这一行的内容指定一个修饰的方法, 例如 青字, 红字, 黄字
        :param 重复: 指定填充字符是否自动重复以适应表格宽度
        :param 适应窗口: 可指定生成的分隔行内容是否将长度限现在终端显示宽度范围内
        :return: None
        """
        self.__表格.append(
            self.__表格分隔器(填充字符=填充字符,
                              提示文本=提示文本,
                              重复=重复,
                              修饰方法=修饰方法,
                              提示对齐=提示对齐,
                              适应窗口=适应窗口))
        return None

    def 添加调试分隔行(self,
                       填充字符: str = '-',
                       提示文本: str = None,
                       提示对齐: str = 'c',
                       修饰方法: _Callable[[str], str] = None,
                       重复: bool = None,
                       适应窗口: bool = None) -> None:
        """
        添加一个分隔行, 但只有在调试状态为 True 时才能添加成功
        :param 填充字符: 分隔行填充字符/串
        :param 提示文本: 分隔行上的提示文本内容
        :param 提示对齐: 分隔行上的提示文本的对齐方式, 支持 l, c, r 选项
        :param 修饰方法:  可以指定修饰方法, 例如 青字, 红字, 黄字
        :param 重复:  指定填充字符是否自动重复以适应表格宽度
        :param 适应窗口: 可指定生成的分隔行内容是否将长度限现在终端显示宽度范围内
        :return: None
        """
        if self.__调试状态:
            self.__表格.append(self.__表格分隔器(填充字符=填充字符,
                                                 提示文本=提示文本,
                                                 重复=重复, 修饰方法=修饰方法,
                                                 提示对齐=提示对齐,
                                                 适应窗口=适应窗口))
        return None

    def 修改指定行(self, 行号: int, 列表: list[str] or tuple[str] or list = None):
        """
        如果指定行号的行存在, 可以用新的 list[] 对象为该行重新赋值
        :param 行号:  指定要悠的行号
        :param 列表: 指定修改的内容
        :return: 次级方法
        """
        if 列表 is not None and self.__表格:
            if isinstance(行号, int) and 0 <= 行号 < len(self.__表格):
                if type(列表) in [list, tuple]:
                    self.__表格[行号] = [str(元素) for 元素 in 列表]
                else:
                    self.__表格[行号] = [str(列表)]

                # 修改了某一行的值后,会影响到表格的宽度和列宽度参数的计算,所以这里需要有一些变更复位的操作
                # 复位表格宽度值
                self.__表格宽度 = -1

                # 复位 表格宽度值
                self.__表格列宽 = []

        class 次级方法类:
            def 修饰行(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
                pass

            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        # 定义一个修饰指定行的方法
        def 修饰指定行(方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
            指定修饰的行号: int = 行号
            self.__修饰指定行(行号=指定修饰的行号, 方法=方法)

        次级方法: 次级方法类 = 次级方法类()
        次级方法.修饰行 = 修饰指定行
        次级方法.展示表格 = self.展示表格

        return 次级方法

    def 添加多行(self,
                 行列表: list or tuple,
                 拆分列数: int = -1,
                 拆分行数: int = -1,
                 修饰方法: _Callable[[str], str] = None):
        """
        如果 行列表 不是 list 或者 tuple 对象, 则将 [str(行列表)] 添加到表格尾部
        如果 行列表是 list 或者 tuple 对象, 则判断如下:
        1, 如果指定的 拆分列数 和 拆分行数 均无效(例如小于1), 则做判断如下:
        1.1, 如果 行列表 内部元素是 list 对象,则整理成 list[str] 对象添加到表格尾部
        1.2, 如果 行列表 内部元素不是 list 对象, 则整理成 [str(元素)] 添加到表格尾部
        2, 如果指定的拆分列数有效,则 行列表 视做一维列表,按指定的列数切片后,添加到表格尾部
        2.1, 如果指定的拆分列数无效,但拆分行数有效,则 行列表 视做一维列表, 按不超过指定行数进行切片后,添加到表格尾部
        将 list[list] 对象中的每一个 list 对象添加到表格的尾部
        如果传入的是
        :param 行列表: 需要添加到表格的数据, 一般为 list 对象,或者 list[list] 对象
        :param 拆分列数: 如果行列表为一维 list 对象, 可以指定拆分的列数控制切片, 如果此时没有指定, 则按 1 列进行拆分
        :param 拆分行数: 如果行列表为一维 list 对象, 可以指定拆分的行数控制切换
        :param 修饰方法: 对添加的每一行每一列字符,运行修饰方法进行修饰
        :return: 次级方法
        """
        if type(行列表) in [list, tuple]:
            if 拆分列数 <= 0 and 拆分行数 <= 0:
                for 行元素 in 行列表:
                    if type(行元素) in [list, tuple]:
                        self.__添加一行(行元素)
                        if callable(修饰方法):
                            self.__修饰最后一行(方法=修饰方法)
                    else:
                        self.__添加一行([str(行元素)])
                        if callable(修饰方法):
                            self.__修饰最后一行(方法=修饰方法)
            elif 拆分列数 > 0:
                拆分行列表: list[list] = [行列表[截断位置: 截断位置 + 拆分列数] for 截断位置 in
                                          range(0, len(行列表), 拆分列数)]
                self.添加多行(拆分行列表, 修饰方法=修饰方法)
            else:
                计算拆分列数: int = (len(行列表) / 拆分行数).__ceil__()
                self.添加多行(行列表=行列表, 拆分列数=计算拆分列数, 修饰方法=修饰方法)
        else:
            self.__添加一行([str(行列表)])
            if callable(修饰方法):
                self.__修饰最后一行(方法=修饰方法)

        class 次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.展示表格 = self.展示表格

        return 次级方法

    def 添加一调试行(self, *元素列表):
        """
        添加一行表格内容, 但只有在调试状态为 True 时,才能添加成功
        :param 元素列表:  需要添加的内容
        :return: 次级方法
        """
        if self.__调试状态:
            self.添加一行(*元素列表)

        class 次级方法类:
            行号: int

            def 修饰行(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
                pass

            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        if self.__调试状态:
            次级方法.修饰行 = self.__修饰最后一行
            次级方法.展示表格 = self.展示表格
            次级方法.行号 = max(len(self.__表格) - 1, 0)
        else:
            次级方法.修饰行 = self.__空方法
            次级方法.展示表格 = self.__空方法
            次级方法.行号 = -1

        return 次级方法

    def 添加多调试行(self,
                     行列表: list or tuple,
                     拆分列数: int = -1,
                     拆分行数: int = -1,
                     修饰方法: _Callable[[str], str] = None):
        """
        添加多行表格内容, 但只有在调试状态为 True 时才能添加成功
        :param 行列表: 需要添加的表格内容
        :param 拆分列数: 可以指定拆分列数
        :param 拆分行数: 可以指定拆分行数
        :param 修饰方法: 对添加的每一行每一列字符,运行修饰方法进行修饰
        :return: 次级方法
        """
        if self.__调试状态:
            self.添加多行(行列表, 拆分列数, 拆分行数, 修饰方法=修饰方法)

        class 次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        if self.__调试状态:
            次级方法.展示表格 = self.展示表格
        else:
            次级方法.展示表格 = self.__空方法

        return 次级方法

    def 上下颠倒表格(self):
        """
        将表格的行进行倒序处理,将最末一行的内容放到第一行
        :return: 次级方法
        """
        if self.__表格:
            self.__表格.reverse()

        class 次次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        class 次级方法类:
            def 左右颠倒表格(self) -> 次次级方法类:
                pass

            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.左右颠倒表格 = self.左右颠倒表格
        次级方法.展示表格 = self.展示表格

        return 次级方法

    def 左右颠倒表格(self):
        """
        将表格每一行的 list 对象数量,使用空元素进行补齐到最大列数,然后进行倒序处理,以使最后一列的内容放到第一列
        :return: 次级方法
        """
        if self.__表格:
            表格最大列数: int = max(1, max([len(表格行) for 表格行 in self.__表格 if type(表格行) in [list, tuple]]))

            临时表格: list = []
            for 表格行 in self.__表格:
                if not type(表格行) in [list, tuple]:
                    临时表格.append(表格行)
                else:
                    这一行: list[str] = 表格行[:] + [''] * (表格最大列数 - len(表格行))
                    这一行.reverse()
                    临时表格.append(这一行)
            self.__表格 = 临时表格

            # 处理对齐控制表, 需要同步颠倒
            if 表格最大列数 < len(self.__表格列对齐):
                self.__表格列对齐 = self.__表格列对齐[:表格最大列数]
            elif 表格最大列数 > len(self.__表格列对齐):
                if not self.__表格列对齐:
                    self.__表格列对齐.append('l')
                for 次序 in range(表格最大列数 - len(self.__表格列对齐)):
                    # 后续列继承表格列对齐最后一个对齐控制字
                    self.__表格列对齐.append(self.__表格列对齐[-1])
            self.__表格列对齐.reverse()

            # 处理表格列宽控制表, 需要同步颠倒
            if isinstance(self.__表格列宽控制表, list):
                if 表格最大列数 < len(self.__表格列宽控制表):
                    self.__表格列宽控制表 = self.__表格列宽控制表[:表格最大列数]
                elif 表格最大列数 > len(self.__表格列宽控制表):
                    self.__表格列宽控制表 = self.__表格列宽控制表 + [0] * (表格最大列数 - len(self.__表格列宽控制表))
                self.__表格列宽控制表.reverse()

            # 处理表格列间距, 需要同步颠倒
            if isinstance(self.__表格列间距, list) and 表格最大列数 > 1:
                if 表格最大列数 - 1 < len(self.__表格列间距):
                    self.__表格列间距 = self.__表格列间距[:表格最大列数 - 1]
                elif 表格最大列数 - 1 > len(self.__表格列间距):
                    self.__表格列间距 = self.__表格列间距 + [2] * (表格最大列数 - 1 - len(self.__表格列间距))
                self.__表格列间距.reverse()

        class 次次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        class 次级方法类:
            def 上下颠倒表格(self) -> 次次级方法类:
                pass

            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.上下颠倒表格 = self.上下颠倒表格
        次级方法.展示表格 = self.展示表格

        return 次级方法

    def 修饰列(self, 指定列: list[int] or int, 修饰方法: list[_Callable[[str], str]] or _Callable[[str], str]):
        """
        对指定的列用指定的方法进行修饰
        :param 指定列: 指定列号[从 0 开始],或者指定的列号列表,[0,3,4]
        :param 修饰方法: 指定的方法,或者对应指定列号列表的方法列表
        :return: 次级方法
        """
        可修饰: bool = True
        if 可修饰:
            if not isinstance(指定列, list) and not isinstance(指定列, int):
                可修饰 = False
        if 可修饰 and isinstance(指定列, int) and 指定列 < 0:
            可修饰 = False
        if 可修饰 and isinstance(指定列, list):
            for 列号 in 指定列:
                if not isinstance(列号, int):
                    可修饰 = False
                elif 列号 < 0:
                    可修饰 = False
        if 可修饰:
            if not isinstance(修饰方法, list) and not callable(修饰方法):
                可修饰 = False
        if 可修饰 and isinstance(修饰方法, list):
            for 方法 in 修饰方法:
                if not callable(方法):
                    可修饰 = False
                    break
        if 可修饰 and isinstance(指定列, list) and isinstance(修饰方法, list) and len(指定列) != len(修饰方法):
            可修饰 = False

        if 可修饰:
            # 复位表格宽度值
            self.__表格宽度 = -1

            # 复位 表格宽度值
            self.__表格列宽 = []

        if 可修饰:
            修饰列列号列表: list[int]
            if isinstance(指定列, int):
                修饰列列号列表 = [指定列]
            else:
                修饰列列号列表 = _copy(指定列)

            修饰方法列表: list[_Callable[[str], str]]
            if isinstance(修饰方法, list):
                修饰方法列表 = _copy(修饰方法)
            else:
                修饰方法列表 = [修饰方法] * len(修饰列列号列表)

            if self.__表格:
                for 表格行 in self.__表格:
                    if not type(表格行) in [list, tuple]:
                        # 非 list 或者 tuple 行, 不做修饰处理
                        continue

                    for 下标 in range(len(修饰列列号列表)):
                        列号 = 修饰列列号列表[下标]
                        方法 = 修饰方法列表[下标]

                        if 列号 < len(表格行):
                            元素 = 表格行[列号]

                            # 查找是否存在换行现象
                            换行符: str = '\n' if 元素.__contains__('\n') else ''
                            if not 换行符:
                                换行符 = '\r' if 元素.__contains__('\r') else ''

                            if not 换行符:
                                元素 = 方法(元素)
                                表格行[列号] = str(元素)
                            else:
                                子元素表: list[str] = []
                                for 子元素 in 元素.split(换行符):
                                    子元素表.append(str(方法(子元素)))
                                表格行[列号] = 换行符.join(子元素表)

        class 次级方法类:
            def 展示表格(self, 列间距: list[int] or int = None, 打印方法: _Callable[[str], None] = print) -> None:
                pass

        次级方法: 次级方法类 = 次级方法类()
        次级方法.展示表格 = self.展示表格

        return 次级方法

    def 展示表格(self,
                 列间距: list[int] or int = None,
                 填充字符: str = None,
                 打印方法: _Callable[[str], None] = print) -> None:
        """
        将表格的每行内容进行对齐后合成字符串,分别进持打印呈现
        :param 填充字符: 在进行对齐操作时, 填充在文本字符之间的符号,请尽量使用宽度与英文空格 或者 - 相同的符号, 默认使用英文空格填充
        :param 列间距: 表格对齐处理时,不同列与前面一列的最小间隙,默认为 2 个空格
        :param 打印方法:  可以指定表格行对齐字符串的打印方法, 如果不指定, 默认是 print 方法
        :return: None
        """
        # 如果 __表格 无内容，则直接返回
        if not self.__表格:
            return None

        # 同步列间距参数
        self.表格列间距 = 列间距

        # 判定填充字符
        填充字符 = str(填充字符 if 填充字符 else '')
        if 显示宽度(内容=填充字符, 特殊字符宽度字典=self.__特殊字符宽度字典) != 1:
            if '\033[' in 填充字符:  # 这是一个带有颜色控制的字符串
                颜色控制字匹配模式: str = r'\033\[(?:\d+;)*\d*m'
                填充字符: str = _re.sub(颜色控制字匹配模式, '', 填充字符)
            填充字符 = 填充字符.strip()
            填充字符 = 填充字符[0] if 填充字符 else ' '

        # 展开的表格
        展开的表格: list[list[str] or callable]
        # 表格各列显示宽度表
        各列显示宽度表: list[int]

        展开的表格, 各列显示宽度表 = self.__表格各列显示宽度表()

        # 更新总列数
        总列数: int = len(各列显示宽度表)
        if 总列数 < 1:
            return None

        # 生成列间距表
        列间距表: list[int] = [0]
        if isinstance(self.__表格列间距, int):
            列间距表 = 列间距表 + [self.__表格列间距] * (总列数 - 1)
        elif isinstance(self.__表格列间距, list):
            列间距表 = 列间距表 + self.__表格列间距
            if len(列间距表) < 总列数:
                列间距表 = 列间距表 + [2] * (总列数 - len(列间距表))
        else:
            列间距表 = 列间距表 + [2] * (总列数 - 1)

        # 计算每一列的起始位置
        列起位置: list = [0] * 总列数
        for 列号 in range(总列数):
            if 列号 == 0:
                # 第一列的列起始位置为 0
                列起位置[列号] = 0
            else:
                # 每列的起始位置计算, 前一列起始位置 + 前一列最大长度 + 指定数量的个空格
                列起位置[列号] = 列起位置[列号 - 1] + 各列显示宽度表[列号 - 1] + 列间距表[列号]

        对齐控制表列数: int = len(self.__表格列对齐)
        # 根据每一列的起始位置，将每一行的内容合成一个字符串
        行字符串列表: list[str] = []
        for 行元素 in 展开的表格:
            if callable(行元素):
                行字符串列表.append(str(行元素()))
                continue
            elif not type(行元素) in [list, tuple]:
                行字符串列表.append(str(行元素))
                continue

            列数 = len(行元素)
            行字符串: str = ''
            for 列号 in range(总列数):
                本列对齐方式: str = 'l'
                if 列号 < 对齐控制表列数:
                    本列对齐方式 = self.__表格列对齐[列号]
                elif 对齐控制表列数 > 0:
                    本列对齐方式 = self.__表格列对齐[-1]  # 遵循最后一个控制字的控制逻辑

                if 列号 < 列数:
                    # 补齐 行字符串 尾部的空格，以使其长度与该列的起始位置对齐
                    行字符串 = '{}{}'.format(行字符串, f'{填充字符}' * max(0, (
                            列起位置[列号] - 显示宽度(行字符串, self.__特殊字符宽度字典))))

                    # 在补齐的基础上, 添加本列的内容
                    本列内容: str
                    if 本列对齐方式 == 'l':
                        # 左对齐
                        本列内容 = 行元素[列号]
                    else:
                        本列宽度: int
                        if 列号 + 1 < 总列数:
                            本列宽度 = 列起位置[列号 + 1] - 列起位置[列号] - 列间距表[列号 + 1]
                        else:
                            本列宽度 = 各列显示宽度表[列号]

                        本列补齐空格数量: int = max(0, 本列宽度 - 显示宽度(行元素[列号], self.__特殊字符宽度字典))
                        if 本列补齐空格数量 > 0:
                            if 本列对齐方式 == 'r':
                                # 右对齐
                                本列内容 = '{}{}'.format(f'{填充字符}' * 本列补齐空格数量, 行元素[列号])
                            else:
                                # 居中对齐
                                本列左侧补齐空格数量: int = (本列补齐空格数量 * 0.5).__floor__()
                                本列右侧补齐空格数量: int = 本列补齐空格数量 - 本列左侧补齐空格数量
                                if 本列左侧补齐空格数量 > 0:
                                    本列内容 = '{}{}'.format(f'{填充字符}' * 本列左侧补齐空格数量, 行元素[列号])
                                else:
                                    本列内容 = 行元素[列号]

                                if 本列右侧补齐空格数量 > 0:
                                    # 如果需要做些什么， 可以在这里写你的代码
                                    # 本列内容 = '{}{}'.format(本列内容, ' ' * 本列右侧补齐空格数量)
                                    pass
                        else:
                            本列内容 = 行元素[列号]

                    行字符串 += 本列内容
            行字符串列表.append(行字符串)

        # 打印输出每一行的内容
        if not callable(打印方法):
            打印方法 = self.__打印方法

        if not callable(打印方法):
            打印方法 = print

        if 行字符串列表:
            for 行字符串 in 行字符串列表:
                打印方法(f'{self.__缩进字符}{self.__打印头}{行字符串.rstrip()}')

        return None

    def 保存表格为txt(self, 指定文档: str, 使用Tab分列: bool = False) -> None:
        """
        将表格保存为指定的txt文档, 这里不再有打印头
        :param 指定文档: 带路径的文档名,如果指定的文档已经存在,则会保存失败
        :param 使用Tab分列: 如何指定使用 tag 进行列分割,则每列之间会使用固定的一个 tab 字符
        :return: None
        """

        if not 指定文档:
            self.提示错误(f'指定文档无效(可能是空字符串)')
            return
        if _os.path.isfile(指定文档):
            self.提示错误(f'文档的文档已经存在: {指定文档}')
            return
        if not self.__表格:
            self.提示错误(f'当前表格为空')
            return

        # 创建指定的文档,并将
        try:
            # 创建目录（如果不存在）
            _os.makedirs(_os.path.dirname(指定文档), exist_ok=True)
            with open(指定文档, 'w', encoding='utf-8') as f:
                if 使用Tab分列:
                    f.writelines('\n'.join(['\t'.join(行) for 行 in self.__表格]))
                else:
                    打印头长度: int = len(f'{self.__缩进字符}{self.__打印头}')

                    def writeLine(lineStr: str):
                        f.write(lineStr[打印头长度:].strip() + '\n')

                    self.展示表格(打印方法=writeLine)
        except Exception as thisExp:
            self.提示错误('写入文档操作遇到异常：', str(thisExp))

    def 表格宽度(self, 列间距: list[int] or int = None) -> int:
        """
        根据展示表格和逻辑, 计算当前模板对象中表格内容每一行对齐处理后的字符串,取其中最长的一行的显示宽度返回
        :param 列间距: 表格列间距
        :return: 表格宽度
        """
        # 如果 self.__表格宽度 值不小于0
        if self.__表格宽度 >= 0:
            # 如果不指定列间距, 或者指定的列间距 与 列间距成员相同, 则可以直接返回
            if 列间距 is None:
                return self.__表格宽度
            elif self.__表格列间距 == 列间距:
                return self.__表格宽度
            elif isinstance(self.__表格列间距, list):
                if isinstance(列间距, int):
                    if len(self.__表格列间距) == 1 and self.__表格列间距[0] == 列间距:
                        return self.__表格宽度
                elif isinstance(列间距, list):
                    间距等价: bool = True
                    for 下标 in range(min(len(self.__表格列间距), len(列间距))):
                        if self.__表格列间距[下标] != 列间距[下标]:
                            间距等价 = False
                            break
                    if 间距等价:
                        if len(self.__表格列间距) > len(列间距):
                            if self.__表格列间距[len(列间距):len(self.__表格列间距)] != [2] * (
                                    len(self.__表格列间距) - len(列间距)):
                                间距等价 = False
                    if 间距等价:
                        if len(列间距) > len(self.__表格列间距):
                            if 列间距[len(self.__表格列间距):len(列间距)] != [2] * (
                                    len(列间距) - len(self.__表格列间距)):
                                间距等价 = False

                    if 间距等价:
                        return self.__表格宽度
            elif isinstance(self.__表格列间距, int):
                if isinstance(列间距, list) and len(列间距) == 1 and 列间距[0] == self.__表格列间距:
                    return self.__表格宽度
            else:
                pass

        # 如果 __表格 无内容，则直接返回
        if not self.__表格:
            return 0

        # 同步列间距参数
        self.表格列间距 = 列间距

        # 展开的表格
        展开的表格: list[list[str] or callable]
        # 表格各列显示宽度表
        各列显示宽度表: list[int]

        展开的表格, 各列显示宽度表 = self.__表格各列显示宽度表()

        # 更新总列数
        总列数: int = len(各列显示宽度表)
        if 总列数 < 1:
            return 0

        # 生成列间距表
        列间距表: list[int] = [0]
        if isinstance(self.__表格列间距, int):
            列间距表 = 列间距表 + [self.__表格列间距] * (总列数 - 1)
        elif isinstance(self.__表格列间距, list):
            列间距表 = 列间距表 + self.__表格列间距
            if len(列间距表) < 总列数:
                列间距表 = 列间距表 + [2] * (总列数 - len(列间距表))
        else:
            列间距表 = 列间距表 + [2] * (总列数 - 1)

        # 计算每一列的起始位置
        列起位置: list = []
        for 列号 in range(总列数):
            if 列号 == 0:
                # 第一列的列起始位置为 0
                列起位置.append(0)
            else:
                # 每列的起始位置计算, 前一列起始位置 + 前一列最大长度 + 指定数量的个空格
                列起位置.append(列起位置[列号 - 1] + 各列显示宽度表[列号 - 1] + 列间距表[列号])

        # 最后一列的起始位置 + 最后一列的最大宽度, 即为表格宽度
        self.__表格宽度 = 列起位置[-1] + 各列显示宽度表[-1]

        return self.__表格宽度

    def __添加一行(self, 行表: list or tuple = None) -> None:
        if 行表 is None:
            return None

        if type(行表) not in [list, tuple]:
            return None

        这一行: list[str] = []

        # 将每一行中的元素转为字符串，存于list中
        for 元素 in 行表:
            这一行.append(str(元素))

        if 这一行:
            self.__表格.append(这一行)

            # 复位 表格宽度值
            self.__表格宽度 = -1

            # 复位 表格列宽
            self.__表格列宽 = []

        return None

    def __表格各列显示宽度表(self) -> tuple[list, list[int]]:
        """
        将 self.__表格 的内容展开,计算展开后的表格中, 表格各列的显示宽度, 然后将展开的表格和计算的各列显示宽度表一并返回
        :return: 那个的表格, 各列显示长度表
        """
        展开的表格: list[list[str] or callable] = []
        表格各列显示宽度表: list[int] = []

        if not self.__表格:
            return 展开的表格, 表格各列显示宽度表

        # 把 self.__表格展开，主要是展开单元格中的子行
        展开的表格 = self.__表格展开()

        # 计算 展开的表格 中每一行中列数的最大值
        总列数: int
        if 展开的表格:
            总列数 = max(1, max([len(行元素) for 行元素 in 展开的表格 if type(行元素) in [list, tuple]]))
        else:
            return 展开的表格, 表格各列显示宽度表

        # 计算每一列中各行内容的最大显示长度值
        表格各列显示宽度表 = [0] * 总列数
        for 行元素 in 展开的表格:
            if not type(行元素) in [list, tuple]:
                # 非 list 或者 tuple 行,不参与宽度计算
                continue

            列数 = len(行元素)
            for 列号 in range(总列数):
                if 列号 < 列数:
                    表格各列显示宽度表[列号] = max(显示宽度(行元素[列号], self.__特殊字符宽度字典),
                                                   表格各列显示宽度表[列号])

        # 消除 表格各列显示宽度表 尾部的零，即如果最后 N 列的内容长度都是 0，则可以不再处理最后的 N 列
        临时序列: list = []
        for 列号 in range(总列数):
            if sum(表格各列显示宽度表[列号:]) > 0:
                临时序列.append(表格各列显示宽度表[列号])
        表格各列显示宽度表 = 临时序列

        # 更新总列数
        总列数 = len(表格各列显示宽度表)
        if 总列数 < 1:
            return 展开的表格, 表格各列显示宽度表

        # 生成表格列宽控制表
        表格列宽控制表: list[int] = []
        if isinstance(self.__表格列宽控制表, int):
            表格列宽控制表 = [self.__表格列宽控制表] * 总列数
        elif isinstance(self.__表格列宽控制表, list):
            表格列宽控制表 = self.__表格列宽控制表

        # 考虑表格列宽表中对应列的宽度值,取大使用
        表格列宽控制表长度: int = len(表格列宽控制表)
        for 列号 in range(总列数):
            if 列号 < 表格列宽控制表长度:
                表格各列显示宽度表[列号] = max(表格各列显示宽度表[列号], 表格列宽控制表[列号])
            else:
                break

        # 返回处理结果
        return 展开的表格, 表格各列显示宽度表

    def __表格展开(self) -> list[list[str] or callable]:
        # 这个函数将 self.__表格 进行展开操作，主要是展开表格内容中的换行符
        展开的表格: list[list[str]] = []
        if self.__表格:
            for 行元素 in self.__表格:
                if not type(行元素) in [list, tuple]:
                    # 如果行元素不是list 或者 tuple, 则不做展开处理
                    展开的表格.append(行元素)
                    continue

                # 对表格中的每一行元素，做如下处理
                这一行: list[str]

                换行符: str = '\n'
                换行符的个数: int = sum([1 if str(元素).__contains__(换行符) else 0 for 元素 in 行元素])
                if 换行符的个数 == 0:
                    换行符 = '\r'
                    换行符的个数 = sum([1 if str(元素).__contains__(换行符) else 0 for 元素 in 行元素])

                if 换行符的个数 == 0:
                    # 列表中的元素字符串中不包括换行符
                    这一行 = []
                    for 元素 in 行元素:
                        这一行.append(元素)
                    if 这一行:
                        展开的表格.append(这一行)
                else:
                    # 列表中的元素包括了换行符,则需要处理换行符,处理的方案是换行后的内容放到新的表格行中
                    行列表: list[list[str]] = [str(元素).split(换行符) for 元素 in 行元素]
                    最大行数: int = max([len(列表) for 列表 in 行列表])
                    列数: int = len(行列表)
                    for 行号 in range(最大行数):
                        这一行 = []
                        for 列号 in range(列数):
                            列表: list[str] = 行列表[列号]
                            if 行号 < len(列表):
                                这一行.append(列表[行号])
                            else:
                                这一行.append('')
                        if 这一行:
                            展开的表格.append(这一行)
        return 展开的表格

    def __修饰最后一行(self, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
        if not self.__表格:
            return None

        if not type(self.__表格[-1]) in [list, tuple]:
            # 如果最后一行不是 list 或者 tuple, 则不修饰
            return None

        return self.__修饰指定行(行号=len(self.__表格) - 1, 方法=方法)

    def __修饰指定行(self, 行号: int, 方法: _Callable[[str], str] or list[_Callable[[str], str]] = None) -> None:
        if not self.__表格:
            return None

        有效行号: int = -1
        if isinstance(行号, int) and 0 <= 行号 < len(self.__表格):
            有效行号 = 行号

        if 有效行号 < 0:
            return None

        if not type(self.__表格[有效行号]) in [list, tuple]:
            # 如果 有效行号 对应的行不是 list 或者 tuple, 则不修饰
            return None

        # 准备修饰方法表
        修饰方法表: list[_Callable[[str], str]] = []
        if callable(方法):
            修饰方法表 = [方法]
        elif isinstance(方法, list):
            可修饰: bool = True
            if 可修饰:
                for 方子 in 方法:
                    if not callable(方子):
                        可修饰 = False
                        break
            if 可修饰:
                修饰方法表 = 方法

        if 修饰方法表:
            if not type(self.__表格[有效行号]) in [list, tuple]:
                元素 = str(self.__表格[有效行号])
                for 方子 in 修饰方法表:
                    元素 = str(方子(元素))
                self.__表格[有效行号] = 元素
            else:
                for 序号 in range(len(self.__表格[有效行号])):
                    元素: str = str(self.__表格[有效行号][序号])

                    # 查找是否存在换行现象
                    换行符: str = '\n' if 元素.__contains__('\n') else ''
                    if not 换行符:
                        换行符 = '\r' if 元素.__contains__('\r') else ''

                    if not 换行符:
                        for 方子 in 修饰方法表:
                            元素 = 方子(元素)
                        self.__表格[有效行号][序号] = str(元素)
                    else:
                        子元素表: list[str] = []
                        for 子元素 in 元素.split(换行符):
                            for 方子 in 修饰方法表:
                                子元素 = 方子(子元素)
                            子元素表.append(str(子元素))
                        self.__表格[有效行号][序号] = 换行符.join(子元素表)

        # 由于无法判断修饰方法是否会发动表格元素内容,这可能会影响到表格的宽度和列宽度参数的计算,所以这里需要有一些变更复位的操作
        # 复位表格宽度值
        self.__表格宽度 = -1

        # 复位 表格宽度值
        self.__表格列宽 = []

    def __表格分隔器(self,
                     填充字符: str = '-',
                     提示文本: str = None,
                     提示对齐: str = 'c',
                     修饰方法: _Callable[[str], str] = None,
                     重复: bool = False,
                     适应窗口: bool = None) -> callable:
        if '\033[' in 填充字符:  # 这是一个带有颜色控制的字符串
            颜色控制字匹配模式: str = r'\033\[(?:\d+;)*\d*m'
            填充字符: str = _re.sub(颜色控制字匹配模式, '', 填充字符)
        填充字符 = str(填充字符) if 填充字符 is not None else '-'
        填充字符 = 填充字符 if 填充字符 else '-'

        提示文本 = str(提示文本 if 提示文本 else '').strip()

        if not isinstance(重复, bool):
            if len(填充字符) > 1:
                重复 = False
            else:
                重复 = True

        提示对齐 = str(提示对齐).strip().lower()
        if 提示对齐 and 提示对齐[0] in 'lcr左中右':
            提示对齐 = 提示对齐[0]
        else:
            提示对齐 = 'c'
        提示对齐 = 提示对齐.replace('左', 'l').replace('中', 'c').replace('右', 'r')

        def 自动重复生成器() -> str or 分隔线模板:
            总长度: int = 0
            if 适应窗口:
                # 修正值的作用是为了在行尾穿出位置处理换行符,避免行间粘连问题
                窗口宽度修正值: int
                if len(self.__缩进字符) > 1:
                    窗口宽度修正值 = min(len(self.__缩进字符), 5)
                elif len(f'{self.__缩进字符}{self.__打印头}') > 1:
                    窗口宽度修正值 = min(len(f'{self.__缩进字符}{self.__打印头}'), 5)
                else:
                    窗口宽度修正值 = 2

                窗口宽度值: int = 窗口宽度(修正值=-(显示宽度(f'{self.__缩进字符}{self.__打印头}',
                                                             特殊字符宽度字典=self.__特殊字符宽度字典) + 窗口宽度修正值))
                if 窗口宽度值 > 0:
                    总长度: int = min(self.表格宽度(), 窗口宽度值)
            总长度 = 总长度 if 总长度 > 0 else self.表格宽度()
            return 分隔线模板(符号=填充字符,
                              提示内容=提示文本,
                              总长度=总长度,
                              修饰方法=修饰方法,
                              提示对齐=提示对齐,
                              特殊字符宽度字典=self.__特殊字符宽度字典)

        def 不重复生成器() -> str:
            if callable(修饰方法):
                if 提示文本:
                    return 修饰方法(提示文本)
                else:
                    return 修饰方法(填充字符)
            else:
                if 提示文本:
                    return 提示文本
                else:
                    return 填充字符

        if 重复:
            return 自动重复生成器
        else:
            return 不重复生成器

    def __空方法(self, *args) -> None:
        pass

    # endregion

    def 缩进(self, 缩进字符: str = None):
        """
        将当前打印内容前增加指定的缩进字符, 如果不指定, 则默认增加一个 ' '
        :param 缩进字符: 指定缩进字符
        :return: self
        """
        self.__缩进字符 = f"{self.__缩进字符} " if not 缩进字符 else f"{self.__缩进字符}{缩进字符}"
        return self

    def 打开调试(self) -> '打印模板':
        """
        将打印模板对象的调试状态设置为 True, 并返回 self
        :return: self
        """
        self.__调试状态 = True
        return self

    def 关闭调试(self) -> '打印模板':
        """
        将打印模板对象的调试状态设置为 False, 并返回 self
        :return: self
        """
        self.__调试状态 = False
        return self

    def 设置打印头(self, 符号: str = None):
        """
        模板默认的打印头为 '|-'
        设置当前模板对象打印消息前的标记, 如果不指定, 则为 ''
        :return: self
        """
        self.打印头 = 符号
        return self

    def 设置位置提示符(self, 符号: str = None):
        """
        模板默认的位置提示符为 '->'
        设置模板对齐提示执行位置消息时的打印头, 如果不指定, 则为 ''
        :param 符号: 位置提示消息的打印头符号
        :return: self
        """
        self.位置提示符 = 符号
        return self

    def 设置特殊字符宽度字典(self, 字典: dict[str, float]):
        """
        指定一个字典,这个字典用于指定特殊字符的显示宽度,即其等效的英文空格的数量
        字符显示宽度的计算,将影响到文本对齐场景下的功能表现
        :param 字典: 一个 dict[str, float] 对象
        :return: self
        """
        self.特殊字符宽度字典 = 字典

        # 特殊字符宽度字符将影响到表格的宽度参数的估算,所以设置 特殊字符宽度字典,将会导致表格宽度和列宽表的复位
        # 复位表格宽度值
        self.__表格宽度 = -1

        # 复位 表格宽度值
        self.__表格列宽 = []

        return self

    def 消息(self, *参数表, 打印方法: callable = None):
        """
        输出/打印一条消息, 消息格式为 '{}{}{}'.format(缩进, 打印头, 消息内容)
        :param 打印方法: 可以指定接收 str 作为参数的方法,做为消息的输出处理方法
        :param 参数表: 需要打印的内容
        :return: Any
        """
        打印消息: str = ' '.join((str(参数) for 参数 in 参数表))
        if callable(打印方法):
            return 打印方法(f'{self.__缩进字符}{self.__打印头}{打印消息}')
        elif callable(self.__打印方法):
            return self.__打印方法(f'{self.__缩进字符}{self.__打印头}{打印消息}')
        else:
            return print(f'{self.__缩进字符}{self.__打印头}{打印消息}')

    def 打印空行(self, 行数: int = 1, 仅限调试模式: bool = False) -> None:
        """
        使用 self.__打印方法 打印 指定行数 行的消息, 消息格式为 '{}{}{}'.format(缩进, 打印头, '')
        :param 行数: 指定打印消息的行数
        :param 仅限调试模式: 如果指定为True, 则只有在模板对象的调试状态为True时,才会打印
        :return: None
        """
        if 行数 < 1:
            return None

        打印方法: callable
        if 仅限调试模式:
            打印方法 = self.调试消息
        else:
            打印方法 = self.消息

        for 次数 in range(行数):
            打印方法('')

    def 提示错误(self, *参数表, 打印方法: callable = None):
        """
        将消息以 红底黄字 修饰后,调用 self.消息 输出之
        :param 打印方法: 可以指定接收 str 作为参数的方法,做为消息的输出处理方法
        :param 参数表: 需要打印的消息内容
        :return: None
        """
        错误消息: str = ' '.join((str(参数) for 参数 in 参数表))
        return self.消息(红底黄字(错误消息), 打印方法=打印方法)

    def 调试消息(self, *参数表, 打印方法: callable = None):
        """
        在调试状态下
        将消息以 红底黄字 修饰后,调用 self.消息 输出之
        :param 打印方法: 可以指定接收 str 作为参数的方法,做为消息的输出处理方法
        :param 参数表: 消息内容
        :return: Any
        """
        if self.__调试状态:
            return self.消息(*参数表, 打印方法=打印方法)
        return None

    def 调试错误(self, *参数表, 打印方法: callable = None):
        """
        在调试状态下
        将消息以 红底黄字 修饰后,调用 self.消息 输出之
        :param 打印方法: 可以指定接收 str 作为参数的方法,做为消息的输出处理方法
        :param 参数表: 错误消息内容
        :return: Any
        """
        if self.__调试状态:
            return self.提示错误(*参数表, 打印方法=打印方法)
        return None

    def 提示调试错误(self, *参数表, 打印方法: callable = None):
        """
        效果同方法 调试错误
        :param 打印方法: 可以指定接收 str 作为参数的方法,做为消息的输出处理方法
        :param 参数表: 错误消息内容
        :return: Any
        """
        if self.__调试状态:
            return self.调试错误(*参数表, 打印方法=打印方法)
        return None

    def 执行位置(self, *位置) -> None:
        """
        使用 self.__打印方法 打印一条消息,提示当前代码的运行位置,消息格式 '{}{}{}'.format(缩进, 位置提示符, 参数.__name__ + '开始执行')
        :param 位置: 需要进行提示的方法, 多个位置之间使用符号 . 进行连接,表示成员关系, 如果指定的成员存在 __name__ 属性,则取其 __name__ 值
        :return: None

        对于脚本内的方法(不位于类结构内部),您可以这样写: 画板.执行位置(__file__, 方法名称)
        对于位于类结构内部的方法,您可以这样写: 画板.执行位置(self.__class__, self.方法名称)
        对于脚本内的 if __name__ == '__main__' 入口,您可以这样写: 画板.执行位置(__file__)
        """
        if self.__调试状态:
            提示文本: str = '.'.join(
                (str(每个位置.__name__ if hasattr(每个位置, '__name__') else 每个位置) for 每个位置 in 位置))
            if 提示文本:
                if callable(self.__打印方法):
                    self.__打印方法(f'{self.__缩进字符}{self.__位置提示符}{黄字(提示文本)} 开始执行')
                else:
                    print(f'{self.__缩进字符}{self.__位置提示符}{黄字(提示文本)} 开始执行')

    @staticmethod
    def 帮助文档(打印方法: _Callable[[str], None] = None) -> None:
        画板: 打印模板 = 打印模板()

        if not callable(打印方法):
            画板.添加一行('属性', '功能说明', '|').修饰行(青字)
            画板.添加一行('属性.打印头', '获取或者设置模板对象的打印头字符', '|')
            画板.添加一行('属性.位置提示符', '获取或者设置模板对象的位置提示符字符', '|')
            画板.添加一行('属性.调试状态', '获取当前调试状态,如果正在调试:True, 如果不在调试:False', '|')
            画板.添加一行('属性.正在调试', '获取当前调试状态,如果正在调试:True, 如果不在调试:False', '|')
            画板.添加一行('属性.分隔线', '获取一个分隔线对象,这个对象的 打印方法是 self.消息', '|')
            画板.添加一行('属性.语义日期', '获取一个语义日期对象,这个对象的 打印方法是 self.消息', '|')
            画板.添加一行('属性.副本', '生成并返回一个新的模板对象,新对象中的成员值复制自当前对象', '|')
            画板.添加一行('方法', '功能说明', '|').修饰行(青字)
            画板.添加一行('缩进', '设置打印模板对象在原来缩进的基础上进一步缩进指定的字符,默认为缩进一个空格', '|')
            画板.添加一行('打开调试', '设置调试状态为True,并返回self对象', '|')
            画板.添加一行('关闭调试', '设置调试状态为False, 并返回self对象', '|')
            画板.添加一行('消息', '打印一条指定内容的消息', '|')
            画板.添加一行('错误', '打印一条指定内容的错误消息,该消息以着色方式显示', '|')
            画板.添加一行('调试消息', '打印一条指定内容的消息, 只有调试状态为True时才会打印', '|')
            画板.添加一行('调试错误 ',
                          '打印一条指定内容的错误消息,该消息以着色方式显示, 只有在调试状态为True时才会打印', '|')
            画板.添加一行('执行位置', '打印一条消息, 显示当前程序的执行位置', '|')
            画板.添加一行('', '', '|')
            画板.添加一行('表格属性.表格行数', '获取当前模板对象中表格的行数', '|')
            画板.添加一行('表格属性.表格列数', '获取当前模板对象中表格的列数', '|')
            画板.添加一行('表格属性.表格列表', '获取当前模板对象中表格 list[list]] 对象副本', '|')
            画板.添加一行('表格属性.表格列宽', '获取当前模板对象中表格各列最大宽度的list[int]对象', '|')
            画板.添加一行('表格属性.表格列间距', '获取或设置表格列前的间隙, list[int] 或者 int', '|')
            画板.添加一行('表格操作.准备表格', '通过 准备表格.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.添加一行', '通过 添加一行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.添加分隔行', '通过 添加分隔行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.添加多行', '通过 添加多行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.添加一调试行', '通过 添加一调试行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.添加多调试行', '通过 添加多调试行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.修改指定行', '通过 修改指定行.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.设置列对齐', '通过 设置列对齐.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.设置列宽', '通过 设置列宽.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.修饰列', '通过 修饰列.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.展示表格', '通过 展示表格.__doc__ 查看详情', '|')
            画板.添加一行('表格操作.保存表格为txt', '通过 保存表格为txt.__doc__ 查看详情', '|')

            画板.分隔线.符号('=').提示内容('╗').文本对齐('r').总长度(画板.表格宽度()).修饰(黄字).展示()
            画板.展示表格()
            画板.分隔线.符号('=').提示内容('╝').文本对齐('r').总长度(画板.表格宽度()).展示()
        else:
            画板.添加一行('属性', '功能说明').修饰行(青字)
            画板.添加一行('属性.缩进', '获取或者设置模板对象的缩进字符')
            画板.添加一行('属性.打印头', '获取或者设置模板对象的打印头字符')
            画板.添加一行('属性.位置提示符', '获取或者设置模板对象的位置提示符字符')
            画板.添加一行('属性.调试状态', '获取当前调试状态,如果正在调试:True, 如果不在调试:False')
            画板.添加一行('属性.正在调试', '获取当前调试状态,如果正在调试:True, 如果不在调试:False')
            画板.添加一行('属性.打开调试', '设置调试状态为True,并返回self对象')
            画板.添加一行('属性.关闭调试', '设置调试状态为False, 并返回self对象')
            画板.添加一行('属性.分隔线', '获取一个分隔线对象,这个对象的 打印方法是 self.消息')
            画板.添加一行('属性.语义日期', '获取一个语义日期对象,这个对象的 打印方法是 self.消息')
            画板.添加一行('属性.副本', '生成并返回一个新的模板对象,新对象中的成员值复制自当前对象')
            画板.添加一行('属性', '功能说明').修饰行(青字)
            画板.添加一行('缩进', '设置打印模板对象在原来缩进的基础上进一步缩进指定的字符,默认为缩进一个空格')
            画板.添加一行('打开调试', '设置调试状态为True,并返回self对象')
            画板.添加一行('关闭调试', '设置调试状态为False, 并返回self对象')
            画板.添加一行('消息', '打印一条指定内容的消息')
            画板.添加一行('错误', '打印一条指定内容的错误消息,该消息以着色方式显示')
            画板.添加一行('调试消息', '打印一条指定内容的消息, 只有调试状态为True时才会打印')
            画板.添加一行('调试错误 ',
                          '打印一条指定内容的错误消息,该消息以着色方式显示, 只有在调试状态为True时才会打印')
            画板.添加一行('执行位置', '打印一条消息, 显示当前程序的执行位置')
            画板.添加一行('', '')
            画板.添加一行('表格属性.表格行数', '获取当前模板对象中表格的行数')
            画板.添加一行('表格属性.表格列数', '获取当前模板对象中表格的列数')
            画板.添加一行('表格属性.表格列表', '获取当前模板对象中表格 list[list]] 对象副本')
            画板.添加一行('表格属性.表格列宽', '获取当前模板对象中表格各列最大宽度的list[int]对象')
            画板.添加一行('表格属性.表格列间距', '获取或设置表格列前的间隙, list[int] 或者 int')
            画板.添加一行('表格操作.准备表格', '通过 准备表格.__doc__ 查看详情')
            画板.添加一行('表格操作.添加一行', '通过 添加一行.__doc__ 查看详情')
            画板.添加一行('表格操作.添加分隔行', '通过 添加分隔行.__doc__ 查看详情')
            画板.添加一行('表格操作.添加多行', '通过 添加多行.__doc__ 查看详情')
            画板.添加一行('表格操作.添加一调试行', '通过 添加一调试行.__doc__ 查看详情')
            画板.添加一行('表格操作.添加多调试行', '通过 添加多调试行.__doc__ 查看详情')
            画板.添加一行('表格操作.修改指定行', '通过 修改指定行.__doc__ 查看详情')
            画板.添加一行('表格操作.设置列对齐', '通过 设置列对齐.__doc__ 查看详情')
            画板.添加一行('表格操作.设置列宽', '通过 设置列宽.__doc__ 查看详情')
            画板.添加一行('表格操作.修饰列', '通过 修饰列.__doc__ 查看详情')
            画板.添加一行('表格操作.展示表格', '通过 展示表格.__doc__ 查看详情')

            画板.展示表格(打印方法=打印方法)


# 旧类名 调试模板继续使用
调试模板 = 打印模板


# region 交互与搜索
class 交互选项类:
    """
    选项的代号不能为 0 或者 '0'
    """

    def __init__(self,
                 代号: str or int = None,
                 选项: str = None,
                 备注: str = None,
                 属于功能选项: bool = False,
                 修饰方法: callable = None,
                 可选: bool = True
                 ):
        self._代号: str or int or None = 代号
        self._选项: str = 选项
        self._备注: str = 备注
        self._属于功能选项: bool = 属于功能选项
        self._可选: bool = 可选
        self.修饰方法: callable = 修饰方法

    # region 访问器
    @property
    def 有效(self) -> bool:
        if str(self._选项 if (self._选项 is not None) else '').strip():
            return True
        return False

    @property
    def 代号(self) -> str:
        if isinstance(self._代号, int) and self._代号 > 0:
            return str(self._代号)
        if isinstance(self._代号, str):
            代号值 = self._代号.strip()
            return '' if '0' == 代号值 else 代号值.replace('。', '.')  # 中文 。 需要替换成 .
        return ''

    @property
    def 选项(self) -> str:
        if self.有效:
            return self._选项.strip()
        return ''

    @property
    def 备注(self) -> str:
        return str(self._备注 if self._备注 else '').strip()

    @property
    def 属于功能选项(self) -> bool:
        if self.有效:
            return self._属于功能选项
        return False

    @属于功能选项.setter
    def 属于功能选项(self, 值: bool):
        self._属于功能选项 = True if 值 else False

    @property
    def 可选(self) -> bool:
        if self._可选:
            return True
        else:
            return False

    @可选.setter
    def 可选(self, 值: bool):
        self._可选 = True if 值 else False
    # endregion


class 搜索结果类:
    """
    整理搜索接口的搜索结果
    """

    def __init__(self):
        self.截断: bool = False
        self.总数: int = 0
        self.状态码: int = 0
        self.结果列表: list[str] = []
        self.错误消息: str = ''


class _远程指令执行结果类:
    def __init__(self):
        self.标准输出消息: str = ''
        self.标准错误消息: str = ''


class _远程指令执行结果集类:
    def __init__(self):
        self.指令执行完成: bool = True
        self.存在指令执行错误: bool = False
        self.存在代码执行错误: bool = False
        self.代码执行错误消息: str = ''
        self.执行结果集: dict[str, _远程指令执行结果类] = {}  # 以 ip@userNanme 为key

    def 添加结果(self, ssh接口: 'ssh接口类', 指令结果: _远程指令执行结果类 or str, 标准错误: str = None):
        if isinstance(ssh接口, ssh接口类) and ssh接口.有效:
            if isinstance(指令结果, _远程指令执行结果类):
                self.执行结果集[f'{ssh接口.主机地址}@{ssh接口.用户名}'] = 指令结果
            else:
                结果: _远程指令执行结果类 = _远程指令执行结果类()
                结果.标准输出消息 = str('' if 指令结果 is None else 指令结果).strip()
                结果.标准错误消息 = str('' if 标准错误 is None else 标准错误).strip()
                self.执行结果集[f'{ssh接口.主机地址}@{ssh接口.用户名}'] = 结果

    def 结果存在(self, ssh接口: 'ssh接口类') -> bool:
        if isinstance(ssh接口, ssh接口类) and ssh接口.有效:
            键: str = f'{ssh接口.主机地址}@{ssh接口.用户名}'
            if 键 in self.执行结果集.keys():
                return True
        return False

    def 执行结果(self, ssh接口: 'ssh接口类') -> _远程指令执行结果类:
        if isinstance(ssh接口, ssh接口类) and ssh接口.有效:
            键: str = f'{ssh接口.主机地址}@{ssh接口.用户名}'
            if 键 in self.执行结果集.keys():
                return self.执行结果集[键]
        return _远程指令执行结果类()


class ssh接口类:
    def __init__(self,
                 主机名: str = None,
                 主机地址: str = None,
                 端口号: int = 22,
                 everything服务端口号: int = 0,
                 用户名: str = None,
                 密码: str = None):
        self.主机名: str = 主机名
        self.__主机地址: str = 主机地址
        self.__端口号: int = 端口号
        self.__everything服务端口号: int = everything服务端口号
        self.用户名: str = 用户名
        self.密码: str = 密码
        self.__可达: bool = False
        self.__系统识别完成: bool = False
        self.__在nt系统中: bool = False
        self.__在posix系统中: bool = False
        self.__在mac系统中: bool = False
        self.__检测时间: _time = 0

    # region 访问器
    @property
    def 有效(self) -> bool:
        self.主机名 = str(self.主机名 if self.主机名 else '').strip()
        self.__主机地址 = str(self.__主机地址 if self.__主机地址 else '').strip()
        self.用户名 = str(self.用户名 if self.用户名 else '').strip()
        self.密码 = str(self.密码 if self.密码 else '').strip()
        if isinstance(self.__端口号, str) and self.__端口号.isdigit():
            self.__端口号 = int(self.__端口号)
        if not (isinstance(self.__端口号, int) and 0 < self.__端口号 < 65536):
            self.__端口号 = 22
        if self.主机名 and self.__主机地址 and self.用户名 and self.密码:
            return True
        return False

    @property
    def 无效(self) -> bool:
        return not self.有效

    @property
    def 主机地址(self) -> str:
        return self.__主机地址

    @主机地址.setter
    def 主机地址(self, 地址: str):
        旧地址 = self.__主机地址
        self.__主机地址 = str(地址 if 地址 else '').strip()
        if 旧地址 != self.__主机地址:
            self.__可达 = False
            self.__测试次数 = 0
            self.__系统识别完成 = False

    @property
    def 端口号(self) -> int:
        return self.__端口号

    @property
    def everything服务端口(self) -> int:
        return self.__everything服务端口号

    @端口号.setter
    def 端口号(self, 端口号: int):
        旧端口号 = self.__端口号
        if isinstance(端口号, str) and 端口号.isdigit():
            端口号 = int(端口号)
        if not (isinstance(端口号, int) and 0 < 端口号 < 65536):
            端口号 = 22
        self.__端口号 = 端口号

        if 旧端口号 != self.__端口号:
            self.__可达 = False
            self.__测试次数 = 0
            self.__系统识别完成 = False

    @everything服务端口.setter
    def everything服务端口(self, 端口号: int):
        if isinstance(端口号, str) and 端口号.isdigit():
            端口号 = int(端口号)
        if not (isinstance(端口号, int) and 0 < 端口号 < 65536):
            端口号 = 0
        self.__everything服务端口号 = 端口号

    @property
    def 可达(self) -> bool:
        if not self.__可达 and _time.time() - self.__检测时间 > 30 and self.__主机地址 and self.__端口号:
            # 尝试发起 socket链接,以检测是否可达
            sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            sock.settimeout(1)  # 设置超时时间 1s
            try:
                sock.connect((self.__主机地址, self.__端口号))
                sock.shutdown(_socket.SHUT_RDWR)
                self.__可达 = True
            except Exception as exp:
                self.__可达 = False
            finally:
                sock.close()
        # 记录检测时间，如果距离上次检测时间大于1min时，则重新检测
        self.__检测时间 = _time.time()
        return self.__可达

    @property
    def 在nt系统中(self) -> bool:
        if self.__系统识别完成:
            return self.__在nt系统中
        else:
            # 如果系统识别没有完成,则识别之
            if self.__识别系统类型():
                return self.__在nt系统中
            else:
                return False

    @property
    def 在posix系统中(self) -> bool:
        if self.__系统识别完成:
            return self.__在posix系统中

        else:
            # 如果系统识别没有完成,则识别之
            if self.__识别系统类型():
                return self.__在posix系统中
            else:
                # 如果无法完成系统类型判断,则默认为在 posix 系统中
                return True

    @property
    def 在mac系统中(self) -> bool:
        if self.__系统识别完成:
            return self.__在mac系统中
        else:
            # 如果系统识别没有完成,则识别之
            if self.__识别系统类型():
                return self.__在mac系统中
            else:
                return False

    # endregion

    def __识别系统类型(self) -> bool:
        # 复位系统标志
        self.__在nt系统中 = False
        self.__在posix系统中 = False
        self.__在mac系统中 = False

        # 尝试识别远程系统类型,并返回识别状态
        self.__系统识别完成 = False
        if self.有效:
            ssh管道 = None
            标准输出: str
            标准错误: str
            try:
                # 如果ssh接口有效, 则通过 ssh 管道执行远程指令
                ssh管道 = _paramiko.SSHClient()
                ssh管道.set_missing_host_key_policy(_paramiko.AutoAddPolicy())
                ssh管道.connect(hostname=self.主机地址,
                                username=self.用户名,
                                password=self.密码,
                                port=self.端口号)

                if not self.__系统识别完成:
                    stdin, stdout, stderr = ssh管道.exec_command('ver', timeout=100)
                    标准输出Byte = stdout.read()
                    if 标准输出Byte:
                        标准输出Byte检测 = _chardet.detect(标准输出Byte)
                        标准输出 = 标准输出Byte.decode(encoding=标准输出Byte检测['encoding'] or 'UTF-8').strip()
                        if 标准输出:
                            if 标准输出.lower().__contains__('microsoft windows'):
                                self.__在nt系统中 = True
                                self.__在posix系统中 = False
                                self.__在mac系统中 = False

                                self.__系统识别完成 = True
                if not self.__系统识别完成:
                    stdin, stdout, stderr = ssh管道.exec_command('uname -a', timeout=100)
                    标准输出Byte = stdout.read()
                    if 标准输出Byte:
                        标准输出Byte检测 = _chardet.detect(标准输出Byte)
                        标准输出 = 标准输出Byte.decode(encoding=标准输出Byte检测['encoding'] or 'UTF-8').strip()
                        if 标准输出:
                            if 标准输出.lower().__contains__('linux'):
                                self.__在nt系统中 = False
                                self.__在posix系统中 = True
                                self.__在mac系统中 = False

                                self.__系统识别完成 = True
                            elif 标准输出.lower().__contains__('darwin'):
                                self.__在nt系统中 = False
                                self.__在posix系统中 = False
                                self.__在mac系统中 = True

                                self.__系统识别完成 = True
            finally:
                if isinstance(ssh管道, _paramiko.client.SSHClient):
                    ssh管道.close()

        return self.__系统识别完成

    def 执行远程指令(self,
                     指令: str,
                     目标ssh接口列表: 'ssh接口类' or list['ssh接口类'] = None,
                     超时限制ms: int = 0,
                     画板: 打印模板 = None) -> _远程指令执行结果集类:
        """
        该方法可以支持通过 paramiko.SSHClient 执行一个远程指令，并将指令的执行结果返回
        :param 指令: 待远程执行的指令，一般来说，被执行的指令不宜有大量的返
        :param 目标ssh接口列表: 可以指定目标ssh主机，如果不指定，默认使用 self 参数进行执行，但前提是 self 参数有效
        :param 超时限制ms: exec_command 方法的 timeout 参数值
        :param 画板: 提供打印输出的渠道
        :return: _远程指令执行结果集类，返回执行的结果
        """

        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.执行远程指令)

        执行结果: _远程指令执行结果集类 = _远程指令执行结果集类()

        # 入参检查
        目标ssh接口列表 = 目标ssh接口列表 if isinstance(目标ssh接口列表, list) else [目标ssh接口列表]
        目标ssh接口列表 = [接口 for 接口 in 目标ssh接口列表 if isinstance(接口, ssh接口类) and 接口.有效]

        if not 目标ssh接口列表 and self.有效:
            目标ssh接口列表 = [self]

        if not 目标ssh接口列表 and self.有效:
            执行结果.指令执行完成 = False
            执行结果.存在代码执行错误 = True
            执行结果.代码执行错误消息 = '目标ssh接口列表为空'
            return 执行结果

        指令 = str('' if 指令 is None else 指令).strip()
        if not 指令:
            执行结果.指令执行完成 = False
            执行结果.存在代码执行错误 = True
            执行结果.代码执行错误消息 = '无待执行的指令'
            return 执行结果

        超时限制ms = 超时限制ms if isinstance(超时限制ms, int) else 0
        # endregion

        for ssh接口 in 目标ssh接口列表:
            ssh管道 = None
            标准输出: str = ''
            标准错误: str = ''
            try:
                if ssh接口.有效:
                    # 如果ssh接口有效, 则通过 ssh 管道执行远程指令
                    ssh管道 = _paramiko.SSHClient()
                    ssh管道.set_missing_host_key_policy(_paramiko.AutoAddPolicy())
                    ssh管道.connect(hostname=ssh接口.主机地址,
                                    username=ssh接口.用户名,
                                    password=ssh接口.密码,
                                    port=ssh接口.端口号)
                    if 超时限制ms > 0:
                        stdin, stdout, stderr = ssh管道.exec_command(指令, timeout=超时限制ms)
                    else:
                        stdin, stdout, stderr = ssh管道.exec_command(指令)
                    标准输出Byte = stdout.read()
                    标准输出Byte检测 = _chardet.detect(标准输出Byte)
                    标准输出 = 标准输出Byte.decode(encoding=标准输出Byte检测['encoding'] or 'UTF-8').strip()
                    标准错误 = stderr.read().decode(encoding=标准输出Byte检测['encoding'] or 'UTF-8').strip()
            except Exception as exp:
                执行结果.存在代码执行错误 = True
                执行结果.代码执行错误消息 = exp.__str__()
                break
            finally:
                if isinstance(ssh管道, _paramiko.client.SSHClient):
                    ssh管道.close()

                if 标准错误:
                    执行结果.存在指令执行错误 = True

                执行结果.添加结果(ssh接口=ssh接口, 指令结果=标准输出, 标准错误=标准错误)

        return 执行结果

    def ssh接口补全(self,
                    补地址: bool = False,
                    补端口: bool = False,
                    补用户名: bool = False,
                    补密码: bool = False,
                    画板: 打印模板 = None) -> bool:
        """
        根据入参指定的项目,引导用户输入补全对应的ssh接口信息,当未指定需要补全的项目时,则默认补全所有项目
        :param 补地址: 要求用户补全ssh主机地址
        :param 补端口: 要求用户补全ssh端口号
        :param 补用户名: 要求用户补全ssh用户名
        :param 补密码: 要求用户补全ssh登录密码
        :param 画板: 提供消息打印输出渠道
        :return: 如果用户没有输入 0,且存在至少一个补全项,则返回 True, 否则返回 False
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.ssh接口补全)

        地址已补全: bool = False
        端口已补全: bool = False
        用户名已补全: bool = False
        密码已补全: bool = False

        补所有: bool = False
        if not (补用户名 or 补地址 or 补密码 or 补端口):
            # 如果没有指定需要补全的项目,则认为所有项目都需要补全
            补所有 = True

        def ip地址格式检测(待检测字串: str) -> bool:
            待检测字串 = str(待检测字串 if 待检测字串 else '').strip()
            if not 待检测字串:
                return False
            try:
                _socket.inet_pton(_socket.AF_INET, 待检测字串)
                return True
            except _socket.error:
                try:
                    _socket.inet_pton(_socket.AF_INET6, 待检测字串)
                    return True
                except _socket.error:
                    return False

        def ip端口格式检测(待检测端口: str) -> bool:
            待检测端口 = str(待检测端口 if 待检测端口 else '').strip()
            if not 待检测端口:
                return False
            if not 待检测端口.isdigit():
                return False
            if 0 < int(待检测端口) < 65536:
                return True
            else:
                return False

        def 展示ssh接口信息(画板: 打印模板 = None):
            画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
            画板.执行位置(self.__class__, 展示ssh接口信息)

            画板.准备表格(对齐控制串='ccccc')
            画板.添加一行('主机名', 'ssh地址', 'ssh端口', 'ssh用户名', 'ssh密码').修饰行(青字)
            值列表: list[str] = [self.主机名 if self.主机名 else '-']

            if 补所有 or 补地址:
                值列表.append(
                    f"{绿字(self.主机地址)}{红字('-?') if not 地址已补全 else ''}" if self.主机地址 else 红字('?'))
            else:
                值列表.append(self.主机地址 if self.主机地址 else '-')
            if 补所有 or 补端口:
                值列表.append(
                    f"{绿字(self.端口号)}{红字('-?') if not 端口已补全 else ''}" if self.端口号 else 红字('?'))
            else:
                值列表.append(self.端口号 if self.端口号 else '-')
            if 补所有 or 补用户名:
                值列表.append(
                    f"{绿字(self.用户名)}{红字('-?') if not 用户名已补全 else ''}" if self.用户名 else 红字('?'))
            else:
                值列表.append(self.用户名 if self.用户名 else '-')
            if 补所有 or 补密码:
                值列表.append(
                    f"{绿字(self.密码)}{红字('-?') if not 密码已补全 else ''}" if self.密码 else 红字('?'))
            else:
                值列表.append(self.密码 if self.密码 else '-')
            画板.添加一行(值列表)
            画板.展示表格()

        # 引导用户交互式实例ssh参数接口
        if 补所有 or 补地址:
            展示ssh接口信息(画板=画板)
            地址 = 交互接口类.发起文本交互(输入提示='请输入主机地址(0: 退出补全):', 限定范围=ip地址格式检测,
                                           画板=画板.副本)
            if '0' == 地址:
                # 用户要求退出
                return False
            else:
                self.主机地址 = 地址
                地址已补全 = True
        if 补所有 or 补端口:
            展示ssh接口信息(画板=画板)
            端口 = 交互接口类.发起文本交互(输入提示='请输入主机端口(0: 退出补全):', 限定范围=ip端口格式检测,
                                           画板=画板.副本)
            if '0' == 端口:
                # 用户要求退出
                return False
            else:
                self.端口号 = int(端口)
                端口已补全 = True
        if 补所有 or 补用户名:
            展示ssh接口信息(画板=画板)
            用户名 = 交互接口类.发起文本交互(输入提示='请输入用户名(0: 退出补全):', 画板=画板.副本)
            if '0' == 用户名:
                # 用户要求退出
                return False
            else:
                self.用户名 = 用户名
                用户名已补全 = True
        if 补所有 or 补密码:
            展示ssh接口信息(画板=画板)
            密码 = 交互接口类.发起文本交互(输入提示='请输入密码(0: 退出补全):', 画板=画板.副本)
            if '0' == 密码:
                # 用户要求退出
                return False
            else:
                self.密码 = 密码
                密码已补全 = True

        if self.__主机地址 and not self.主机名:
            self.主机名 = self.__主机地址

        if 补所有 or 补地址 or 补端口 or 补用户名 or 补密码:
            return True
        else:
            return False

    def 展示(self, 画板: 打印模板 = None):
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.展示)

        画板.准备表格(对齐控制串='l')
        画板.添加一行('项目', '值').修饰行(青字)
        画板.添加一行('主机名', self.主机名)
        画板.添加一行('主机地址', self.主机地址)
        画板.添加一行('端口号', self.端口号)
        画板.添加一行('用户名', self.用户名)
        画板.添加一行('密码', self.密码)
        画板.展示表格()


class 搜索接口类:
    """
    这是一个通用的基于搜索接口类,在windows环境下依赖everything服务
    当 ssh接口 无效时:
        当本地环境是 nt 环境时,在本地依赖 everything 服务提供搜索支持
        当本地环境是 posix 环境时,在本地通过 locate/find 提供搜索支持
    当 ssh接口 有效时:
        当远程环境是 nt 环境时,依赖远程环境下的 everything 服务提供搜索支持
        当远程环境是 posix 环境时,通过在远程环境下执行 locate/find 提供搜索支持
    """

    def __init__(self,
                 名称: str = None,
                 地址: str = None,
                 端口号: int = 0,
                 用户名: str = None,
                 密码: str = None,
                 everything服务端口: int = 0,
                 ssh接口: ssh接口类 = None):
        if isinstance(ssh接口, ssh接口类):
            self.ssh接口: ssh接口类 = ssh接口类(主机名=ssh接口.主机名,
                                                主机地址=ssh接口.主机地址,
                                                端口号=ssh接口.端口号,
                                                everything服务端口号=ssh接口.everything服务端口,
                                                用户名=ssh接口.用户名,
                                                密码=ssh接口.密码)
        else:
            self.ssh接口: ssh接口类 = ssh接口类(主机名=名称,
                                                主机地址=地址,
                                                端口号=端口号,
                                                everything服务端口号=everything服务端口,
                                                用户名=用户名,
                                                密码=密码)
        self.__everything服务端口: int = everything服务端口

        # 表示当前搜索服务是否在线
        self.服务在线: bool = True

    # region 访问器
    @property
    def 在nt系统中(self) -> bool:
        if self.ssh接口.有效:
            # 如果 ssh接口 有效,则指的是ssh终端的环境
            return self.ssh接口.在nt系统中
        else:
            # 如果 ssh接口 无效,则指的是当前的运行环境
            return 在nt系统中()

    @property
    def 在posix系统中(self) -> bool:
        if self.ssh接口.有效:
            # 如果 ssh接口 有效,则指的是ssh终端的环境
            return self.ssh接口.在posix系统中
        else:
            # 如果 ssh接口 无效,则指的是当前的运行环境
            return 在posix系统中()

    @property
    def 在mac系统中(self) -> bool:
        if self.ssh接口.有效:
            # 如果 ssh接口 有效,则指的是ssh终端的环境
            return self.ssh接口.在mac系统中
        else:
            # 如果 ssh接口 无效,则指的是当前的运行环境
            return 在mac系统中()

    @property
    def 可用(self) -> bool:
        if self.服务在线:
            if self.ssh接口.无效:
                # 如果 ssh接口 无效,则使用本地环境下的搜索接口判断逻辑
                if self.在nt系统中:
                    if 0 < self.everything服务端口 < 65536:
                        # 在windows系统中,everything的http服务地址是 127.0.0.1, 此时如果everything服务端口有效,则everything服务可用
                        return True
                elif self.在posix系统中:
                    # 在 posix 系统中,搜索服务使用自带命令 find/locate 作为backup,所以默认在 posix 系统中搜索服务可用
                    return True
            else:
                # 如果 ssh接口 有效,则我们需要判断远程终端环境下的搜索服务是否可用
                if self.ssh接口.在nt系统中:
                    if 0 < self.everything服务端口 < 65536:
                        # 在远程windows系统中,everything的http服务地址是 ssh接口.主机地址,此时如果everything服务端口有效,则everything服务可用
                        return True
                elif self.ssh接口.在posix系统中:
                    # 在 posix 系统中,搜索服务使用自带命令 find/locate 作为backup,所以默认在 posix 系统中搜索服务可用
                    return True

        # 如果以上都没有能够判断搜索服务是否可用,则默认搜索服务不可用
        return False

    @property
    def 不可用(self) -> bool:
        return not self.可用

    @property
    def 名称(self) -> str:
        return self.ssh接口.主机名

    @名称.setter
    def 名称(self, 名称: str):
        self.ssh接口.主机名 = 名称

    @property
    def 用户名(self) -> str:
        return self.ssh接口.用户名

    @用户名.setter
    def 用户名(self, 用户名: str):
        旧用户名 = self.ssh接口.用户名
        self.ssh接口.用户名 = 用户名

        if 旧用户名 != self.ssh接口.用户名:
            self.服务在线 = True
            self.服务在线 = self.可用

    @property
    def 端口号(self) -> int:
        return self.ssh接口.端口号

    @端口号.setter
    def 端口号(self, 端口号: int):
        旧端口 = self.ssh接口.端口号
        self.ssh接口.端口号 = 端口号

        if 旧端口 != self.ssh接口.端口号:
            self.服务在线 = True
            self.服务在线 = self.可用

    @property
    def 主机地址(self) -> str:
        return self.ssh接口.主机地址

    @主机地址.setter
    def 主机地址(self, 地址: str):
        旧地址 = self.ssh接口.主机地址
        self.ssh接口.主机地址 = 地址

        if 旧地址 != self.ssh接口.主机地址:
            self.服务在线 = True
            self.服务在线 = self.可用

    @property
    def 密码(self) -> str:
        return self.ssh接口.密码

    @密码.setter
    def 密码(self, 密码: str):
        旧密码 = self.ssh接口.密码
        self.ssh接口.密码 = 密码

        if 旧密码 != self.ssh接口.密码:
            self.服务在线 = True
            self.服务在线 = self.可用

    @property
    def everything服务端口(self) -> int:
        if self.ssh接口.无效:
            return self.__everything服务端口
        if self.ssh接口.有效:
            return self.ssh接口.everything服务端口

    @everything服务端口.setter
    def everything服务端口(self, 端口号: int):
        旧端口号 = self.__everything服务端口
        if isinstance(端口号, str) and 端口号.isdigit():
            端口号 = int(端口号)
        if not (isinstance(端口号, int) and 0 < 端口号 < 65536):
            端口号 = 0

        if self.ssh接口.无效:
            self.__everything服务端口 = 端口号
        if self.ssh接口.有效:
            self.ssh接口.everything服务端口 = 端口号

        # 如果端口号发生了更新,则重置服务可用性
        if 旧端口号 != 端口号:
            if 0 < 端口号 < 65536:
                self.服务在线 = True
                self.服务在线 = self.可用
            else:
                self.服务在线 = self.可用
                self.服务在线 = False

    # endregion

    def 路径展开(self, 路径: str, 画板: 打印模板 = None) -> str:
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.路径展开)

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'
        非法路径分隔符: str = '\\' if self.在posix系统中 else '/'

        路径 = str('' if 路径 is None else 路径).strip().replace(非法路径分隔符, 路径分隔符)
        路径全名: str = ''

        if not 路径:
            # 入参路径是空的,无效的
            return 路径全名

        if 路径.startswith(f'～{路径分隔符}'):
            # 如果路径存在 ~/ 或者 ~\,则修正 ～ 为 ~
            路径 = f'~{路径分隔符}' + 路径[2:]
        elif '～' == 路径:
            # 如果这是一个 ~ 路径,则修正 ～ 为 ~
            路径 = '~'
        if '*' in 路径:
            # 不支持路径中带 *
            画板.调试消息(f'路径展开不支持带有 * 号的路径入参: {路径}')
            return 路径全名
        if len(路径) > 1:
            # 如果不是根路径,则删除路径尾部的分隔符
            路径 = 路径.rstrip(路径分隔符)

        # 合成 路径全名
        路径全名 = 路径
        if '~' == 路径 or 路径.startswith(f'~{路径分隔符}'):
            # 如果路径是一个单独的 ~ 或者是 ~/ 开头的路径,则需要将 ~ 扩展为 homne 路径
            路径全名 = ""
            home路径: str = ''
            if self.ssh接口.在posix系统中:
                if self.ssh接口.无效:
                    # 计算本地环境下的 ~ 路径
                    home路径 = f"{_os.path.expanduser('~')}"
                else:
                    # 计算远程posix环境下的 ~ 参考路径, 该路径为 /home/user
                    home路径 = f'{路径分隔符}home{路径分隔符}{self.ssh接口.用户名}'
            elif self.ssh接口.在nt系统中:
                if self.ssh接口.无效:
                    # 计算本地环境下的 ~ 路径
                    home路径 = f"{_os.path.expanduser('~')}"
                else:
                    # 计算远程nt环境下的 ~ 参考路径, 通过执行远程shell指令 echo %USERPROFILE% 来获取
                    执行结果 = self.ssh接口.执行远程指令(指令='echo %USERPROFILE%',
                                                         超时限制ms=1000,
                                                         画板=画板.副本.缩进())
                    if 执行结果.指令执行完成:
                        if not 执行结果.存在代码执行错误:
                            if 执行结果.结果存在(self.ssh接口):
                                ssh接口指令结果 = 执行结果.执行结果(self.ssh接口)
                                if not ssh接口指令结果.标准错误消息:
                                    home路径 = 执行结果.执行结果(self.ssh接口).标准输出消息.strip()
                                else:
                                    画板.提示错误(
                                        f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})指令出现错误:')
                                    画板.提示错误(f'{ssh接口指令结果.标准错误消息}')
                            else:
                                画板.提示错误(f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})下未执行任何指令')
                        else:
                            画板.提示错误(f'执行远程指令代码异常: {执行结果.代码执行错误消息}')
                    else:
                        画板.提示错误(f'执行远程指令代码未执行完成: {执行结果.代码执行错误消息}')

            home路径 = home路径.rstrip(路径分隔符)
            if home路径:
                # 如果 home路径 解析成功
                if '~' == 路径:
                    # 把 ~ 替换为 home路径
                    路径全名 = home路径
                elif 路径.startswith(f'~{路径分隔符}'):
                    # 将 ~/ 替换为 home路径
                    路径全名 = f'{home路径}{路径分隔符}' + 路径[2:]
        return 路径全名

    def 存在路径(self, 路径: str, 画板: 打印模板 = None) -> bool:
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.存在路径)

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'
        非法路径分隔符: str = '\\' if self.在posix系统中 else '/'

        # region 入参检查
        路径 = str(路径 if 路径 else '').strip().replace(非法路径分隔符, 路径分隔符)
        if 路径.startswith(f'～{路径分隔符}'):
            # 如果路径存在 ~ 路径变量,则修正 ～ 为 ~
            路径 = f'~{路径分隔符}' + 路径[2:]
        elif '～' == 路径:
            # 如果这是一个 ~ 路径,则修正 ～ 为 ~
            路径 = '~'
        if len(路径) > 1:
            # 如果不是根路径,则删除路径尾部的分隔符
            路径 = 路径.rstrip(路径分隔符)
        if not 路径:
            # 如果路径是空,则返回False
            return False
        if '*' in 路径:
            # 如果在路径中存在通配符,则直接否定
            return False
        # endregion

        # region ssh接口 无效,则进行本地判断
        if self.ssh接口.无效:
            return _os.path.isdir(路径)
        # endregion

        # region ssh接口 有效,则需要判断远程是否存在该路径
        shell指令: str = ''
        if self.ssh接口.在posix系统中:
            if '~' == 路径:
                # 把 ~ 扩展为用户根目录
                路径 = f'/home/{self.ssh接口.用户名}'
            elif 路径.startswith('~/'):
                # 将 ~/ 扩展为 /home/user/
                路径 = f'/home/{self.ssh接口.用户名}/' + 路径[2:]

            # 为防止路径中出现空格,路径需要使用 "" 包起来
            shell指令 = f'[ -d "{路径}" ] && echo Existsdyy || echo Noexists'
        elif self.ssh接口.在nt系统中:
            if '~' == 路径:
                # 把 ~ 扩展为用户根目录
                路径 = '%USERPROFILE%'
            elif 路径.startswith('~\\'):
                # 将 ~/ 扩展为 %USERPROFILE%\\
                路径 = f'%USERPROFILE%\\' + 路径[2:]
            shell指令 = f'if exist "{路径}" (echo Existsdyy) else (echo Noexists)'
        画板.调试消息(f'shell指令是: {shell指令}')

        路径存在: bool = False
        if shell指令:
            执行结果 = self.ssh接口.执行远程指令(指令=shell指令, 超时限制ms=1000, 画板=画板.副本.缩进())
            if 执行结果.指令执行完成:
                if not 执行结果.存在代码执行错误:
                    if 执行结果.结果存在(self.ssh接口):
                        ssh接口指令结果 = 执行结果.执行结果(self.ssh接口)
                        if not ssh接口指令结果.标准错误消息:
                            if 'Existsdyy' in 执行结果.执行结果(self.ssh接口).标准输出消息:
                                路径存在 = True
                        else:
                            画板.提示错误(
                                f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})指令出现错误:')
                            画板.提示错误(f'{ssh接口指令结果.标准错误消息}')
                    else:
                        画板.提示错误(f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})下未执行任何指令')
                else:
                    画板.提示错误(f'执行远程指令代码异常: {执行结果.代码执行错误消息}')
            else:
                画板.提示错误(f'执行远程指令代码未执行完成: {执行结果.代码执行错误消息}')
        return 路径存在

        # endregion

    def 存在文档(self, 文档: str, 画板: 打印模板 = None) -> bool:
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.存在文档)

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'
        非法路径分隔符: str = '\\' if self.在posix系统中 else '/'

        # region 入参检查
        文档 = str(文档 if 文档 else '').strip().replace(非法路径分隔符, 路径分隔符)
        if 文档.startswith(f'～{路径分隔符}'):
            # 如果路径存在 ~ 路径变量,则修正 ～ 为 ~
            文档 = f'~{路径分隔符}' + 文档[2:]

        if not 文档:
            # 如果文档是空,则返回False
            return False
        if 文档.endswith(路径分隔符):
            # 如果文档是以路径分隔符结尾的,则这不是一个文档
            return False
        if '*' in 文档:
            # 如果在文档中存在通配符,则直接否定
            return False
        # endregion

        # region ssh接口 无效,则进行本地判断
        if self.ssh接口.无效:
            return _os.path.isfile(文档)
        # endregion

        # region ssh接口 有效,则需要判断远程是否存在该路径
        shell指令: str = ''
        if self.ssh接口.在posix系统中:
            if 文档.startswith('~/'):
                # 将 ~/ 扩展为 /home/user/
                文档 = f'/home/{self.ssh接口.用户名}/' + 文档[2:]

            # 为防止路径中出现空格,路径需要使用 "" 包起来
            shell指令 = f'[ -e "{文档}" ] && echo Existsdyy || echo Noexists'
        elif self.ssh接口.在nt系统中:
            if 文档.startswith('~\\'):
                # 将 ~/ 扩展为 %USERPROFILE%\\
                文档 = f'%USERPROFILE%\\' + 文档[2:]
            shell指令 = f'if exist "{文档}" (echo Existsdyy) else (echo Noexists)'
        画板.调试消息(f'shell指令是: {shell指令}')

        文档存在: bool = False
        if shell指令:
            执行结果 = self.ssh接口.执行远程指令(指令=shell指令, 超时限制ms=1000, 画板=画板.副本.缩进())
            if 执行结果.指令执行完成:
                if not 执行结果.存在代码执行错误:
                    if 执行结果.结果存在(self.ssh接口):
                        ssh接口指令结果 = 执行结果.执行结果(self.ssh接口)
                        if not ssh接口指令结果.标准错误消息:
                            if 'Existsdyy' in 执行结果.执行结果(self.ssh接口).标准输出消息:
                                文档存在 = True
                        else:
                            画板.提示错误(f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})指令出现错误:')
                            画板.提示错误(f'{ssh接口指令结果.标准错误消息}')
                    else:
                        画板.提示错误(f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})下未执行任何指令')
                else:
                    画板.提示错误(f'执行远程指令代码异常: {执行结果.代码执行错误消息}')
            else:
                画板.提示错误(f'执行远程指令代码未执行完成: {执行结果.代码执行错误消息}')
        return 文档存在

        # endregion

    def 列出文档(self, 路径: str, 级联: bool = False, 限制数量: int = 0, 画板: 打印模板 = None) -> list[str]:
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.列出文档)

        文档列表: list[str] = []

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'

        # region 入参检查
        if isinstance(限制数量, str) and 限制数量.isdigit():
            限制数量 = int(限制数量)
        if isinstance(限制数量, float):
            限制数量 = int(限制数量)
        if not isinstance(限制数量, int):
            限制数量 = 0
        if 限制数量 < 1:
            # 如果 限制数量 < 1, 则相当于没有限制
            限制数量 = 1000000

        路径全名: str = self.路径展开(路径=路径, 画板=画板.副本.缩进())
        if not self.存在路径(路径=路径全名):
            # 如果路径不存在,则返回空列表
            return 文档列表
        # endregion

        文档数量: int = 0

        # region 如果搜索接口可用, 但是 ssh接口 无效, 此情况下说明是在本地进行搜索
        if self.可用 and self.ssh接口.无效 and False:
            节点列表: list[str] = []
            权限错误: bool = False
            try:
                for 节点 in _os.scandir(路径全名):
                    if 文档数量 >= 限制数量:
                        break
                    节点列表.append(节点.name)
                    文档数量 += 1
            except PermissionError:
                # 如果遇到 PermissionError 错误,则清空 节点列表 和 文档数量
                权限错误 = True
                节点列表 = []

            if not 权限错误 and 节点列表:
                # 如果没有权限错误, 并且已经搜索到了文档
                for 节点 in 节点列表:
                    全名: str = _os.path.join(路径全名, 节点)
                    if _os.path.isfile(全名):
                        # 判断如果是文档,则添加该文档
                        文档列表.append(全名)

            if not 权限错误:
                # 如果没有权限错误,则返回 文档列表
                return 文档列表
        # endregion

        # region 尝试通过搜索接口进行文档搜索,
        if self.不可用:
            # 如是搜索接口不可用, 则返回空列表
            return 文档列表
        搜索关键字: str = f'{路径全名}{"" if 路径全名.endswith(路径分隔符) else 路径分隔符}*'
        搜索结果 = self.搜索(搜索关键字=搜索关键字, 搜文档=True, 搜路径=False, 画板=画板.副本.缩进())

        文档数量 = 0
        搜索文档全名: str
        搜索文档名: str
        if 搜索结果.总数 > 0:
            for 序号 in range(len(搜索结果.结果列表)):
                if 文档数量 >= 限制数量:
                    # 如果文档数量已经达到限制数量,则不再循环
                    break
                else:
                    搜索文档全名 = 搜索结果.结果列表[序号]
                    if 搜索文档全名 and len(搜索文档全名) > len(路径全名):
                        # 理论上来说,搜索文档全名应该是包含路径命名的
                        搜索文档名 = 搜索文档全名[len(路径全名):].strip(路径分隔符)
                        if 路径分隔符 in 搜索文档名 and not 级联:
                            # 如果搜索文档名中存在 路径分隔符,则说明该文档存在于子路径中
                            continue
                        elif 搜索文档名.startswith('~$'):
                            # 如果搜索文档名中存在 ~$, 则说明该文档存在于垃圾回收站内
                            continue
                        else:
                            文档列表.append(搜索文档全名)
                            文档数量 += 1
            return 文档列表
        # endregion

        # 作为最后的兜底,返回空文档列表
        return 文档列表

    def 列出子路径(self, 路径: str, 级联: bool = False, 限制数量: int = 0, 画板: 打印模板 = None) -> list[str]:
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.列出子路径)

        路径列表: list[str] = []

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'

        # region 入参检查
        if isinstance(限制数量, str) and 限制数量.isdigit():
            限制数量 = int(限制数量)
        if isinstance(限制数量, float):
            限制数量 = int(限制数量)
        if not isinstance(限制数量, int):
            限制数量 = 0
        if 限制数量 < 1:
            # 如果 限制数量 < 1, 则相当于没有限制
            限制数量 = 1000000

        路径全名: str = self.路径展开(路径=路径, 画板=画板.副本.缩进())
        if not self.存在路径(路径=路径全名):
            # 如果路径不存在,则返回空列表
            return 路径列表

        # endregion

        路径数量: int = 0

        # region 如果搜索接口可用, 但 ssh接口 无效, 此情况被认为是在本地进行搜索
        if self.可用 and self.ssh接口.无效:
            节点列表: list[str] = []
            权限错误: bool = False
            try:
                for 节点 in _os.scandir(路径全名):
                    if 路径数量 >= 限制数量:
                        break
                    节点列表.append(节点.name)
                    路径数量 += 1
            except PermissionError:
                # 如果遇到 PermissionError 错误,则清空 节点列表 和 路径数量
                权限错误 = True
                节点列表 = []

            if not 权限错误 and 节点列表:
                for 节点 in 节点列表:
                    全名: str = _os.path.join(路径全名, 节点)
                    if _os.path.isdir(全名):
                        # 判断如果是路径,则添加该路径
                        路径列表.append(全名)

            if not 权限错误:
                # 如果没有权限错误,则返回 路径列表
                return 路径列表
        # endregion

        # region ssh接口 有效,则需要判断搜索接口是否可用,如果搜索接口可用,则通过通过服务列出路径
        if self.不可用:
            # 搜索接口不可用,则返回空列表
            return 路径列表
        搜索关键字: str = f'{路径全名}{"" if 路径全名.endswith(路径分隔符) else 路径分隔符}*'
        搜索结果 = self.搜索(搜索关键字=搜索关键字, 搜文档=False, 搜路径=True, 画板=画板.副本.缩进())

        路径数量 = 0
        搜索路径全名: str
        搜索路径名: str
        if 搜索结果.总数 > 0:
            for 序号 in range(len(搜索结果.结果列表)):
                if 路径数量 >= 限制数量:
                    # 如果文档数量已经达到限制数量,则不再循环
                    break
                else:
                    搜索路径全名 = 搜索结果.结果列表[序号]
                    if 搜索路径全名 and len(搜索路径全名) > len(路径全名):
                        # 理论上来说,搜索文档全名应该是包含路径命名的
                        搜索路径名 = 搜索路径全名[len(路径全名):].strip(路径分隔符)
                        if 路径分隔符 in 搜索路径名 and not 级联:
                            # 如果搜索文档名中存在 路径分隔符,则说明该文档存在于子路径中
                            continue
                        elif 搜索路径名.startswith('~$'):
                            # 如果搜索文档名中存在 ~$, 则说明该文档存在于垃圾回收站内
                            continue
                        else:
                            路径列表.append(搜索路径名)
                            路径数量 += 1
            return 路径列表
        # endregion

        # 作为最后的兜底,返回空路径列表
        return 路径列表

    def 搜索(self,
             搜索关键字: str = None,
             大小写敏感: bool = False,
             参考路径: str = None,
             指定命令参数: str = None,
             搜文档: bool = True,
             搜路径: bool = False,
             限定数量: int = 0,
             画板: 打印模板 = None) -> 搜索结果类:
        """
        根据指定的搜索参数，搜索并返回符合要求的搜索结果集
        :param 搜索关键字: 指定的搜索关键字，可以使用 * 进行模糊匹配，也可以使用 ｜ 分隔限定搜索的路径
        :param 大小写敏感: 指定是否对搜索结果大小写敏感
        :param 参考路径: 指定搜索的参考路径
        :param 指定命令参数: 指定搜索命令参数
        :param 搜文档: 指定要求搜索文档而不是路径，当指定搜索文档时，忽略对参数 搜索路径 的设置
        :param 搜路径: 指定要求搜索路径而不是文档，当没有指定搜索文档时，该参数的设置有效
        :param 限定数量: 指定返回搜索结果的条数，当该参数 < 1时，返回所有的搜索结果
        :param 画板: 指定打印消息的处理对象
        :return: 返回搜索的结果，是一个搜索结果类对象
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.搜索)

        搜索结果 = 搜索结果类()

        # 分辨路径分隔符
        路径分隔符: str = '/' if self.在posix系统中 else '\\'
        非法路径分隔符: str = '\\' if self.在posix系统中 else '/'

        if self.不可用:
            搜索结果.状态码 = 1
            搜索结果.错误消息 = '搜索接口不可用'
            return 搜索结果

        # region 入参检查
        # region 检查搜索关键字
        搜索关键字 = str(搜索关键字 if 搜索关键字 else '').strip().replace(非法路径分隔符,路径分隔符)
        if 搜索关键字.endswith(路径分隔符):
            # 如果搜索关键字以路径分隔符结尾,则补一个 * 作为搜索匹配字符
            搜索关键字 = 搜索关键字 + '*'
        if 路径分隔符 in 搜索关键字:
            # 如果搜索关键字中有路径分隔符,则说明这个搜索关键字中包含了参考路径
            真正关键字 = 搜索关键字.split(路径分隔符)[-1]
            参考路径 = 搜索关键字[:-len(真正关键字)]

            搜索关键字 = 真正关键字.strip()
            参考路径 = 参考路径.rstrip(路径分隔符)
        搜索关键字 = 搜索关键字.replace('.*', '*')  # 把关键字中的 .* 统一替换成 *
        while True:
            if "**" not in 搜索关键字:
                break
            else:
                搜索关键字 = 搜索关键字.replace("**", "*")
        画板.调试消息(f'搜索关键字: {搜索关键字}')
        # endregion

        # region 检查大小写敏感标记
        大小写敏感 = True if 大小写敏感 else False
        画板.调试消息(f'大小写敏感: {大小写敏感}')
        # endregion

        # region 检查参考路径
        参考路径全名: str = self.路径展开(路径=参考路径, 画板=画板.副本.缩进())
        if 参考路径:
            # 如果有参考路径,则需要满足 参考路径命名 也是有效的路径
            if not 参考路径全名:
                # 参考路径全名是空的
                搜索结果.状态码 = 1
                搜索结果.错误消息 = '参考路径全名为空'
                return 搜索结果
            if not self.存在路径(路径=参考路径全名):
                # 如果最终的处理角果,参考路径全名不存在,则返回空的搜索结果
                画板.提示调试错误(f'参考路径全名: {参考路径全名}')
                搜索结果.状态码 = 1
                搜索结果.错误消息 = '参考路径全名无效'
                return 搜索结果
        # endregion

        # region 检查限定数量入参
        if isinstance(限定数量, str) and 限定数量.isdigit():
            限定数量 = int(限定数量)
        if not isinstance(限定数量, int):
            限定数量 = 0
        # endregion

        # region 检查指定命令参数
        指定命令参数 = str(指定命令参数 if 指定命令参数 else '').strip()
        画板.调试消息(f'指定命令参数: {指定命令参数}')
        # endregion

        # region 检查 搜文档/搜路径 标记,优先支持搜路径
        搜文档 = True if 搜文档 else False
        搜路径 = True if 搜路径 else False
        if not 搜文档 and not 搜路径:
            # 如果没有要求搜文档 or 搜路径，则默认搜路径
            搜路径 = True
        画板.调试消息(f'搜文档: {搜文档}')
        画板.调试消息(f'搜路径: {搜路径}')
        # endregion

        # endregion

        # region 合成 posixLocate搜索字串
        posixLocate搜索字串: str = 搜索关键字
        # 把关键字中的 .* 统一替换成 *
        posixLocate搜索字串 = posixLocate搜索字串.replace('.*', '*').strip()

        # endregion

        # region 合成 posixFind搜索字串
        posixFind搜索字串: str = 搜索关键字

        # endregion

        # region 合成 everything搜索字串
        everything搜索字串: str = 搜索关键字
        if 参考路径全名:
            everything搜索字串 = f'"{参考路径全名}{路径分隔符}{everything搜索字串}"'

        # endregion

        # region 在nt平台下,执行everything搜索
        if self.在nt系统中 and everything搜索字串:
            # 关于 everything 的 url 参数,可参考: https://www.voidtools.com/support/everything/http/
            主机地址: str = '127.0.0.1' if self.ssh接口.无效 else self.ssh接口.主机地址
            搜索url: str = f'http://{主机地址}:{self.everything服务端口}/?search={everything搜索字串}' \
                           f'&json=1&path_column=1&size_column=1&date_modified_column=1'
            if 大小写敏感:
                搜索url = f'{搜索url}&case=1'
            画板.调试消息(f'搜索url为: {搜索url}')

            会话 = None
            try:
                会话 = _requests.Session()
                会话.trust_env = False
                everything搜索结果 = 会话.get(搜索url, timeout=2000)
            except Exception as exp:
                搜索结果.总数 = 0
                搜索结果.状态码 = 1
                搜索结果.错误消息 = str(exp)

                self.服务在线 = False
                画板.消息(f'everything 服务请求失败, 本次使用中将关闭 everything 服务支持!!!')
                画板.消息(f'请参考文档 https://ynrx7b5i1u.feishu.cn/docx/CKO8d2NlTo62yVxkUKmcMSWBnDf '
                          f'设置并启用 everything 服务, 并绑定 http 服务端口为: {self.ssh接口.端口号}')
            else:
                if hasattr(everything搜索结果, 'status_code'):
                    搜索结果.状态码 = everything搜索结果.status_code

                    if 搜索结果.状态码 == 200:
                        everything搜索结果 = everything搜索结果.json()
                        if 'totalResults' in everything搜索结果.keys():
                            if everything搜索结果['totalResults'] > 0:
                                for result in everything搜索结果['results']:
                                    文档type: str = ''
                                    文档name: str = ''
                                    文档path: str = ''
                                    if 'type' in result.keys():
                                        文档type = result['type']
                                    if 'name' in result.keys():
                                        文档name = result['name']
                                    if 'path' in result.keys():
                                        文档path = result['path']

                                    if 文档name and '$RECYCLE.BIN' not in 文档name:
                                        # 如果文档名有效且这不是个拉圾站($RECYCLE.BIN)中的文档
                                        文档命中: bool = False
                                        文档全名: str = _os.path.join(文档path, 文档name) if 文档path else 文档name

                                        if 文档全名:
                                            if 搜文档 and 'file' == 文档type:
                                                文档命中 = True
                                            if 搜路径 and 'folder' == 文档type:
                                                文档命中 = True
                                        if 文档命中:
                                            搜索结果.结果列表.append(文档全名)
                                            搜索结果.总数 += 1
                                    if 0 < 限定数量 <= 搜索结果.总数:
                                        # 如果搜索结果中的文档数量满足限定数量,则截断并退出循环
                                        搜索结果.截断 = True
                                        break
                    else:
                        if 搜索结果.状态码 == 503:
                            # 服务器拒绝提供服务
                            self.服务在线 = False
                            画板.消息(f'everything 服务请求失败, 本次使用中将关闭 everything 服务支持!!!')
                            搜索结果.错误消息 = '请求被拒绝提供服务'
                        else:
                            搜索结果.错误消息 = '请根据状态码自行查询'
                else:
                    搜索结果.状态码 = 2
                    搜索结果.错误消息 = str(everything搜索结果)
            finally:
                try:
                    if 会话 is not None:
                        会话.close()
                except Exception as exp:
                    画板.提示调试错误(f'关闭会话(_requests.Session())时出现异常: {str(exp)}')
            return 搜索结果

        # endregion

        # region 在posix平台下,执行locate搜索
        locate服务可用: bool = True
        if self.在posix系统中 and posixLocate搜索字串:
            可能的locate安装位置表: list[str] = [
                "/opt/bin", "/opt/sbin",
                "/usr/local/bin", "/usr/bin", "/bin",
                "/sbin", "/usr/local/sbin",
                "/share/CACHEDEV1_DATA/.qpkg/Entware/bin",
                "/share/CACHEDEV1_DATA/.qpkg/Entware/sbin"
            ]
            locate命令: str = f'export PATH=$PATH:{":".join(可能的locate安装位置表)} && locate'

            locate指令: str
            if 指定命令参数:
                locate指令 = f'{locate命令} {指定命令参数.strip().lstrip("locate").strip()}'
            else:
                locate指令 = f'{locate命令} "{路径分隔符}{posixLocate搜索字串}" | '
                if 搜文档:
                    locate指令 = locate指令 + f'{("grep -i" if not 大小写敏感 else "grep") + " " + 参考路径全名 + " | " if 参考路径全名 else ""}'
                if posixLocate搜索字串[-1] == '*':
                    locate指令 = locate指令 + f'grep {"-i " if not 大小写敏感 else ""} "{posixLocate搜索字串.replace("*", "")}" | '
                else:
                    locate指令 = locate指令 + f'grep {"-i " if not 大小写敏感 else ""} "{posixLocate搜索字串.replace("*", "")}$" | '
                if 搜文档:
                    locate指令 = locate指令 + 'xargs -I {} sh -c \'if [ -f "{}" ]; then echo {}; fi\''
                else:
                    locate指令 = locate指令 + 'xargs -I {} sh -c \'if [ -d "{}" ]; then echo {}; fi\''
            画板.调试消息(f'locate指令: {locate指令}')

            locate结果: str = ''
            locate错误: str = ''
            # 执行 locate 指令
            try:
                if self.ssh接口.无效:
                    # 如果 ssh 接口无效, 则在当前环境下执行 locate 搜索
                    指令结果 = _subprocess.run(locate指令,
                                               stdout=_subprocess.PIPE,
                                               stderr=_subprocess.PIPE,
                                               shell=True,
                                               text=True)
                    locate结果 = str(指令结果.stdout).strip()
                    locate错误 = str(指令结果.stderr).strip()
                else:
                    # 如果ssh接口有效,则在远程环境中执行 locate 搜索
                    执行结果 = self.ssh接口.执行远程指令(指令=locate指令,
                                                         超时限制ms=2000,
                                                         画板=画板.副本.缩进())
                    if 执行结果.指令执行完成:
                        if not 执行结果.存在代码执行错误:
                            if 执行结果.结果存在(self.ssh接口):
                                ssh接口指令结果 = 执行结果.执行结果(self.ssh接口)
                                locate结果 = ssh接口指令结果.标准输出消息
                                locate错误 = ssh接口指令结果.标准错误消息
                            else:
                                画板.提示错误(
                                    f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})下未执行任何指令')
                        else:
                            画板.提示错误(f'执行远程指令代码异常: {执行结果.代码执行错误消息}')
                    else:
                        画板.提示错误(f'执行远程指令代码未执行完成: {执行结果.代码执行错误消息}')
            except Exception as exp:
                搜索结果.状态码 = 1
                搜索结果.错误消息 = str(exp)
                self.服务在线 = False

                locate结果 = ''

            # 解析 locate 结果
            if not locate结果:
                if locate错误:
                    画板.调试消息('locate指令执行错误打印如下:')
                    画板.调试消息(locate错误)

                    errList: list[str] = ['locate: command not found',
                                          'locate: not found',
                                          'locate: 未找到命令',
                                          'locate: no such',
                                          '找不到命令']

                    locate错误小写: str = locate错误.lower()
                    for err in errList:
                        if err in locate错误小写:
                            locate服务可用 = False
                            break

                    if locate错误 and not locate服务可用:
                        画板.提示错误('locate 指令缺失,请确认安装 locate 服务后再试')
                        画板.提示错误('你可以通过 sudo apt-get install plocate 来安装 locate 服务')

                    搜索结果.状态码 = 1
                    搜索结果.错误消息 = locate错误
                else:
                    画板.消息(黄字('基于 locate 的搜索结果可能不是最新的,请更新目标主机上的 locate 数据库后再尝试(sudo updatedb)'))
            else:
                文档命中: bool = True
                for 行 in locate结果.split('\n'):
                    文档全名: str = 行.strip()
                    搜索结果.结果列表.append(文档全名)
                    if 文档全名 and 文档命中:
                        搜索结果.总数 += 1

                    if 0 < 限定数量 <= 搜索结果.总数:
                        搜索结果.截断 = True
                        break
        if locate服务可用:
            # 如果 locate服务可用,则返回locate搜索的结果
            return 搜索结果

        # endregion

        # region 在posix平台下,执行find搜索
        if self.在posix系统中 and posixFind搜索字串:
            find指令: str
            if not 参考路径全名:
                # 如果没有指定参考路径,则强制使用 / 作为参考路径
                参考路径全名 = '/'
            if 指定命令参数:
                find指令 = f'find {指定命令参数}'
            elif 搜文档:
                # 如果被要求搜文档，则处理搜文档逻辑，不再关注是否要求搜路径
                if '*' == posixFind搜索字串:
                    find指令 = f'find {参考路径全名} -maxdepth 1 -type f'
                else:
                    find指令 = f'find {参考路径全名} -{"" if 大小写敏感 else "i"}name "{posixFind搜索字串}" -type f'
            else:
                if '*' == posixFind搜索字串:
                    find指令 = f'find {参考路径全名} -maxdepth 1 -type d'
                else:
                    find指令 = f'find {参考路径全名} -{"" if 大小写敏感 else "i"}name "{posixFind搜索字串}" -type d'
            # 调试模式下展示指令字符串
            画板.调试消息(f'find指令: {find指令}')

            find结果: str = ''
            find错误: str = ''
            try:
                if self.ssh接口.无效:
                    # 如果 ssh 接口无效, 则在当前环境下执行 find 搜索
                    指令结果 = _subprocess.run(find指令,
                                               stdout=_subprocess.PIPE,
                                               stderr=_subprocess.PIPE,
                                               shell=True,
                                               text=True)
                    find结果 = str(指令结果.stdout).strip()
                    find错误 = str(指令结果.stderr).strip()
                    if find错误:
                        # 除去因权限不足引发的 Permission denied 类错误
                        错误列表 = find错误.split('\n')
                        if 错误列表:
                            非PermissionDenied错误列表: list[str] = []
                            for 错误 in 错误列表:
                                if not 错误.endswith('Permission denied'):
                                    if not 错误.endswith('权限不够'):
                                        非PermissionDenied错误列表.append(错误)
                            if 非PermissionDenied错误列表:
                                find错误 = '\n'.join(非PermissionDenied错误列表)
                            else:
                                find错误 = ''
                else:
                    # 如果ssh接口有效,则在远程环境中执行 find 搜索
                    执行结果 = self.ssh接口.执行远程指令(指令=find指令,
                                                         超时限制ms=2000,
                                                         画板=画板.副本.缩进())
                    if 执行结果.指令执行完成:
                        if not 执行结果.存在代码执行错误:
                            if 执行结果.结果存在(self.ssh接口):
                                ssh接口指令结果 = 执行结果.执行结果(self.ssh接口)
                                find结果 = ssh接口指令结果.标准输出消息
                                find错误 = ssh接口指令结果.标准错误消息
                                if find错误:
                                    # 除去因权限不足引发的 Permission denied 类错误
                                    错误列表 = find错误.split('\n')
                                    if 错误列表:
                                        非PermissionDenied错误列表: list[str] = []
                                        for 错误 in 错误列表:
                                            if not 错误.endswith('Permission denied'):
                                                if not 错误.endswith('权限不够'):
                                                    非PermissionDenied错误列表.append(错误)
                                        if 非PermissionDenied错误列表:
                                            find错误 = '\n'.join(非PermissionDenied错误列表)
                                        else:
                                            find错误 = ''
                            else:
                                画板.提示错误(
                                    f'ssh接口({self.ssh接口.主机地址}@{self.ssh接口.用户名})下未执行任何指令')
                        else:
                            画板.提示错误(f'执行远程指令代码异常: {执行结果.代码执行错误消息}')
                    else:
                        画板.提示错误(f'执行远程指令代码未执行完成: {执行结果.代码执行错误消息}')
            except Exception as exp:
                搜索结果.状态码 = 1
                搜索结果.错误消息 = str(exp)
                self.服务在线 = False

                find结果 = ''

            if not find结果:
                if find错误:
                    画板.调试消息('find指令执行错误打印如下:')
                    画板.调试消息(find错误)

                    搜索结果.状态码 = 1
                    搜索结果.错误消息 = find错误
            else:
                文档命中: bool = True
                for 行 in find结果.split('\n'):
                    文档全名: str = 行.strip()
                    搜索结果.结果列表.append(文档全名)
                    if 文档全名 and 文档命中:
                        搜索结果.总数 += 1

                    if 0 < 限定数量 <= 搜索结果.总数:
                        搜索结果.截断 = True
                        break
            return 搜索结果
        # endregion

        # 作为最后的兜底,返回搜索结果
        return 搜索结果


class 交互接口类:
    """
    提供一个统一的, 在命令行场景下与用户交互的处理逻辑,可以支持文本交互,选项交互,路径指定交互,以及文档选择交互
    """

    class 交互结果类:
        """
        定义与用户交互的结果,代号是用户反馈的选项代号列表,选项是用户反馈的对应代号的选项列表
        """

        def __init__(self,
                     代号: list[str] = None,
                     选项: list[str] = None):
            self.代号: list[str] = 代号
            self.选项: list[str] = 选项

    # 提供输入提示消息的修饰,以期提高交互体验, 默认输入提示文本为白底黑色样式,以便醒目
    __输入提示修饰方法: _Callable[[str], str] or None = 白底黑字

    @classmethod
    def __修饰输入提示(cls, 文本: str) -> str or None:
        if 文本 is None:
            return 文本
        elif not callable(cls.__输入提示修饰方法):
            return 文本
        else:
            return cls.__输入提示修饰方法(文本)

    def __init__(self):
        self._选项列表: list[交互选项类] = []

    # region 访问器
    @property
    def 输入提示修饰方法(self) -> _Callable[[str], str]:
        return 交互接口类.__输入提示修饰方法

    @输入提示修饰方法.setter
    def 输入提示修饰方法(self, 修饰方法: _Callable[[str], str] or None):
        交互接口类.__输入提示修饰方法 = 修饰方法

    # endregion

    @classmethod
    def 复位输入提示修饰方法(cls):
        交互接口类.__输入提示修饰方法 = 白底黑字

    @classmethod
    def 设置输入提示修饰方法(cls, 修饰方法: _Callable[[str], str] = None):
        cls.__输入提示修饰方法 = 修饰方法

    def 复位选项(self):
        self._选项列表 = []

    def 添加选项(self,
                 选项: list[str or 交互选项类] or str or 交互选项类,
                 代号: list[str or int] or str or int = None,
                 备注: list[str] or str = None,
                 功能选项标记: list[bool] or bool = False,
                 修饰方法: list[callable] or callable = None,
                 可选: list[bool] or bool = True) -> int:
        """
        添加选项，以供交互时提供给用户选择
        :param 选项: 需要添加的选项
        :param 代号: 需要添加的选项指定的代号
        :param 备注: 需要添加的选项指定的备注信息
        :param 功能选项标记: 标记所添加的选项是否属于功能选项
        :param 修饰方法: 提供该选项的修饰功能
        :param 可选: 指示该选项是否可以选择
        :return: 添加成功的选项的数量
        """
        待添加选项列表: list[交互选项类] = []
        if isinstance(选项, 交互选项类):
            # 如果选项是 交互选项类 对象,则直接添加之
            待添加选项列表.append(选项)
        elif isinstance(选项, list):
            # 如果给出的选项是个列表, 则按列表对齐后操作
            选项数量: int = len(选项)
            代号数量: int = len(代号) if isinstance(代号, list) else (1 if 代号 else 0)
            备注数量: int = len(备注) if isinstance(备注, list) else (1 if 备注 else 0)
            功能选项标记数量: int = len(功能选项标记) if isinstance(功能选项标记, list) else (1 if 功能选项标记 is not None else 0)
            可选标记数量: int = len(可选) if isinstance(可选, list) else (1 if 可选 is not None else 0)

            if 选项数量 > 0:
                代号列表: list[str] = 代号 if isinstance(代号, list) else ([代号] if 代号 else [])
                备注列表: list[str] = 备注 if isinstance(备注, list) else ([备注] if 备注 else [])
                功能选项标记列表: list[bool] = 功能选项标记 if isinstance(功能选项标记, list) else ([功能选项标记] if 功能选项标记 is not None else [])
                可选标记列表: list[bool] = 可选 if isinstance(可选, list) else ([可选] if 可选 is not None else [])
                修饰方法列表: list[callable]
                if isinstance(修饰方法, list):
                    修饰方法列表 = [方法 if callable(方法) else None for 方法 in 修饰方法]
                    修饰方法列表 = 修饰方法列表 + [None] * max(0, 选项数量 - len(修饰方法列表))
                else:
                    if callable(修饰方法):
                        修饰方法列表 = [修饰方法] * 选项数量
                    else:
                        修饰方法列表 = [None] * 选项数量

                代号备注索引: int = 0
                for 选项索引 in range(选项数量):
                    if isinstance(选项[选项索引], 交互选项类):
                        待添加选项列表.append(选项[选项索引])
                    else:
                        选项名称: str = str(选项[选项索引] if 选项[选项索引] else '').strip()

                        代号值: str = ''
                        if 代号备注索引 < 代号数量:
                            代号值 = str(代号列表[代号备注索引] if 代号列表[代号备注索引] else '').strip()

                        备注: str = ''
                        if 代号备注索引 < 备注数量:
                            备注 = str(备注列表[代号备注索引] if 备注列表[代号备注索引] else '').strip()

                        功能选项标记: bool = False
                        if 代号备注索引 < 功能选项标记数量:
                            功能选项标记 = 功能选项标记列表[代号备注索引]

                        可选状态: bool = True
                        if 代号备注索引 < 可选标记数量:
                            可选状态 = 可选标记列表[代号备注索引]

                        修饰方法 = 修饰方法列表[选项索引]

                        代号备注索引 += 1

                        待添加选项列表.append(交互选项类(代号=代号值,
                                                         选项=选项名称,
                                                         备注=备注,
                                                         属于功能选项=功能选项标记,
                                                         修饰方法=修饰方法,
                                                         可选=可选状态))
        else:
            # 统一把 选项,代号, 备注 识为字符串
            if 选项:
                修饰方法 = 修饰方法[0] if isinstance(修饰方法, list) else 修饰方法
                修饰方法 = 修饰方法 if callable(修饰方法) else None
                可选状态 = 可选[0] if isinstance(可选, list) else 可选
                待添加选项列表.append(交互选项类(代号=str(代号 if 代号 else ''),
                                                 选项=str(选项),
                                                 备注=str(备注 if 备注 else ''),
                                                 属于功能选项= True if 功能选项标记 else False,
                                                 修饰方法=修饰方法,
                                                 可选=True if 可选状态 is None else (True if 可选状态 else False)))

        添加选项数量: int = 0
        if 待添加选项列表:
            for 项 in 待添加选项列表:
                if 项.有效:
                    if '-' == 项.选项:
                        self._选项列表.append(项)
                        添加选项数量 += 1
                    elif 项.选项 not in [选项.选项 for 选项 in self._选项列表]:
                        self._选项列表.append(项)
                        添加选项数量 += 1

        return 添加选项数量

    def 添加选项分隔行(self) -> int:
        return self.添加选项(选项='-')

    @classmethod
    def 发起文本交互(cls,
                     输入提示: str = None,
                     允许空值: bool = False,
                     限定范围: list[str] or str or _Callable[[str], bool] = None,
                     画板: 打印模板 = None) -> str:
        """
        返回用户输入的文本内容
        :param 输入提示: 提示用户输入时的提示内容
        :param 允许空值: 如果允许空值,则允许用户不输入任何内容直接提交,否则会轮循要求用户输入内容
        :param 限定范围: 如果存在用户输入,则要求其应是限定范围内的值('0' 不受此约束); 如果限定范围不存在,则不做要求
        :param 画板: 提供用户交互输出的渠道
        :return: 返回用户的输入
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(cls, cls.发起文本交互)

        # 整理输入提示
        输入提示 = (输入提示 if 输入提示 else '').strip()
        输入提示 = 输入提示 if 输入提示 else '请输入：'

        class 范围判定类:
            def __init__(self):
                self.__判定方法: _Callable[[str], bool] or None = None
                self._判定方法名: str = ''
                self.范值列表: list[str] = []

            # region 访问器
            @property
            def 判定方法(self) -> _Callable[[str], bool]:
                return self.__判定方法

            @判定方法.setter
            def 判定方法(self, 方法: _Callable[[str], bool]):
                if callable(方法):
                    self.__判定方法 = 方法
                    self._判定方法名 = 方法.__name__
                else:
                    self.__判定方法 = None
                    self._判定方法名 = ''

            @property
            def 判定失败说明(self) -> str:
                if callable(self.__判定方法):
                    if str.isdigit == self.__判定方法:
                        return '不是数字'
                    elif str.isalnum == self.__判定方法:
                        return f'含有除字母数字外的其它字符'
                    elif str.isalpha == self.__判定方法:
                        return f'含有除字母外的其它字符'
                    elif str.isnumeric == self.__判定方法:
                        return f'含有除数字外的其它字符'
                    elif str.isascii == self.__判定方法:
                        return f'含有除 ASCII 字符外的其它字符'
                    elif str.islower == self.__判定方法:
                        return f'含有除小写字符外的其它字符'
                    elif str.isdecimal == self.__判定方法:
                        return f'不是十进制数字'
                    elif str.isprintable == self.__判定方法:
                        return f'不可打印字符'
                    elif str.isspace == self.__判定方法:
                        return f'含有除空格外的其它字符'
                    elif str.isupper == self.__判定方法:
                        return f'含有除大写字符外的其它字符'
                    elif str.istitle == self.__判定方法:
                        return f'不符合标题规范'
                    else:
                        判定规则名: str
                        if self._判定方法名:
                            判定规则名 = self._判定方法名
                        else:
                            判定规则名 = self.判定方法.__name__

                        if 判定规则名:
                            if 判定规则名.endswith('检测'):
                                return f'不满足 {判定规则名} 规则'
                            else:
                                return f'不满足 {判定规则名} 检测'
                        else:
                            return f'判定规则未知'
                else:
                    if self.范值列表:
                        return f'不在限定范围内({self.范值列表})'
                    else:
                        return f'未知原因'

            # endregion

            def __bool__(self, 文本: str):
                if callable(self.__判定方法):
                    return self.__判定方法(文本)
                elif self.范值列表:
                    if 文本 and 文本 in self.范值列表:
                        return True
                    else:
                        return False
                else:
                    return True

        范围判定: 范围判定类 = 范围判定类()

        # 整理限定范围
        if isinstance(限定范围, list):
            if 限定范围:
                范围判定.范值列表 = [str(限定项).strip() for 限定项 in 限定范围]
            if 限定范围:
                范围判定.范值列表 = [限定项 for 限定项 in 限定范围 if 限定项]
        elif isinstance(限定范围, str):
            字串: str = 限定范围.strip()
            if 字串:
                for 字 in 字串:
                    if 字:
                        范围判定.范值列表.append(字)
        elif callable(限定范围):
            范围判定.判定方法 = 限定范围

        # 启动用户交互,引导用户输入
        while True:
            输入文本 = str(画板.消息(交互接口类.__修饰输入提示(输入提示), 打印方法=input)).strip()
            if not 输入文本:
                if 允许空值:
                    return ''
            else:
                if '0' == 输入文本:
                    return 输入文本
                elif 范围判定.__bool__(输入文本):
                    return 输入文本
                else:
                    画板.消息(f'输入无效: {范围判定.判定失败说明}')

    def 发起选项交互(self,
                     输入提示: str = None,
                     多选: bool = False,
                     选项表名称:str = None,
                     选项值列标题: str = None,
                     操作说明: list[str] or str = None,
                     兴趣字: list[str] or str = None,
                     备注高亮兴趣字: bool = False,
                     画板: 打印模板 = None) -> 交互结果类:
        """
        返回用户输入的功能代号的列表, 或者是代号值
        :param 输入提示: 提示用户输入时的提示内容
        :param 多选: 如果支持多选,用户的输入将被以空格 或者 逗号 为分隔,整理成 list[str] 进行返回
        :param 选项表名称: 所给出的选项列表的表名称
        :param 选项值列标题: 所给出的选项的选项值列的列名称
        :param 操作说明: 可以提供一个说明信息的list[str],在选项前会显示该说明内容[一个元素一行],用于指导用户理解选项
        :param 兴趣字: 如果指定了兴趣字,则选项中的兴趣字会被高亮显示
        :param 备注高亮兴趣字: 兴趣字是否在备注中高亮显示
        :param 画板: 提供用户交互输出的渠道
        :return: 返回用户交互的结果
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.发起选项交互)

        交互结果: 交互接口类.交互结果类 = 交互接口类.交互结果类()
        交互结果.选项 = []
        交互结果.代号 = []

        有效选项列表: list[交互选项类] = [选项 for 选项 in self._选项列表 if 选项.有效]
        if not 有效选项列表:
            画板.提示错误('没有可交互的选项')
            return 交互结果

        def 展示选项(操作说明: list[str] or str = None,
                     兴趣字: list[str] or str = None,
                     备注高亮兴趣字: bool = False,
                     选项表名称: str = None,
                     选项值列标题: str = None,
                     画板: 打印模板 = None) -> tuple[dict[str, str], dict[int, list[str]]]:
            """
            展示有效选项列表中的选项,并返回展示的选项数量
            :param 选项表名称: 如果指定了选项表的名称,则将选项表名称打印在选项表的前一行作为标题
            :param 选项值列标题: 如果指定了选项值列标题,则将选项值列标题打印为指定的名称,否则打印为"选项"
            :param 操作说明: 可以提供一个说明信息的list[str] or str, 在选项前会显示该说明内容[一个元素一行],用于指导用户理解选项
            :param 兴趣字: 如果指定了兴趣字,则选项中的兴趣字会被高亮显示
            :param 备注高亮兴趣字: 是否在备注中高亮显示兴趣字
            :param 画板: 提供交互输入的渠道
            :return: 展示的选项字典,以及各选项组的代号列表
            """
            画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
            画板.执行位置(self.__class__, self.发起选项交互, 展示选项)

            # region 处理操作说明
            操作说明信息: list[str] = []
            if isinstance(操作说明, list):
                for 说明 in 操作说明:
                    操作说明信息.append(str(说明 if 说明 else '').strip())
            elif 操作说明:
                操作说明信息.append(str(操作说明 if 操作说明 else '').strip())
            # endregion

            # region 处理兴趣字
            兴趣字集: list[str] = []
            if isinstance(兴趣字, list):
                for 字 in 兴趣字:
                    兴趣字集.append(str(字 if 字 else '').strip())
            elif 兴趣字:
                兴趣字集.append(str(兴趣字 if 兴趣字 else '').strip())

            if 兴趣字集:
                # 去除空值兴趣字
                兴趣字集 = [字 for 字 in 兴趣字集 if 字]
            if 兴趣字集:
                # 兴趣字按长度排序: 长的在前,短的在后
                兴趣字集 = sorted(兴趣字集, key=len, reverse=True)
            if 兴趣字集:
                # 如果存在兴趣字集,则添加到操作说明中显示
                操作说明信息.append(f"兴趣字: {str(兴趣字集)}")

            # 处理兴趣字集中的通配符号(*)
            兴趣字集平化: list[str] = []
            for 字 in 兴趣字集:
                字 = 字.strip('*')  # 先去除前后的 * 号
                if '*' not in 字:
                    兴趣字集平化.append(字)  # 如果不再含 * 号,则完成平化
                else:
                    平化列表: list[str] = [平化字.strip() for 平化字 in 字.split('*')]  # if 还存在 *, 则继续平化
                    平化列表 = [平化字 for 平化字 in 平化列表 if 平化字]
                    兴趣字集平化 = 兴趣字集平化 + 平化列表
            兴趣字集平化 = list(set(兴趣字集平化))  # 做个去重处理
            if not 兴趣字集平化:
                兴趣字集 = []
            else:
                兴趣字集 = sorted(兴趣字集平化, key=len)  # 为了方便兴趣字着色,需要将兴趣字从短到长排序处理
            # endregion

            # region 提示多选操作方式
            if 多选:
                操作说明信息.append(f'多选提示: 您可以使用 1,3,5 或 1 2 s1 的样式选择多个选项')
                操作说明信息.append(f'多选提示: 您可以使用 1-s1 的样式选择指定代号范围内的多个选项')
            # endregion

            # region 处理选项表名称和选项值列标题
            选项表名称 = str(选项表名称 if 选项表名称 else '').strip()
            选项值列标题 = str(选项值列标题 if 选项值列标题 else '选项').strip()
            # endregion

            def 绿化处理(内容: str) -> str:
                # 把 内容 中的 兴趣字 标记为绿色，以起到醒目作用
                绿化内容: str = 内容
                if 兴趣字集:
                    for 字 in 兴趣字集:
                        if 字:
                            # 把字做为一个匹配模板来进行匹配绿化内容,并设置忽略大小写,将字中的符号 . 替换成 \. 以便可以匹配到符号 . 本身
                            匹配结果: list[str] = _re.findall(字.replace('.', '\\.'), 绿化内容, flags=_re.I)
                            if 匹配结果:
                                匹配结果 = [str(结果).strip() for 结果 in 匹配结果]
                                匹配结果 = [结果 for 结果 in 匹配结果 if 结果]
                                if 匹配结果:
                                    匹配结果 = list(set(匹配结果))
                            if 匹配结果:
                                for 结果 in 匹配结果:
                                    if 结果 in 绿化内容:
                                        绿化内容 = 绿化内容.replace(结果, 绿字(结果))
                return 绿化内容

            选项序号: int = 0
            选项字典: dict[str, str] = {}
            分组选项代号字典: dict[int, list[str]] = {}

            画板.准备表格(对齐控制串='rl')
            画板.表格列间距 = 2
            # region 打印表名称
            if 选项表名称:
                画板.添加分隔行(提示文本=选项表名称, 适应窗口=True, 修饰方法=黄字)
            # endregion

            # region 打印操作说明信息
            if 操作说明信息:
                for 说明 in 操作说明信息:
                    if 说明:
                        画板.添加分隔行(提示文本=说明, 提示对齐='l', 重复=False)
                    else:
                        画板.添加空行()
            # endregion

            # region 添加表标题行
            标题行 = 画板.添加一行('').行号
            # endregion

            选项组号: int = 0
            备注存在: bool = False
            for 选项 in 有效选项列表:
                if '-' == 选项.选项:
                    画板.添加分隔行(填充字符='- ', 重复=True, 适应窗口=True)

                    # 每添加一个分隔线,则选项组号增加 1
                    选项组号 = 选项组号 + 1
                elif 选项.有效:
                    临时代号 = 选项.代号
                    if not 临时代号 or 临时代号 in [0, '0']:
                        选项序号 = 选项序号 + 1
                        临时代号 = 选项序号
                    if 临时代号:
                        if 临时代号 in 选项字典.keys():
                            临时代号可用: bool = False
                            for i in range(1, 100):
                                if f'{临时代号}-{i}' not in 选项字典.keys():
                                    临时代号 = f'{临时代号}-{i}'
                                    临时代号可用 = True
                                    break
                            if not 临时代号可用:
                                临时代号 = ''
                        if 临时代号:
                            临时代号 = str(临时代号)

                            # 将该选项添加到选项字典中
                            if 选项.可选:
                                选项字典[临时代号] = 选项.选项

                            # 将该选项代号添加到 分组选项代号字典 中
                            if 选项组号 not in 分组选项代号字典:
                                分组选项代号字典[选项组号] = []
                            分组选项代号字典[选项组号].append(临时代号)

                            绿化的选项: str = 选项.选项 if 选项.属于功能选项 else 绿化处理(选项.选项)
                            if 选项.备注:
                                备注存在 = True
                                绿化的备注: str = 绿化处理(选项.备注) if 备注高亮兴趣字 and not 选项.属于功能选项 else 选项.备注
                                if callable(选项.修饰方法):
                                    画板.添加一行(临时代号, 绿化的选项, 绿化的备注).修饰行(方法=选项.修饰方法)
                                else:
                                    画板.添加一行(临时代号, 绿化的选项, 绿化的备注)
                            else:
                                if callable(选项.修饰方法):
                                    画板.添加一行(临时代号, 绿化的选项).修饰行(方法=选项.修饰方法)
                                else:
                                    画板.添加一行(临时代号, 绿化的选项)

            # 定制标题行
            if 备注存在:
                画板.修改指定行(行号=标题行, 列表=['代号', 选项值列标题, '备注']).修饰行(青字)
            else:
                画板.修改指定行(行号=标题行, 列表=['代号', 选项值列标题]).修饰行(青字)

            if 选项字典:
                画板.展示表格()
                if '0' not in 选项字典.keys():
                    # 在最后一组选项中添加一个额外的代号为 '0' 的选项
                    选项字典['0'] = ''

            return 选项字典, 分组选项代号字典

        输入提示 = (输入提示 if 输入提示 else '').strip()
        输入提示 = 输入提示 if 输入提示 else '根据以上所列,请输入选项代号: '

        选项字典: dict[str, str]
        分组选项代号字典: dict[int, list[str]]

        选项字典, 分组选项代号字典 = 展示选项(操作说明=操作说明,
                                              兴趣字=兴趣字,
                                              备注高亮兴趣字=备注高亮兴趣字,
                                              选项表名称=选项表名称,
                                              选项值列标题=选项值列标题,
                                              画板=画板)

        选项代号总表: list[str] = list(选项字典.keys())
        if not 选项代号总表:
            return 交互结果
        else:
            while True:
                输入文本 = str(画板.消息(交互接口类.__修饰输入提示(输入提示), 打印方法=input)).strip()
                if not 输入文本:
                    # 如果用户没有输入内容,则循环询问
                    continue
                else:
                    # 如果存在用户输入
                    输入文本 = 输入文本.replace('。', '.')  # 将输入文本中的 。 替换成 .
                    if not 多选:
                        # 如果不支持多选
                        if 输入文本 in 选项代号总表:
                            交互结果.代号.append(输入文本)
                            交互结果.选项.append(选项字典[输入文本])
                            return 交互结果
                        else:
                            # 如果存在无效的选项代号,则提示用户重新输入
                            画板.消息(f'不存在选项代号 {红字(输入文本)}, 请重新输入')
                            continue
                    else:
                        分隔符号 = ' '
                        if ',' in 输入文本:
                            分隔符号 = ','
                        elif '，' in 输入文本:
                            分隔符号 = '，'

                        输入文本切割: list[str] = 输入文本.split(分隔符号)
                        输入文本切割 = list(
                            set([有效文本 for 有效文本 in [文本.strip() for 文本 in 输入文本切割] if 有效文本]))

                        选择的代号列表: list[str] = []
                        if 输入文本切割:
                            存在无效值: bool = False
                            for 文本 in 输入文本切割:
                                if '-' in 文本 and 文本 not in 选项代号总表:
                                    选项代号组表: list[str] = []

                                    # 这是一个范围指定项, 例如 'a-z', '1-8', '-', 'a-', '-12' 等
                                    范围值表: list[str] = [值.strip() for 值 in 文本.split('-') if 值.strip()]

                                    代号下界: str = '-'
                                    代号上界: str = '-'
                                    if len(范围值表) < 1: # 用户单独输入了一个 - 符号, 这被认为用户要求选择选项组第0组中的所有选项
                                        选项代号组表 = 分组选项代号字典[0]
                                        代号下界 = 选项代号组表[0]
                                        代号上界 = 选项代号组表[-1]
                                    elif len(范围值表) == 1: # 用户输入了单一边界,例如 a- 或者 -15 此类,则说明用户需要选择对应组中不小于或者不大于指定边界的所有选项
                                        边界代号 = 范围值表[0]
                                        for 组号 in range(len(分组选项代号字典)):
                                            if 边界代号 in 分组选项代号字典[组号]: # 如果指定的边界在这一组中,则在这一组中进行边界勘定
                                                选项代号组表 = 分组选项代号字典[组号]
                                                if 文本[0] == '-': # 这个边界是指定的上边界
                                                    代号下界 = 选项代号组表[0]
                                                    代号上界 = 边界代号
                                                else: # 这个边界是指定上下边界
                                                    代号下界 = 边界代号
                                                    代号上界 = 选项代号组表[-1]
                                            break
                                        if 代号下界 == '-' or 代号上界 == '-':
                                            存在无效值 = True
                                            画板.消息(f'不存在选项代号 {红字(边界代号)}, 请重新输入')
                                    else:
                                        代号下界 = 范围值表[0]
                                        代号上界 = 范围值表[-1]

                                        # 同时指定上边界和下边界的情况下,则要求所指定的边界位于同一个选项分组内
                                        边界属于同一分组: bool = False
                                        for 组号 in range(len(分组选项代号字典)):
                                            if 代号下界 in 分组选项代号字典[组号]: # 如果代号下界位于这一组中
                                                if 代号上界 in 分组选项代号字典[组号]: # 如果代号上界也位于该组中
                                                    边界属于同一分组 = True

                                                if 边界属于同一分组:
                                                    选项代号组表 = 分组选项代号字典[组号]
                                                break
                                        if not 边界属于同一分组:
                                            # 用户输入的区间上下界不在同一个选项分组中,则通知用户重新输入
                                            存在无效值 = True
                                            画板.消息(f'所指定的区间 {红字(文本)} 不属于同一选项分组, 或不存在指定的选项代号, 请重新输入')

                                    代号下界索引: int = -1
                                    代号上界索引: int = -1

                                    if 存在无效值:
                                        break
                                    else:
                                        代号下界索引 = 选项代号组表.index(代号下界)
                                        代号上界索引 = 选项代号组表.index(代号上界)

                                        if 代号下界索引 == 代号上界索引:  # 代号下界与代号上界相同
                                            选择的代号列表.append(代号下界)
                                        else:
                                            for 索引 in range(min(代号下界索引, 代号上界索引), max(代号下界索引, 代号上界索引) + 1):
                                                选择的代号列表.append(选项代号组表[索引])
                                else:
                                    if 文本 in 选项代号总表:
                                        选择的代号列表.append(文本)
                                    else:
                                        # 如果存在无效的选项代号,则提示用户重新输入
                                        画板.消息(f'不存在选项代号 {红字(文本)}, 请重新输入')
                                        存在无效值 = True
                                        break

                            if 存在无效值:
                                continue
                            else:
                                # 如果用户输入都在选项范围内,则整理输入结果并返回
                                for 代号 in 选择的代号列表:
                                    if 代号 not in 交互结果.代号:
                                        交互结果.代号.append(代号)
                                        交互结果.选项.append(选项字典[代号])
                                return 交互结果
                        else:
                            # 如果没有检测到有效的输入内容, 则循环询问
                            continue

    @classmethod
    def 指定选择路径(cls,
                     输入提示: str = None,
                     搜索关键字: str = None,
                     候选项上限: int = 50,
                     选项表名称: str = None,
                     搜索接口: 搜索接口类 = None,
                     功能选项: 交互选项类 or list[交互选项类] = None,
                     排除规则: _Callable[[str], bool] or list[_Callable[[str], bool]] = None,
                     画板: 打印模板 = None) -> str:
        """
        向用户发起交互,以获取用户指定的文档路径
        :param 输入提示: 提示用户输入时的提示内容
        :param 搜索关键字: 可以指定初始搜索关键字
        :param 候选项上限: 如果存在候选项,则限制候选项数量,如果此参数值 <= 0, 则不设限
        :param 选项表名称: 发起用户交互时的表名称
        :param 搜索接口: 协助用户搜索文档的接口
        :param 功能选项: 提供功能选项,以供用户选择对应功能,并返回到上级功能层
        :param 排除规则: 对每一个候选路径运用排除规则[如果规则可用],如果规则返回True,则该候选项被排除
        :param 画板: 提供用户交互输出的渠道
        :return: 用户选择的文档路径 或者给定的功能选项中用户选择的选项的代号
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(cls, cls.指定选择路径)

        输入提示 = str(输入提示 if 输入提示 else '').strip()
        输入提示 = 输入提示 if 输入提示 else '请指定路径(0:退出): '

        搜索关键字 = str(搜索关键字 if 搜索关键字 else '').strip()

        候选项上限 = 候选项上限 if isinstance(候选项上限, int) else 50

        功能选项 = 功能选项 if isinstance(功能选项, list) else [功能选项]
        功能选项 = [项 for 项 in 功能选项 if isinstance(项, 交互选项类) and 项.有效]

        排除规则 = 排除规则 if isinstance(排除规则, list) else [排除规则]
        排除规则 = [规则 for 规则 in 排除规则 if callable(规则)]

        路径约束: list[str]
        关键字: str

        轮循次数: int = 0
        用户输入: str
        搜索条数限制: int = max(1000, 候选项上限 * 10)
        while True:
            # 轮循计数
            轮循次数 += 1

            # 标记是否需要以文档定路径
            文档定路径标记: bool = False

            if 轮循次数 == 1 and 搜索关键字 and '0' != 搜索关键字:
                # 如果第一次轮循,并且存在搜索关键字, 则直接使用搜索关键字展开搜索
                用户输入 = 搜索关键字
            else:
                用户输入 = (cls.发起文本交互(输入提示=输入提示, 画板=画板)).strip()

            # 如果用户输入的是 f=关键字 这种格式的内容,说明用户需要以文档来确定路径
            if len(用户输入) > 2:
                if 用户输入[0].lower() == 'f':
                    if 用户输入[1] in ['=', '＝']:
                        文档定路径标记 = True
                        用户输入 = 用户输入[2:]

            if '0' == 用户输入:
                路径 = '0'
                break
            else:
                # region 分解用户的输入
                用户输入 = 用户输入.replace('｜', '|').strip('|')
                if '|' in 用户输入:
                    # 这个用户输入中包括了约束项
                    用户输入分解: list[str] = [项.strip() for 项 in 用户输入.split('|')]
                    关键字 = 用户输入分解[-1]
                    路径约束 = 用户输入分解[:-1]
                else:
                    # 这个用户输入不包括约束项
                    关键字 = 用户输入
                    路径约束 = []
                if 路径约束:
                    路径约束小写化 = [约束.lower() for 约束 in 路径约束]
                else:
                    路径约束小写化 = []

                路径 = 关键字
                # endregion

                if not isinstance(搜索接口, 搜索接口类) or 搜索接口.不可用:
                    # if 搜索接口不是符合条件的类型, 或者搜索接口不可用, 则无法判断路径是否存在,清空用户输入并返回
                    路径 = ''
                    画板.提示错误('搜索接口不存在, 或者不可用')
                    break
                elif 文档定路径标记:
                    # 用户要求以文档定路径
                    可用文档列表 = 搜索接口.搜索(搜索关键字=关键字,
                                                 搜文档=True,
                                                 搜路径=False,
                                                 限定数量=-1,  # 不限定文档的数量
                                                 画板=画板.副本)
                    if 可用文档列表:
                        if 可用文档列表.总数 > 0:
                            截断标记: bool = False
                            候选项上限值 = max(候选项上限, 1)

                            if not 路径约束小写化:
                                预计处理时长: int = 0
                                if 可用文档列表.总数 >= 20000:
                                    预计处理时长 = 440
                                elif 可用文档列表.总数 >= 10000:
                                    预计处理时长 = 100
                                elif 可用文档列表.总数 >= 9000:
                                    预计处理时长 = 84
                                elif 可用文档列表.总数 >= 8000:
                                    预计处理时长 = 60
                                elif 可用文档列表.总数 >= 7000:
                                    预计处理时长 = 50
                                elif 可用文档列表.总数 >= 6000:
                                    预计处理时长 = 40
                                elif 可用文档列表.总数 >= 5000:
                                    预计处理时长 = 25
                                elif 可用文档列表.总数 >= 4000:
                                    预计处理时长 = 20
                                elif 可用文档列表.总数 >= 3000:
                                    预计处理时长 = 11
                                elif 可用文档列表.总数 >= 2000:
                                    预计处理时长 = 4

                                if 预计处理时长 > 0:
                                    风险决策: str = 交互接口类.发起文本交互(
                                        输入提示=f"满足您指定关键字({黄字(关键字)})的文档有 {黄字(可用文档列表.总数)},"
                                                 f"预计处理时间大于{黄字(预计处理时长)}s："
                                                 f"（{红字('y: 继续')}；{绿字('r：重新搜索')}）",
                                        限定范围='YyRr',
                                        画板=画板.副本).lower()
                                    if '0' == 风险决策:
                                        # 用户要求退出程序
                                        exit(0)
                                    elif 'y' != 风险决策:
                                        # 如果用户要求重新搜索
                                        continue

                            交互端 = 交互接口类()
                            可用路径字典: dict[str,list[str]] = {} # 以路径为 key, 文档名组成的 list 为值 建立一个字典

                            # region 循环处理每一个搜索到的文档,如果文档满足要求,则将其添加到 可用路径字典 中备用
                            for 可用文档 in 可用文档列表.结果列表:
                                约束满足: bool = True
                                if 路径约束小写化:
                                    右半截: str = 可用文档.lower()
                                    for 约束 in 路径约束小写化:
                                        右半截 = 右半截.partition(约束)[2]
                                        if '\\' not in 右半截 and '/' not in 右半截:
                                            # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                            约束满足 = False
                                            break
                                if 约束满足:
                                    确认排除: bool = False
                                    if 排除规则:
                                        if sum([(1 if 规则(可用文档) else 0) for 规则 in 排除规则]) > 0:
                                            确认排除 = True

                                    if not 确认排除:
                                        这个文档路径, 这个文档名 = _os.path.split(可用文档)
                                        if 这个文档路径:
                                            if 这个文档路径 not in 可用路径字典:
                                                可用路径字典[这个文档路径] = []
                                            if 这个文档名:
                                                if 这个文档名 not in 可用路径字典[这个文档路径]:
                                                    可用路径字典[这个文档路径].append(这个文档名)

                            if 候选项上限 > 0 and len(可用路径字典) > 候选项上限值:
                                截断标记 = True
                            # endregion

                            # region 循环 可用路径字典 中的路径和文档,将其整理到交互选项中以供交互使用
                            if 可用路径字典:
                                可用路径字典路径列表: list[str] = [key for key in 可用路径字典.keys()]
                                if len(可用路径字典路径列表) <= 12:
                                    可用路径字典路径列表 = sorted(可用路径字典路径列表, key=len)
                                else:
                                    可用路径字典路径列表 = sorted(可用路径字典路径列表, key=len, reverse=True)

                                if 截断标记:
                                    可用路径字典路径列表 = 可用路径字典路径列表[:候选项上限值]

                                # 添加路径候选项
                                for key in 可用路径字典路径列表:
                                    交互端.添加选项(选项=key,
                                                    备注='\n'.join(sorted(可用路径字典[key],key=len)))

                                # 添加一个额外选项,供用户反悔
                                交互端.添加选项分隔行()
                                交互端.添加选项(代号='r',
                                                选项='重新指定/搜索\n'
                                                     f'仅支持 {绿字("*")} 通配符\n'
                                                     f'可以使用 {绿字("f=关键字")} 以列出包含指定文档的路径',
                                                功能选项标记=True,
                                                修饰方法=黄字)
                                if 功能选项:
                                    for 选项 in 功能选项:
                                        选项.属于功能选项 = True
                                        if 选项.修饰方法 is None:
                                            选项.修饰方法 = 黄字
                                        交互端.添加选项(选项=选项)

                                操作说明: list = [
                                    f'您输入的关键字为: {绿字(用户输入)}; 以下列出了符合条件的路径供您选择']

                                选择结果 = 交互端.发起选项交互(输入提示='请选择路径代号(0:退出)',
                                                               操作说明=操作说明,
                                                               兴趣字=路径约束 + [关键字],
                                                               备注高亮兴趣字=True,
                                                               选项表名称=选项表名称,
                                                               选项值列标题='路径',
                                                               画板=画板.副本)

                                if '0' in 选择结果.代号:
                                    # 用户要求退出
                                    路径 = '0'
                                    break
                                elif 'r' in 选择结果.代号:
                                    # 用户要求重新选择
                                    continue
                                elif 选择结果.选项:
                                    if 选择结果.选项[0] in 可用路径字典路径列表:
                                        路径 = 选择结果.选项[0]
                                    else:
                                        路径 = 选择结果.代号[0]

                                    # 用户选择了结果,退出循环
                                    break
                            else:
                                # 没有满足约束条件的搜索结果,请用户重新输入, 以便重新搜索
                                画板.消息(
                                    '不存在满足条件的路径选项, 可能的原因是搜索关键字过于宽泛,您可以提供更多关键字信息以便重试')
                            # endregion
                else:
                    # 如果搜索接口可用,则尝试搜索并列出符合条件的路径供用户选择
                    可用路径列表 = 搜索接口.搜索(搜索关键字=关键字,
                                                 搜文档=False,
                                                 搜路径=True,
                                                 限定数量=搜索条数限制 if 候选项上限 > 0 else -1,
                                                 画板=画板.副本)
                    if 可用路径列表:
                        if 可用路径列表.总数 > 0:
                            截断标记: bool = False
                            路径选项数量: int = 0

                            if not 路径约束小写化:
                                预计处理时长: int = 0
                                if 可用路径列表.总数 >= 20000:
                                    预计处理时长 = 440
                                elif 可用路径列表.总数 >= 10000:
                                    预计处理时长 = 100
                                elif 可用路径列表.总数 >= 9000:
                                    预计处理时长 = 84
                                elif 可用路径列表.总数 >= 8000:
                                    预计处理时长 = 60
                                elif 可用路径列表.总数 >= 7000:
                                    预计处理时长 = 50
                                elif 可用路径列表.总数 >= 6000:
                                    预计处理时长 = 40
                                elif 可用路径列表.总数 >= 5000:
                                    预计处理时长 = 25
                                elif 可用路径列表.总数 >= 4000:
                                    预计处理时长 = 20
                                elif 可用路径列表.总数 >= 3000:
                                    预计处理时长 = 11
                                elif 可用路径列表.总数 >= 2000:
                                    预计处理时长 = 4

                                if 预计处理时长 > 0:
                                    风险决策: str = 交互接口类.发起文本交互(
                                        输入提示=f"满足您指定关键字({黄字(关键字)})的选项有 {黄字(可用路径列表.总数)},"
                                                 f"预计处理时间大于{黄字(预计处理时长)}s："
                                                 f"（{红字('y: 继续')}；{绿字('r：重新搜索')}）",
                                        限定范围='YyRr',
                                        画板=画板.副本).lower()
                                    if '0' == 风险决策:
                                        # 用户要求退出程序
                                        exit(0)
                                    elif 'y' != 风险决策:
                                        # 如果用户要求重新搜索
                                        continue

                            交互端 = 交互接口类()
                            路径列表: list[str] = []
                            候选项上限值: int = max(候选项上限, 1)
                            for 可用路径 in 可用路径列表.结果列表:
                                if 路径选项数量 >= 候选项上限值:
                                    截断标记 = True
                                    break

                                约束满足: bool = True
                                if 路径约束小写化:
                                    右半截: str = 可用路径.lower()
                                    for 约束 in 路径约束小写化:
                                        右半截 = 右半截.partition(约束)[2]
                                        if '\\' not in 右半截 and '/' not in 右半截:
                                            # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                            约束满足 = False
                                            break
                                if 约束满足:
                                    确认排除: bool = False
                                    if 排除规则:
                                        if sum([(1 if 规则(可用路径) else 0) for 规则 in 排除规则]) > 0:
                                            确认排除 = True

                                    if not 确认排除:
                                        路径列表.append(f'{可用路径}')
                                        if 候选项上限 > 0:
                                            路径选项数量 += 1

                            if 路径列表:
                                if len(路径列表) <= 12:
                                    交互端.添加选项(选项=sorted(路径列表, key=len))
                                else:
                                    交互端.添加选项(选项=sorted(路径列表, key=len, reverse=True))

                                if 可用路径列表.截断 or 截断标记:
                                    if 可用路径列表.截断:
                                        交互端.添加选项(代号='...',
                                                        选项=f'搜索结果未完全呈现, 共 >={搜索条数限制} 条',
                                                        修饰方法=红字,
                                                        可选=False)
                                    else:
                                        交互端.添加选项(代号='...',
                                                        选项=f'搜索结果未完全呈现, 共 {可用路径列表.总数} 条',
                                                        修饰方法=红字,
                                                        可选=False)

                                # 添加一个额外选项,供用户反悔
                                交互端.添加选项分隔行()
                                交互端.添加选项(代号='r',
                                                选项='重新指定/搜索\n'
                                                     f'仅支持 {绿字("*")} 通配符\n'
                                                     f'可以使用 {绿字("f=关键字")} 以文档定路径',
                                                功能选项标记=True,
                                                修饰方法=黄字)
                                if 功能选项:
                                    for 选项 in 功能选项:
                                        选项.属于功能选项 = True
                                        if 选项.修饰方法 is None:
                                            选项.修饰方法 = 黄字
                                        交互端.添加选项(选项=选项)

                                操作说明: list = [
                                    f'您输入的关键字为: {绿字(用户输入)}; 以下列出了符合条件的路径供您选择']

                                选择结果 = 交互端.发起选项交互(输入提示='请选择路径代号(0:退出)',
                                                               操作说明=操作说明,
                                                               兴趣字=路径约束 + [关键字],
                                                               选项表名称=选项表名称,
                                                               选项值列标题='路径',
                                                               画板=画板.副本)

                                if '0' in 选择结果.代号:
                                    # 用户要求退出
                                    路径 = '0'
                                    break
                                elif 'r' in 选择结果.代号:
                                    # 用户要求重新选择
                                    continue
                                elif 选择结果.选项:
                                    if 选择结果.选项[0] in 路径列表:
                                        路径 = 选择结果.选项[0]
                                    else:
                                        路径 = 选择结果.代号[0]

                                    # 用户选择了结果,退出循环
                                    break
                            else:
                                # 没有满足约束条件的搜索结果,请用户重新输入, 以便重新搜索
                                画板.消息('不存在满足条件的路径选项, '
                                          '可能的原因是搜索关键字过于宽泛, '
                                          '您可以提供更多关键字信息以便重试')
                        elif 可用路径列表.状态码 != 0 and 可用路径列表.状态码 != 200:
                            画板.提示错误(f'搜索接口反馈错误:{可用路径列表.状态码}')
                            if 可用路径列表.错误消息:
                                画板.消息(可用路径列表.错误消息)
                            # 搜索引擎出现异常,无法验证用户输入是否有效,清空之, 再次尝试无意义
                            路径 = ''
                            break
                        else:
                            # 没有搜索到有效结果,则返回要求用户重新输入, 以便重新搜索
                            画板.消息('未搜索到有效路径选项')
                    else:
                        # 搜索结果未知,直接使用用户输入的值,再次尝试无意义
                        画板.消息('搜索引擎返回未知结果')
                        路径 = ''
                        break
        return 路径

    @classmethod
    def 指定选择文档(cls,
                     输入提示: str = None,
                     搜索关键字: str = None,
                     候选项上限: int = 50,
                     选项表名称: str = None,
                     搜索接口: 搜索接口类 = None,
                     功能选项: 交互选项类 or list[交互选项类] = None,
                     排除规则: _Callable[[str], bool] or list[_Callable[[str], bool]] = None,
                     多选: bool = False,
                     画板: 打印模板 = None) -> list[str]:
        """
        向用户发起交互,以获取用户指定的文档
        :param 输入提示: 提示用户输入时的提示内容
        :param 搜索关键字: 可以指定初始搜索关键字
        :param 候选项上限: 如果存在候选项,则限制候选项数量,如果此参数值 <= 0, 则不设限
        :param 选项表名称: 发起用户交互时的表名称
        :param 搜索接口: 协助用户搜索文档的接口
        :param 功能选项: 提供功能选项,以供用户选择对应功能,并返回到上级功能层
        :param 排除规则: 对每一个候选文档运用排除规则[如果规则可用],如果规则返回True,则该候选项被排除
        :param 多选: 是否允许选择多个文档
        :param 画板: 提供用户交互输出的渠道
        :return: 用户选择的文档路径列表,以及给定的功能选项中被用户选择的选项的代号
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(cls, cls.指定选择文档)

        输入提示 = str(输入提示 if 输入提示 else '').strip()
        输入提示 = 输入提示 if 输入提示 else '请指定文档或者文档关键字(0:退出): '

        搜索关键字 = str(搜索关键字 if 搜索关键字 else '').strip()

        候选项上限 = 候选项上限 if isinstance(候选项上限, int) else 50

        功能选项 = 功能选项 if isinstance(功能选项, list) else [功能选项]
        功能选项 = [项 for 项 in 功能选项 if isinstance(项, 交互选项类) and 项.有效]

        排除规则 = 排除规则 if isinstance(排除规则, list) else [排除规则]
        排除规则 = [规则 for 规则 in 排除规则 if callable(规则)]

        路径约束: list[str]
        关键字: str

        文档列表: list[str]

        列出指定路径下的文档: bool = False
        列出包含指定文档的路径下的文档: bool = False

        轮循次数: int = 0
        用户输入: str
        搜索条数限制: int = max(1000, 候选项上限 * 10)
        while True:
            # 轮循计数
            轮循次数 += 1

            if 轮循次数 == 1 and 搜索关键字 and '0' != 搜索关键字:
                # 如果第一次轮循,并且存在搜索关键字, 则直接使用搜索关键字展开搜索
                用户输入 = 搜索关键字
            else:
                # 否则向用户发起交互, 要求用户指定搜索关键字
                用户输入 = (cls.发起文本交互(输入提示=输入提示, 画板=画板)).strip()

            # 如果用户输入的是 f=关键字 这种格式的内容, 说明用户需要列出指定路径下的文档以供选择
            列出指定路径下的文档 = False
            列出包含指定文档的路径下的文档 = False
            if len(用户输入) > 3 and 用户输入[0:3].lower() in ['ff=', 'ff＝']:
                列出包含指定文档的路径下的文档 = True
                用户输入 = 用户输入[3:]
            elif len(用户输入) > 2 and 用户输入[0:2].lower() in ['f=', 'f＝']:
                列出指定路径下的文档 = True
                用户输入 = 用户输入[2:]
            if '0' == 用户输入:
                文档列表 = ['0']
                break
            else:
                # region 分解用户的输入
                用户输入 = 用户输入.replace('｜', '|').strip('|')
                if '|' in 用户输入:
                    # 这个用户输入中包括了约束项
                    用户输入分解: list[str] = [项.strip() for 项 in 用户输入.split('|')]
                    关键字 = 用户输入分解[-1]
                    路径约束 = 用户输入分解[:-1]
                else:
                    # 这个用户输入不包括约束项
                    关键字 = 用户输入
                    路径约束 = []
                if 路径约束:
                    路径约束小写化 = [约束.lower() for 约束 in 路径约束]
                else:
                    路径约束小写化 = []

                文档列表 = [关键字]
                # endregion

                if not isinstance(搜索接口, 搜索接口类) or 搜索接口.不可用:
                    # 搜索接口类型不符合要求, 或者搜索接口不可用, 无法验证用户输入是否存在,清空之
                    文档列表 = []
                    画板.提示错误('搜索接口不存在, 或者不可用')
                    break
                elif 列出指定路径下的文档:
                    # 用户要求列出指定路径下的所有文档以供选择
                    # region 根据用户指定的关键字,搜索并整理兴趣路径
                    兴趣路径列表: list[str] = []

                    # 搜索满足用户指定关键字及约束的路径
                    兴趣路径搜索结果: 搜索结果类 = 搜索接口.搜索(搜索关键字=关键字,
                                                             搜文档=False,
                                                             搜路径=True,
                                                             限定数量=-1,
                                                             画板=画板.副本)
                    if 兴趣路径搜索结果.状态码 not in [0, 200]:
                        # 如果搜索时遇到了异常
                        画板.提示错误(f'搜索路径时遇到异常: {兴趣路径搜索结果.错误消息}')
                        continue
                    else:
                        if 兴趣路径搜索结果.总数 < 1:
                            画板.消息(f'指定的关键字 {红字(关键字)} 未能搜索到有效路径 !!!')
                            continue
                        else:
                            # 检查指定的路径是否满足约束条件
                            约束满足: bool
                            右半截: str
                            for 路径 in 兴趣路径搜索结果.结果列表:
                                约束满足 = True
                                if 路径约束小写化:
                                    右半截 = 路径.lower()
                                    for 约束 in 路径约束小写化:
                                        右半截 = 右半截.partition(约束)[2]
                                        if '\\' not in 右半截 and '/' not in 右半截:
                                            # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                            约束满足 = False
                                            break
                                if 约束满足:
                                    兴趣路径列表.append(路径)
                    # endregion

                    # region 遍历每个兴趣路径,查找其下的文档并记录下来
                    if not 兴趣路径列表:
                        # 没有有效的兴趣路径
                        画板.消息(f'指定的关键字 {红字(关键字)} 未能搜索到有效路径 !!!')
                        continue
                    else:
                        文档列表 = []
                        路径文档字典: dict[str: list[str]] = {}
                        确认排除: bool
                        候选项上限值 = max(候选项上限, 1)
                        截断标记: bool = False
                        文档选项数量: int = 0
                        for 路径 in 兴趣路径列表:
                            if 文档选项数量 >= 候选项上限值:
                                截断标记 = True
                                break

                            备选文档列表 = 搜索接口.列出文档(路径=路径, 画板=画板.副本)
                            if 备选文档列表:
                                if 路径 not in 路径文档字典:
                                    路径文档字典[路径] = []
                                for 文档 in 备选文档列表:
                                    if 文档选项数量 >= 候选项上限值:
                                        截断标记 = True
                                        break

                                    确认排除 = False
                                    if 排除规则:
                                        if sum([(1 if 规则(文档) else 0) for 规则 in 排除规则]) > 0:
                                            确认排除 = True
                                    if not 确认排除:
                                        路径文档字典[路径].append(文档)
                                        文档列表.append(文档)
                                        if 候选项上限 > 0:
                                            文档选项数量 += 1
                    # endregion

                    # region 将文档与路径信息打印出来供用户选择
                    if not 路径文档字典:
                        # 没有满足约束条件的搜索结果,请用户重新输入, 以便重新搜索
                        画板.消息('不存在满足条件的文档选项, '
                                  '您可以确认并修正关键字信息以重试')
                    else:
                        交互端 = 交互接口类()

                        # 对每一个路径下的文档，根据文档命名的长度，从短到长进行排序，然后打印以供交互
                        for 路径 in 路径文档字典:
                            兴趣路径列表 = 路径文档字典[路径]
                            if 兴趣路径列表:
                                兴趣路径列表 = sorted(兴趣路径列表, key=len)
                                文档数量 = len(兴趣路径列表)
                                if 文档数量 == 1:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注=']')
                                elif 文档数量 == 2:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注='┐')
                                    交互端.添加选项(选项=兴趣路径列表[1], 备注='┘')
                                else:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注='┐')
                                    for 文档 in 兴趣路径列表[1:-1]:
                                        交互端.添加选项(选项=文档, 备注='|')
                                    交互端.添加选项(选项=兴趣路径列表[-1], 备注='┘')

                        if 截断标记:
                            交互端.添加选项(代号='...',
                                            选项=f'搜索结果未完全呈现 ! ! !',
                                            修饰方法=红字,
                                            可选=False)

                        # 添加一个额外选项,供用户反悔
                        交互端.添加选项分隔行()
                        交互端.添加选项(代号='r',
                                        选项='重新指定/搜索\n'
                                             f'仅支持 {绿字("*")} 通配符\n'
                                             f'可以使用 {绿字("f=关键字")} 以列出指定文件夹内的文档\n'
                                             f'可以使用 {绿字("ff=关键字")} 以列出包含指定文档的文件夹内的文档',
                                        功能选项标记=True,
                                        修饰方法=黄字)
                        if 功能选项:
                            for 选项 in 功能选项:
                                选项.属于功能选项 = True
                                if 选项.修饰方法 is None:
                                    选项.修饰方法 = 黄字
                                交互端.添加选项(选项=选项)

                        操作说明: list = [
                            f'您输入的关键字为: {绿字(用户输入)}; 在此列出了符合条件的文档供您选择']

                        选择结果 = 交互端.发起选项交互(输入提示='请选择文档代号(0:退出):',
                                                       操作说明=操作说明,
                                                       兴趣字=路径约束 + [关键字],
                                                       多选=多选,
                                                       选项表名称=选项表名称,
                                                       选项值列标题='文档',
                                                       画板=画板.副本)
                        if '0' in 选择结果.代号:
                            # 用户要求退出
                            文档列表 = ['0']
                            break
                        elif 'r' in 选择结果.代号:
                            # 用户要求重新选择/搜索
                            continue
                        elif 选择结果.选项:
                            选择结果集: list[str] = []
                            for 序号 in range(len(选择结果.选项)):
                                if 选择结果.选项[序号] in 文档列表:
                                    选择结果集.append(选择结果.选项[序号])
                                else:
                                    选择结果集.append(选择结果.代号[序号])
                            文档列表 = 选择结果集
                            # 用户选择了结果,退出循环
                            break
                    # endregion
                elif 列出包含指定文档的路径下的文档:
                    # 用户要求列出包含指定文档的所有路径下的所有文档以供选择
                    # region 根据用户关键字，搜索兴趣文档, 并整理成兴趣路径
                    兴趣文档列表: list[str] = []
                    兴趣文档搜索结果: 搜索结果类 = 搜索接口.搜索(搜索关键字=关键字,
                                                                 搜文档=True,
                                                                 搜路径=False,
                                                                 限定数量=-1,
                                                                 画板=画板.副本)
                    # 根据约束要求,整理搜索到的兴趣文档
                    if 兴趣文档搜索结果.状态码 not in [0, 200]:
                        # 如果搜索时遇到了异常
                        画板.提示错误(f'搜索路径时遇到异常: {兴趣文档搜索结果.错误消息}')
                        continue
                    else:
                        if 兴趣文档搜索结果.总数 < 1:
                            画板.消息(f'指定的关键字 {红字(关键字)} 未能搜索到有效文档 !!!')
                            continue
                        else:
                            # 检查搜索到的兴趣文档是否满足约束条件
                            约束满足: bool
                            右半截: str
                            for 文档 in 兴趣文档搜索结果.结果列表:
                                约束满足 = True
                                if 路径约束小写化:
                                    右半截 = 文档.lower()
                                    for 约束 in 路径约束小写化:
                                        右半截 = 右半截.partition(约束)[2]
                                        if '\\' not in 右半截 and '/' not in 右半截:
                                            # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                            约束满足 = False
                                            break
                                if 约束满足:
                                    兴趣文档列表.append(文档)

                    # 根据兴趣文档,整理出兴趣路径
                    兴趣路径列表: list[str] = []
                    if 兴趣文档列表:
                        for 文档 in 兴趣文档列表:
                            路径 = _os.path.split(文档)[0]
                            if 路径 not in 兴趣路径列表:
                                兴趣路径列表.append(路径)
                    else:
                        # 没有有效的兴趣文档
                        画板.消息(f'指定的关键字 {红字(关键字)} 未能搜索到有效的文档 !!!')
                        continue
                    # endregion

                    # region 根据前文整理出来的兴趣路径,整理出其下的文档
                    if not 兴趣路径列表:
                        # 没有有效的兴趣路径
                        画板.消息(f'指定的关键字 {红字(关键字)} 未能定位到有效的文档路径 !!!')
                        continue
                    else:
                        # 遍历每个兴趣路径,查找其下的文档并记录下来
                        文档列表 = []
                        路径文档字典: dict[str: list[str]] = {}
                        确认排除: bool
                        候选项上限值 = max(候选项上限, 1)
                        截断标记: bool = False
                        文档选项数量: int = 0
                        for 路径 in 兴趣路径列表:
                            if 文档选项数量 >= 候选项上限值:
                                截断标记 = True
                                break

                            备选文档列表 = 搜索接口.列出文档(路径=路径, 画板=画板.副本)
                            if 备选文档列表:
                                if 路径 not in 路径文档字典:
                                    路径文档字典[路径] = []
                                for 文档 in 备选文档列表:
                                    if 文档选项数量 >= 候选项上限值:
                                        截断标记 = True
                                        break

                                    确认排除 = False
                                    if 排除规则:
                                        if sum([(1 if 规则(文档) else 0) for 规则 in 排除规则]) > 0:
                                            确认排除 = True
                                    if not 确认排除:
                                        路径文档字典[路径].append(文档)
                                        文档列表.append(文档)
                                        if 候选项上限 > 0:
                                            文档选项数量 += 1
                    # endregion

                    # region 将文档与路径信息打印出来供用户选择
                    if not 路径文档字典:
                        # 没有满足约束条件的搜索结果,请用户重新输入, 以便重新搜索
                        画板.消息('不存在满足条件的文档选项, '
                                  '您可以确认并修正关键字信息以重试')
                    else:
                        交互端 = 交互接口类()

                        # 对每一个路径下的文档，根据文档命名的长度，从短到长进行排序，然后打印以供交互
                        for 路径 in 路径文档字典:
                            兴趣路径列表 = 路径文档字典[路径]
                            if 兴趣路径列表:
                                兴趣路径列表 = sorted(兴趣路径列表, key=len)
                                文档数量 = len(兴趣路径列表)
                                if 文档数量 == 1:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注=']')
                                elif 文档数量 == 2:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注='┐')
                                    交互端.添加选项(选项=兴趣路径列表[1], 备注='┘')
                                else:
                                    交互端.添加选项(选项=兴趣路径列表[0], 备注='┐')
                                    for 文档 in 兴趣路径列表[1:-1]:
                                        交互端.添加选项(选项=文档, 备注='|')
                                    交互端.添加选项(选项=兴趣路径列表[-1], 备注='┘')

                        if 截断标记:
                            交互端.添加选项(代号='...',
                                            选项=f'搜索结果未完全呈现 ! ! !',
                                            修饰方法=红字,
                                            可选=False)

                        # 添加一个额外选项,供用户反悔
                        交互端.添加选项分隔行()
                        交互端.添加选项(代号='r',
                                        选项='重新指定/搜索\n'
                                             f'仅支持 {绿字("*")} 通配符\n'
                                             f'可以使用 {绿字("f=关键字")} 以列出指定文件夹内的文档\n'
                                             f'可以使用 {绿字("ff=关键字")} 以列出包含指定文档的文件夹内的文档',
                                        功能选项标记=True,
                                        修饰方法=黄字)
                        if 功能选项:
                            for 选项 in 功能选项:
                                选项.属于功能选项 = True
                                if 选项.修饰方法 is None:
                                    选项.修饰方法 = 黄字
                                交互端.添加选项(选项=选项)

                        操作说明: list = [
                            f'您输入的关键字为: {绿字(用户输入)}; 在此列出了符合条件的文档供您选择']

                        选择结果 = 交互端.发起选项交互(输入提示='请选择文档代号(0:退出):',
                                                       操作说明=操作说明,
                                                       兴趣字=路径约束 + [关键字],
                                                       多选=多选,
                                                       选项表名称=选项表名称,
                                                       选项值列标题='文档',
                                                       画板=画板.副本)
                        if '0' in 选择结果.代号:
                            # 用户要求退出
                            文档列表 = ['0']
                            break
                        elif 'r' in 选择结果.代号:
                            # 用户要求重新选择/搜索
                            continue
                        elif 选择结果.选项:
                            选择结果集: list[str] = []
                            for 序号 in range(len(选择结果.选项)):
                                if 选择结果.选项[序号] in 文档列表:
                                    选择结果集.append(选择结果.选项[序号])
                                else:
                                    选择结果集.append(选择结果.代号[序号])
                            文档列表 = 选择结果集
                            # 用户选择了结果,退出循环
                            break
                    # endregion
                else:
                    # 用户只输入了文档关键字, 则进行如下搜索
                    if 搜索接口.存在文档(文档=文档列表[0], 画板=画板.副本):
                        # 如果用户搜索的关键字是切实存在的文档，则检查其是否满足路径约束
                        约束满足: bool
                        右半截: str
                        if 路径约束小写化:
                            约束满足 = True
                            右半截 = 文档列表[0].lower()
                            for 约束 in 路径约束小写化:
                                右半截 = 右半截.partition(约束)[2]
                                if '\\' not in 右半截 and '/' not in 右半截:
                                    # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                    约束满足 = False
                                    break
                            if 约束满足:
                                # 当前的文档满足约束条件, 为有效文档, 退出交互循环
                                break
                        else:
                            # 没有约束条件, 当前的文档有效, 退出交互循环
                            break

                    # 如果判定文档不存在
                    可用文档列表 = 搜索接口.搜索(搜索关键字=关键字,
                                                 搜文档=True,
                                                 搜路径=False,
                                                 限定数量=搜索条数限制 if 候选项上限 > 0 else -1,
                                                 画板=画板.副本)
                    if 可用文档列表:
                        if 可用文档列表.总数 > 0:
                            截断标记: bool = False
                            文档选项数量: int = 0

                            if not 路径约束小写化:
                                预计处理时长: int = 0
                                if 可用文档列表.总数 >= 20000:
                                    预计处理时长 = 440
                                elif 可用文档列表.总数 >= 10000:
                                    预计处理时长 = 100
                                elif 可用文档列表.总数 >= 9000:
                                    预计处理时长 = 84
                                elif 可用文档列表.总数 >= 8000:
                                    预计处理时长 = 60
                                elif 可用文档列表.总数 >= 7000:
                                    预计处理时长 = 50
                                elif 可用文档列表.总数 >= 6000:
                                    预计处理时长 = 40
                                elif 可用文档列表.总数 >= 5000:
                                    预计处理时长 = 25
                                elif 可用文档列表.总数 >= 4000:
                                    预计处理时长 = 20
                                elif 可用文档列表.总数 >= 3000:
                                    预计处理时长 = 11
                                elif 可用文档列表.总数 >= 2000:
                                    预计处理时长 = 4

                                if 预计处理时长 > 0:
                                    风险决策: str = 交互接口类.发起文本交互(
                                        输入提示=f"满足您指定关键字({黄字(关键字)})的选项有 {黄字(可用文档列表.总数)},"
                                                 f"预计处理时间大于{黄字(预计处理时长)}s："
                                                 f"（{红字('y: 继续')}；{绿字('r：重新搜索')}）",
                                        限定范围='YyRr',
                                        画板=画板.副本).lower()
                                    if '0' == 风险决策:
                                        # 用户要求退出程序
                                        exit(0)
                                    elif 'y' != 风险决策:
                                        # 如果用户要求重新搜索
                                        continue

                            文档列表 = []
                            候选项上限值 = max(候选项上限, 1)
                            确认排除: bool
                            for 可用文档 in 可用文档列表.结果列表:
                                if 文档选项数量 >= 候选项上限值:
                                    截断标记 = True
                                    break

                                约束满足 = True
                                if 路径约束小写化:
                                    右半截 = 可用文档.lower()
                                    for 约束 in 路径约束小写化:
                                        右半截 = 右半截.partition(约束)[2]
                                        if '\\' not in 右半截 and '/' not in 右半截:
                                            # 如果 约束 右侧不存在路径分隔符,则说明此约束出现位置不在路径中
                                            约束满足 = False
                                            break
                                if 约束满足:
                                    确认排除 = False
                                    if 排除规则:
                                        if sum([(1 if 规则(可用文档) else 0) for 规则 in 排除规则]) > 0:
                                            确认排除 = True

                                    if not 确认排除:
                                        文档列表.append(f'{可用文档}')
                                        if 候选项上限 > 0:
                                            文档选项数量 += 1

                            if 文档列表:
                                交互端 = 交互接口类()
                                if len(文档列表) <= 12:
                                    交互端.添加选项(选项=sorted(文档列表, key=len))
                                else:
                                    交互端.添加选项(选项=sorted(文档列表, key=len, reverse=True))

                                if 可用文档列表.截断 or 截断标记:
                                    if 可用文档列表.截断:
                                        交互端.添加选项(代号='...',
                                                        选项=f'搜索结果未完全呈现, 共 >={搜索条数限制} 条',
                                                        修饰方法=红字,
                                                        可选=False)
                                    else:
                                        交互端.添加选项(代号='...',
                                                        选项=f'搜索结果未完全呈现, 共 {可用文档列表.总数} 条',
                                                        修饰方法=红字,
                                                        可选=False)

                                # 添加一个额外选项,供用户反悔
                                交互端.添加选项(选项='-')
                                交互端.添加选项(代号='r',
                                                选项='重新指定/搜索\n'
                                                     f'仅支持 {绿字("*")} 通配符\n'
                                                     f'可以使用 {绿字("f=关键字")} 以列出指定文件夹内的文档\n'
                                                     f'可以使用 {绿字("ff=关键字")} 以列出包含指定文档的文件夹内的文档',
                                                功能选项标记=True,
                                                修饰方法=黄字)
                                if 功能选项:
                                    for 选项 in 功能选项:
                                        选项.属于功能选项 = True
                                        if 选项.修饰方法 is None:
                                            选项.修饰方法 = 黄字
                                        交互端.添加选项(选项=选项)

                                操作说明: list = [
                                    f'您输入的关键字为: {绿字(用户输入)}; 在此列出了符合条件的文档供您选择']

                                选择结果 = 交互端.发起选项交互(输入提示='请选择文档代号(0:退出):',
                                                               操作说明=操作说明,
                                                               兴趣字=路径约束 + [关键字],
                                                               多选=多选,
                                                               选项表名称=选项表名称,
                                                               选项值列标题='文档',
                                                               画板=画板.副本)
                                if '0' in 选择结果.代号:
                                    # 用户要求退出
                                    文档列表 = ['0']
                                    break
                                elif 'r' in 选择结果.代号:
                                    # 用户要求重新选择/搜索
                                    continue
                                elif 选择结果.选项:
                                    选择结果集: list[str] = []
                                    for 序号 in range(len(选择结果.选项)):
                                        if 选择结果.选项[序号] in 文档列表:
                                            选择结果集.append(选择结果.选项[序号])
                                        else:
                                            选择结果集.append(选择结果.代号[序号])
                                    文档列表 = 选择结果集
                                    # 用户选择了结果,退出循环
                                    break
                            else:
                                # 没有满足约束条件的搜索结果,请用户重新输入, 以便重新搜索
                                画板.消息('不存在满足条件的文档选项, '
                                          '可能的原因是搜索关键字过于宽泛,'
                                          '您可以提供更多关键字信息以便重试')
                        elif 可用文档列表.状态码 != 0 and 可用文档列表.状态码 != 200:
                            画板.提示错误(f'搜索接口反馈错误:{可用文档列表.状态码}')
                            if 可用文档列表.错误消息:
                                画板.消息(可用文档列表.错误消息)
                            # 搜索引擎出现异常,无法验证用户输入是否有效,清空之,再次尝试无意义
                            文档列表 = []
                            break
                        else:
                            # 搜索结果无效,则返回要求用户重新输入
                            画板.消息('未搜索到有效文档选项')
                    else:
                        # 搜索结果未知,直接使用用户输入的值,再次尝试无意义
                        画板.消息('搜索引擎返回未知结果')
                        文档列表 = []
                        break

        return 文档列表

    @staticmethod
    def 选择文档(初始路径: str = None,
                 多选: bool = False,
                 输入提示: str = None,
                 兴趣字: list[str] or str = None,
                 选项表名称: str = None,
                 路径排除规则: _Callable[[str], bool] or list[_Callable[[str], bool]] = None,
                 文档排除规则: _Callable[[str], bool] or list[_Callable[[str], bool]] = None,
                 搜索接口: 搜索接口类 = None,
                 画板: 打印模板 = None) -> list[str]:
        """
        与用户发起交互,引导用户指定选择路径后，选择其下的兴趣文档
        :param 初始路径: 引导用户在参考路径下操作
        :param 多选: 是否允许用户选择多个文档
        :param 输入提示: 提示用户选择文档的信息
        :param 兴趣字: 在文档名中您关注的字符内容
        :param 选项表名称: 发起用户交互时的表名称
        :param 路径排除规则: 在定位路径时, 对每一个候选路径运用排除规则[如果规则可用],如果规则返回True,则该候选项被排除
        :param 文档排除规则: 在定位文档时,对每一个候选文档运用排除规则[如果规则可用],如果规则返回True,则该候选项被排除
        :param 搜索接口: 提供文档搜索功能, 协助用户快速定义文档
        :param 画板: 提供用户交互的输出渠道
        :return: 返回用户的选择的文档列表, 带全路径
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(交互接口类, 交互接口类.选择文档)

        # region 入参检查
        输入提示 = (输入提示 if 输入提示 else '').strip()
        输入提示 = 输入提示 if 输入提示 else '请选择文档（0:退出操作）: '

        路径排除规则 = 路径排除规则 if isinstance(路径排除规则, list) else [路径排除规则]
        路径排除规则 = [规则 for 规则 in 路径排除规则 if callable(规则)]

        文档排除规则 = 文档排除规则 if isinstance(文档排除规则, list) else [文档排除规则]
        文档排除规则 = [规则 for 规则 in 文档排除规则 if callable(规则)]

        搜索接口 = 搜索接口 if isinstance(搜索接口, 搜索接口类) else 搜索接口类()
        # endregion

        选择结果: list[str] = []

        # region 展开参考路径
        参考路径: str = 搜索接口.路径展开(路径=初始路径, 画板=画板.副本.缩进())
        # endregion

        # 提供用户选择文档的交互
        while True:
            if not (参考路径 and 搜索接口.存在路径(路径=参考路径, 画板=画板.副本)):
                # 如果参考路径不存在, 或者可以判断参考路径不存在
                画板.消息(f"当前路径(本地)为: .")
                参考路径 = 交互接口类.指定选择路径(输入提示='请指定文档路径或者路径关键字(0: 退出操作): ',
                                                   选项表名称 =选项表名称,
                                                   搜索接口=搜索接口,
                                                   排除规则=路径排除规则,
                                                   画板=画板)
                if '0' == 参考路径:
                    # 如果用户选择了退出,则退出
                    选择结果.append('0')
                    return 选择结果

            # region 准备待选择的文档列表
            文档列表: list[str]
            文档列表 = 搜索接口.列出文档(路径=参考路径, 限制数量=50, 画板=画板.副本)

            if 文档排除规则 and 文档列表:
                文档列表 = [文档 for 文档 in 文档列表 if sum([(1 if 规则(文档) else 0) for 规则 in 文档排除规则]) > 0]

            if not 文档列表:
                画板.消息(f'当前路径下没有可用的文档: {参考路径}')
                # 引导用户重新指定操作路径
                参考路径 = 交互接口类.指定选择路径(输入提示='请指定文档路径或者路径关键字(0: 退出操作): ',
                                                   选项表名称=选项表名称,
                                                   搜索接口=搜索接口,
                                                   画板=画板)
                if '0' == 参考路径:
                    # 如果用户选择了退出,则退出
                    选择结果.append('0')
                    return 选择结果
                continue
            # endregion

            # 如果文档列表存在,则解析候选文档路径和候选文档名列表
            候选文档路径: str
            候选文档名列表: list[str]
            样本文档 = 文档列表[0]
            候选文档路径 = _os.path.split(样本文档)[0]
            候选文档名列表 = [_os.path.split(文档)[1] for 文档 in 文档列表]

            交互端: 交互接口类 = 交互接口类()
            if len(候选文档名列表) <= 12:
                交互端.添加选项(选项=sorted(候选文档名列表))
            else:
                交互端.添加选项(选项=sorted(候选文档名列表, reverse=True))

            # 添加一个额外的选项,用于支持重新选择文档路径
            交互端.添加选项(选项='修改文档路径', 代号='c')

            # 发起用户交互
            用户选择 = 交互端.发起选项交互(多选=多选,
                                           操作说明=f"文档路径: {候选文档路径}",
                                           输入提示=输入提示,
                                           兴趣字=兴趣字,
                                           选项表名称=选项表名称,
                                           选项值列标题='文档',
                                           画板=画板.副本)
            if not 用户选择.代号:
                # 如果用户没有选择, 则重新发起新一轮交互引导
                continue

            if 'c' in 用户选择.代号 or 'C' in 用户选择.代号:
                # 用户要求修改文档路径, 则引导用户输入新的路径
                画板.消息(f'当前指定路径为[参考]: {候选文档路径}')
                参考路径 = 交互接口类.指定选择路径(输入提示='请指定文档路径或者路径关键字(0: 退出操作): ',
                                                   选项表名称=选项表名称,
                                                   搜索接口=搜索接口,
                                                   画板=画板)
                if '0' == 参考路径:
                    # 如果用户选择了退出,则退出
                    选择结果.append('0')
                    return 选择结果
            elif '0' in 用户选择.代号:
                # 如果用户选择了退出,则退出
                选择结果.append('0')
                return 选择结果
            else:
                # 处理用户选择的文档
                for 文档 in 用户选择.选项:
                    if 文档:
                        选择结果.append(_os.path.join(候选文档路径, 文档))

                # 如果用户存在输入
                if 选择结果:
                    return 选择结果
# endregion

class 入参基类:
    """
    这是一个命令行参数处理的基类,你可以像以下这样在该基类的基础上构造你的制定入参对象

    # 这是您的定制化入参类, 需要继承 本基类. 您唯二需要做的就是: 添加参数, 制定访问器
    class 命令行参数(入参基类):
        # 您需要在这里添加参数
        def __init__(self):
            # 初始化父类
            super().__init__()

            # 如果有需要,你可以提供接口说明
            self._接口说明 = '因为所以,科学道理'

            # 添加定制参数, 根据你的需要,添加你需要关注的入参参数信息
            # 参数名, 参数类型/None/list, 提示/帮助信息, 参数默认值
            self._添加参数('html', str, '指定要解析的 html 文档', './demo.html')
            self._添加参数('l', None, '如果存在 -l 参数,则返回文档列表')
            self._添加参数('usage', ['install', 'uninstall', 'upgrade'], '指定范围内限定的值作为用途', 'install')

            # 你可以定义你的个性化成员
            self.个性: 类型 = 值

        # 对于包含空格的字符串, 需要使用 "" 来表示字符串的整体
        # 对于字符串参数,符号 \" 会被解释 ",为了避免此类不希望的转换,你需要注意特别处理符号组合 \"
        # 一个可行的办法是, 如果你的字符串参数值中存在 \",而你又不是真正的需要一个 " 符号,则你可以考虑在传参前把符号 \ 替换为 /,然后在py脚本中做反向替换
        # 另一个,如果你希望传输的是一个路径信息,为了避免尾部出现\"的组合,你可以在bat/shell脚本中做如下处理:

        # :: 设置变量延迟加载(重要)
        # setlocal enabledelayedexpansion
        #
        # :: 扩充入参成为一个合法的路径,并去除两端的引号(如果有)
        # set tgtDir=%~dp1
        # :: 如果路径结尾是符号\, 则去除之
        # if "\" == "!tgtDir:~-1!" (set tgtDir=%tgtDir:~0,-1%)
        # :: 你可以这样将参数 tgtDir 传入py脚本
        # python myScript.py --tgtDir="%tgtDir%"

        # 您需要在这里制定参数访问器, 如果您不想定制访问器,您也可以通过 get 方法获取到指定名称的成员的值
        # 您可以通过 self.转换为属性范式(setter=True, 放入粘贴板=True) 方法快速生成对应于参数字典成员的属性范围,然后直接粘贴使用
        # region 访问器
        @property
        def html(self) -> str:
            return self.get('html')

        @html.setter
        def html(self, 值: str):
            self.set('html', 值)

        # endregion

        # 如果您不定义参数成员的访问器接口,你也可以通过 get or set 方法来获取和设置参数值,如下
        参数对象.get('html')
        参数对象.set('html', './example.html')

        # 根据需要,你可以在子类中重写父类的方法

    """

    class _参数结构类:
        def __init__(self,
                     名称: str = None,
                     类型: type = str,
                     无值型: bool = False,
                     提示: str = None,
                     默认值=None,
                     选项: list[str] = None):
            self.名称: str = 名称
            self.类型: type = 类型
            self.无值型: bool = 无值型
            self.__值 = 默认值
            self.__默认值 = 默认值
            self.提示: str = 提示
            self.选项: list[str] = 选项
            self.大写简写: str = ''
            self.小写简写: str = ''

        # region 访问器
        @property
        def 有效(self) -> bool:
            if self.名称:
                self.名称 = str(self.名称).strip()
                if self.名称 and isinstance(self.类型, type):
                    return True
            return False

        @property
        def 无效(self) -> bool:
            return not self.有效

        @property
        def 值(self):
            if isinstance(self.类型, type):
                if self.__值 is None:
                    return self.__默认值
                else:
                    return self.类型(self.__值)
            else:
                return self.__值

        @值.setter
        def 值(self, 值):
            if isinstance(self.类型, type):
                if 值 is None:
                    self.__值 = 值
                else:
                    self.__值 = self.类型(值)
            else:
                self.__值 = 值

            # 如果这个参数存在选项,则需要检查所赋的值是否在选项内
            if self.选项:
                if self.__值 not in self.选项:
                    self.__值 = None

        @property
        def 字串值(self) -> str:
            return '' if self.无效 or self.__值 is None else str(self.__值)

        @property
        def 数字值(self) -> int or float:
            return 0 if self.无效 or type(self.__值) not in [int, float] else self.__值

        @property
        def __class__(self) -> type:
            if isinstance(self.类型, type):
                return self.类型
            else:
                return type(self.__值)

        # endregion

        def __str__(self) -> str:
            return self.字串值

        def __int__(self) -> int:
            return int(self.数字值)

        def __float__(self) -> float:
            return float(self.数字值)

    def __init__(self, 接口说明: str = None):
        self._ARGS = None
        self._接口说明: str = 接口说明
        self._参数字典: dict[str, 入参基类._参数结构类] = {}
        self.匿名参数: list = []

        # 定义一个 jsonCfg 的变量做为默认参数，用于处理 jsonCfg 相关数据
        jsonCfg: 入参基类._参数结构类 = 入参基类._参数结构类(名称='jsonCfg',
                                                             类型=str,
                                                             提示='指定json格式的配置文件',
                                                             默认值='cfg.json')
        if jsonCfg.名称 not in self._参数字典.keys():
            self._参数字典[jsonCfg.名称] = jsonCfg

    # region 属性操作方法
    def get(self, 参数名: str) -> '入参基类._参数结构类':
        """
        读取指定名称的参数对象
        :param 参数名: 需要读取的参数的名称
        :return: 入参基类._参数结构类 对象
        """
        参数名 = str(参数名).strip()
        return self._参数字典[参数名] if 参数名 in self._参数字典.keys() else 入参基类._参数结构类()

    def set(self, 参数名: str, 参数值) -> bool:
        """
        将参数字典中对应于参数名的成员的值,设置为指定的值
        :param 参数名: 需要操作的参数的名称
        :param 参数值: 需要操作的参数的目标值
        :return:
        """
        参数名 = str(参数名).strip()
        if 参数名 in self._参数字典.keys():
            if self._参数字典[参数名].选项:
                if 参数值 in self._参数字典[参数名].选项:
                    self._参数字典[参数名].值 = 参数值
                else:
                    return False
            else:
                self._参数字典[参数名].值 = 参数值
                return True
        else:
            return False

    # endregion

    # 添加参数成员
    def _添加参数(self, 参数名称: str,
                  参数类型: type or list or None = None,
                  帮助提示: str = None,
                  默认值=None) -> bool:
        """
        将指定名称和类型的参数添加到参数字典中
        :param 参数名称: 指定的参数的名称
        :param 参数类型: 指定的参数的类型; 如果为None, 则代表该参数不接受参数值,只检测是否存在; 也可以指定一个list,表示只接受指定范围的参数值
        :param 帮助提示: 该参数的帮助/提示信息
        :param 默认值: 该参数的默认值
        :return: 是否添加成功, 添加成功:True, 添加失败: False
        """
        参数名称 = str(参数名称 if 参数名称 else '').strip()
        if 参数名称:
            # 如果存在有效的参数名称,则做如下处理
            参数值选项: list[str] = []
            参数有效类型: type or None
            无值型: bool = False

            # region 解析参数类型和参数值选项
            if 参数类型 is None:
                参数有效类型 = None
            elif 参数类型 in [int, float, str]:
                # 如果参数类型是数字或者字符串型
                参数有效类型 = 参数类型
            elif isinstance(参数类型, list):
                # 如果参数类型是一个list,那么这是一个指定选项的参数
                参数值选项 = [str(参数).strip() for 参数 in 参数类型 if ((参数 is not None) and str(参数).strip())]
                if not 参数值选项:
                    # 如果不存在有效的参数选项,则重置参数类型为None型
                    参数有效类型 = None
                else:
                    # 如果存在有效的参数选项,则判断这些选项是否全部是数字或者字符串
                    参数选项类型: list[type] = list(
                        set([type(参数) for 参数 in 参数类型 if ((参数 is not None) and str(参数).strip())]))
                    if not 参数选项类型:
                        # 未分析到有效的类型,则清空参数选项,且重置参数类型为None型
                        参数值选项 = []
                        参数有效类型 = None
                    elif 1 == len(参数选项类型) and 参数选项类型[0] in [int, float, str]:
                        # 如果参数选项的类型只有一咱,且属于 [int, float, str] 其中之一,则使用之
                        参数有效类型 = 参数选项类型[0]
                    else:
                        # 如果参数选项的类型不唯一,则统一处理成str形
                        参数有效类型 = str
            else:
                # 其它指定的未知的类型,一律做str处理
                参数有效类型 = str

            if 参数有效类型 is None:
                # 如果参数有效类型不存在,则这被识别为无值型参数
                参数有效类型 = bool
                无值型 = True

            # 格式化参数值选项
            if 参数值选项:
                参数值选项 = [参数有效类型(选项值) for 选项值 in 参数值选项]
            # endregion

            # region 解析默认值
            if type(默认值) in [list, tuple]:
                # 如果给定的默认值是一个list或者是tuple,那么取其第一个非空值做为默认值
                默认值 = [str(值).strip() for 值 in 默认值 if ((值 is not None) and str(值).strip())]
                默认值 = 默认值[0] if 默认值 else None
                if 默认值:
                    默认值 = 参数有效类型(默认值)
            if 参数值选项 and 默认值 is not None:
                # 如果默认值存在,且这是一个选项类的参数,则需要核实默认值是否在选项范围内, 如果不在,则取选项的第一个值做为默认值
                默认值 = 默认值 if 默认值 in 参数值选项 else 参数值选项[0]
            # endregion

            参数结构 = 入参基类._参数结构类(名称=参数名称,
                                            类型=参数有效类型,
                                            默认值=默认值,
                                            选项=参数值选项,
                                            无值型=无值型,
                                            提示=str(帮助提示 if 帮助提示 else '').strip())

            if 参数结构.有效:
                if 参数结构.名称 not in self._参数字典.keys():
                    self._参数字典[参数结构.名称] = 参数结构
                    return True
        return False

    def _移除jsonCfg参数(self):
        if 'jsonCfg' in self._参数字典.keys():
            self._参数字典.pop('jsonCfg')

    # 参数信息展示
    def 展示(self, 画板: 打印模板 = None):
        """
        展示参数字典中的参数名,参数类型,参数值等信息
        :param 画板: 用于打印输出的画板对象
        :return: None
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.展示)

        画板.准备表格(对齐控制串='l')
        画板.添加一行('有效性', '参数名', '参数类型', '参数值', '无值型/选项').修饰行(青字)
        无值型或者选项型: bool = False
        for 参数 in self._参数字典.values():
            if 参数.无值型:
                无值型或者选项型 = True
                画板.添加一行('[有效]' if 参数.有效 else '[无效]', 参数.名称, 参数.类型, 参数.值, '无值型')
            elif 参数.选项:
                无值型或者选项型 = True
                画板.添加一行('[有效]' if 参数.有效 else '[无效]', 参数.名称, 参数.类型, 参数.值,
                              '\n'.join([str(值) for 值 in 参数.选项]))
            else:
                画板.添加一行('[有效]' if 参数.有效 else '[无效]', 参数.名称, 参数.类型, 参数.值)
        if self.匿名参数:
            画板.添加一行('[有效]', '匿名参数', 'list', self.匿名参数)

        if not 无值型或者选项型:
            画板.修改指定行(0, ['有效性', '参数名', '参数类型', '参数值']).修饰行(青字)

        画板.展示表格()

    # 从指定 or 默认的json文档中读取配置参数
    def 解析Json(self,
                 jsonCfg: str = None,
                 encoding: str = None,
                 画板: 打印模板 = None):
        """
        从指定的json文档中(如果不指定,则从 jsonCfg 参数指定的json文档中)读取配置参数,将值赋值给同名的命令行参数
        :param jsonCfg: 可以指定jsonCfg文档
        :param encoding: 可以指定jsonCfg文档的编码格式,如果留空,则会尝试智能检测编码,如果检测失败,则尝试以 utf8 来解码
        :param 画板: 提供消息打印渠道
        :return: None
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.解析Json)

        if not jsonCfg:
            if 'jsonCfg' in self._参数字典.keys():
                jsonCfg = self._参数字典['jsonCfg'].值

        jsonCfg = str(jsonCfg if jsonCfg else '').strip()
        if not jsonCfg:
            画板.提示调试错误('jsonCfg 路径无效')
            return None
        if not _os.path.isfile(jsonCfg):
            画板.提示调试错误(f'jsonCfg 不是有效的 json 文件路径: {jsonCfg}')
            return None
        if not jsonCfg.endswith('.json'):
            画板.提示调试错误(f'jsonCfg 不是 json 格式的文件: {jsonCfg}')

        画板.调试消息(f'待解析的 jsonCfg 文件是: {jsonCfg}')
        jsonDic: dict
        try:
            with 打开(jsonCfg, 'r', encoding=encoding) as f:
                jsonDic = _json.load(f)
        except Exception as openExp:
            画板.提示调试错误(f'打开并读取 json 文档时遇到错误: {openExp}')
            jsonDic = {}
        if not jsonDic:
            画板.提示调试错误(f'未解析到有效的 json 内容: {jsonCfg}')
            return None

        jsonDic字典: dict = {}
        for 键, 值 in jsonDic.items():
            # 去除键前后的空格
            键 = str(键).strip()
            if 键:
                jsonDic字典[键] = 值

        已匹配的参数: dict[str, 入参基类._参数结构类] = {}
        未匹配的参数: dict[str, 入参基类._参数结构类] = {}
        for 参数 in self._参数字典.values():
            if 参数.名称 in jsonDic字典:
                参数.值 = jsonDic字典[参数.名称]
                if str(参数.值).strip() == str(jsonDic字典[参数.名称]).strip():
                    已匹配的参数[参数.名称] = 参数
        for 键, 值 in jsonDic字典.items():
            if 键 not in 已匹配的参数.keys():
                这个参数: 入参基类._参数结构类 = 入参基类._参数结构类(名称=键,
                                                                      类型=str,
                                                                      提示='这是 jsonCfg 中未匹配成功的参数',
                                                                      默认值=值)
                未匹配的参数[键] = 这个参数

        if 画板.正在调试 and (已匹配的参数 or 未匹配的参数):
            if 已匹配的参数:
                已匹配参数画板: 打印模板 = 画板.副本
                已匹配参数画板.准备表格(对齐控制串='l')

                已匹配参数画板.添加一行('参数名', '参数类型', '参数值', '提示').修饰行(青字)
                for 参数 in 已匹配的参数.values():
                    已匹配参数画板.添加一行(参数.名称, 参数.类型, 参数.值, 参数.提示)

                已匹配参数画板.展示表格()

            if 未匹配的参数:
                未匹配参数画板: 打印模板 = 画板.副本
                未匹配参数画板.准备表格(对齐控制串='l')

                未匹配参数画板.添加分隔行(提示文本='以下参数未匹配成功', 适应窗口=True, 修饰方法=红字)
                未匹配参数画板.添加一行('参数名', '参数类型', '文本').修饰行(青字)
                for 参数 in 未匹配的参数.values():
                    未匹配参数画板.添加一行(参数.名称, 参数.类型, 参数.值)

                未匹配参数画板.展示表格()

    # 定义一个函数，用来解析命令行调用传入的参数
    def 解析入参(self, 画板: 打印模板 = None):
        """
        解析命令行输入的参数值, 如果命令行传入的参数值为 None, 则对应的参数将保留默认值
        :param 画板: 用于打印消息的打印模板对象
        :return: None
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()
        画板.执行位置(self.__class__, self.解析入参)

        # region 添加要解析的参数信息
        if not self._参数字典:
            画板.调试消息('未指定任何关键字参数')
        if not isinstance(self._参数字典, dict):
            self._参数字典 = {}

        # region 判断是否可使用简写参数名
        简写列表: list[str] = []
        for 参数 in self._参数字典.values():
            # 默认参数 jsonCfg 不参与简写处理
            # 如果参数以h开关,为了避免与默认参数 help 的简写冲突,不参与简写处理
            if 'jsonCfg' != 参数.名称 and not 参数.名称.startswith('h'):
                # 尝试使用参数的第一个字符进行简写,如果所有参数的第一个字符不存在重复现象,则支持参数名简写
                简写: str = 参数.名称 if len(参数.名称) == 1 else 参数.名称[0]
                if 简写:
                    if 简写 not in 简写列表:
                        # 如果这个简写符号尚不存在,则这个简写被允许
                        if 简写 == 简写.upper():
                            参数.大写简写 = 简写
                        else:
                            参数.小写简写 = 简写
                        # 把这个简写添加到简写列表中
                        简写列表.append(简写)
        # endregion

        # 基于 argparse 模块解析脚本调用传入的参数
        self._接口说明 = str(self._接口说明 if self._接口说明 else '').strip()
        self._接口说明 = self._接口说明 if self._接口说明 else None
        if self._接口说明:
            解析器 = _argparse.ArgumentParser(description=self._接口说明)
        else:
            解析器 = _argparse.ArgumentParser()
        for 参数 in self._参数字典.values():
            if 参数.有效:
                简写符: str = ''
                if len(参数.名称) > 1 and (参数.大写简写 or 参数.小写简写):
                    # 如果参数是多字符参数,且存在大写或者小写简写
                    简写符 = 参数.大写简写 if 参数.大写简写 else 参数.小写简写

                if 参数.无值型:
                    if len(参数.名称) == 1:
                        解析器.add_argument(f'-{参数.名称}', action='store_true', help=参数.提示)
                    elif 简写符:
                        解析器.add_argument(f'-{简写符}', f'--{参数.名称}', action='store_true', help=参数.提示)
                    else:
                        解析器.add_argument(f'--{参数.名称}', action='store_true', help=参数.提示)
                else:
                    if len(参数.名称) == 1:
                        解析器.add_argument(f'-{参数.名称}',
                                            type=参数.类型,
                                            help=参数.提示,
                                            choices=参数.选项 if isinstance(参数.选项, list) and 参数.选项 else None)
                    elif 简写符:
                        解析器.add_argument(f'-{简写符}',
                                            f'--{参数.名称}',
                                            type=参数.类型,
                                            help=参数.提示,
                                            choices=参数.选项 if isinstance(参数.选项, list) and 参数.选项 else None)
                    else:
                        解析器.add_argument(f'--{参数.名称}',
                                            type=参数.类型,
                                            help=参数.提示,
                                            choices=参数.选项 if isinstance(参数.选项, list) and 参数.选项 else None)
        # 用于接收其它未明确的参数
        解析器.add_argument('匿名参数', nargs='*', help='请将所有匿名参数放在关键字参数前,或者后')
        # endregion

        self._ARGS = 解析器.parse_args()
        入参字典: dict = self._ARGS.__dict__ if self._ARGS else {}
        入参字典键列表 = 入参字典.keys()
        for 参数 in self._参数字典.values():
            if 参数.有效:
                if 参数.名称 in 入参字典键列表:
                    if 入参字典[参数.名称] is not None:
                        参数.值 = 入参字典[参数.名称]

        if '匿名参数' in 入参字典键列表:
            self.匿名参数 = 入参字典['匿名参数']

    def 转换为属性范式(self, setter: bool = True, 放入粘贴板: bool = True, 画板: 打印模板 = None) -> None:
        """
        将字典 self._入参字典 转换为以下的类属性范式
        @property
        def 参数名(self) -> 参数类型:
            if '参数名' in self.入参字典:
                return self.入参字典['参数名']
            else:
                return None
        @参数名.setter
        def 参数名(self, 值: 参数类型):
            if '参数名' in self.入参字典:
                if isinstance(值, 参数类型)
                    self.入参字典['参数名'] = 值

        :param setter: 是否输出 setter 属性
        :param 画板: 调试模板,用于输出打印内容
        :param 放入粘贴板: 整理后的内容是否放入粘贴板, 以方便粘贴使用
        :return: None
        """
        画板 = 画板 if isinstance(画板, 打印模板) else 打印模板()

        指定字典: dict = self._参数字典
        字典名: str = 'self._参数字典'

        if not isinstance(指定字典, dict) or not 字典名:
            画板.提示错误('指定字典不是 dict 类型, 或者指定的字典名无效')
            return None

        if not 字典名:
            画板.提示错误('指定的字典名无效')
            return None

        已经打印的属性名: list = []
        打印行: list[str] = ['# region 访问器']

        打印头: str = 画板.打印头

        文本缩进: str
        文本: str
        for 键, 值 in 指定字典.items():
            键 = str(键).strip()
            if not 键 or 键 in 已经打印的属性名:
                continue
            else:
                已经打印的属性名.append(键)

            值类型名: str = 值.__class__.__name__

            文本缩进 = ''
            文本 = f"@property"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            文本缩进 = ''
            if 值类型名 in ['int', 'float', 'str']:
                文本 = f"def {键}(self) -> {值类型名}:"
            else:
                文本 = f"def {键}(self) -> {值类型名} or None:"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            文本缩进 = ' ' * 4
            文本 = f"if '{键}' in {字典名}:"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            文本缩进 = ' ' * 8
            文本 = f"return {字典名}['{键}'].值"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            文本缩进 = ' ' * 4
            文本 = f"else:"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            文本缩进 = ' ' * 8
            if 值类型名 in ['int', 'float']:
                文本 = f"return 0"
            elif 值类型名 in ['str']:
                文本 = f"return ''"
            else:
                文本 = f"return None"
            画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
            打印行.append(f"{文本缩进}{文本}")

            if setter:
                文本缩进 = ''
                文本 = f"@{键}.setter"
                画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                打印行.append(f"{文本缩进}{文本}")

                文本缩进 = ''
                文本 = f"def {键}(self, 值:{值类型名}):"
                画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                打印行.append(f"{文本缩进}{文本}")

                文本缩进 = ' ' * 4
                文本 = f"if '{键}' in {字典名}:"
                画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                打印行.append(f"{文本缩进}{文本}")

                文本缩进 = ' ' * 8
                if 值类型名 in ['int', 'float']:
                    文本 = f"if type(值) in [int, float]:"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")

                    文本缩进 = ' ' * 12
                    文本 = f"{字典名}['{键}'].值 = {值类型名}(值)"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")
                elif 值类型名 == 'str':
                    文本 = f"{字典名}['{键}'].值 = {值类型名}(值)"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")
                else:
                    文本 = f"if isinstance(值, {值类型名}):"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")

                    文本缩进 = ' ' * 12
                    文本 = f"{字典名}['{键}'].值 = 值"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")

                    文本缩进 = ' ' * 8
                    文本 = f"else:"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")

                    文本缩进 = ' ' * 12
                    文本 = f"{字典名}['{键}'].值 = None"
                    画板.设置打印头(f"{打印头}{文本缩进}").消息(文本)
                    打印行.append(f"{文本缩进}{文本}")

        打印行.append('# endregion')
        画板.打印头 = 打印头
        if 打印行 and len(打印行) > 2 and 放入粘贴板:
            if 复制文本('\n'.join(打印行)):
                画板.消息(黄字(
                    f"打印内容已经放入粘贴板, 共 {绿字(len(打印行))} 行，创建属性 {绿字(len(已经打印的属性名))} 个"))


# region 装饰器
def 秒表(目标方法: callable):
    """
    这是一个装饰器,或者说是一个函数,可以使用 time.time 模型测试目标函数的运行时间
    :param 目标方法: 被测试的函数
    :return: 一个封装过的函数.
    """

    @_wraps(目标方法)
    def 参数接收器(*args, **kwargs):
        # 秒表消息通过画板打印输出
        画板: 打印模板 = 打印模板()
        # 清除打印头字符, 避免干扰
        画板.打印头 = ''

        # 检查方法参数中是否存在 打印模板 对象，如果存在，则复用之
        已经找到画板参数: bool = False
        for 参数 in args:
            if isinstance(参数, 打印模板):
                画板 = 参数
                已经找到画板参数 = True
        if not 已经找到画板参数:
            for 参数 in kwargs.values():
                if isinstance(参数, 打印模板):
                    画板 = 参数
                    已经找到画板参数 = True
        if 已经找到画板参数:
            # 为了不影响原画板内容,这里需要做一个副本出来,并缩进一格
            画板 = 画板.副本.缩进()
            # 恢复列左对齐
            画板.设置列对齐('l')
            # 恢复列宽设置
            画板.设置列宽([0])

        秒表启动时间 = _time.time()
        时钟计数开始 = _time.perf_counter()
        时钟计数开始_ns = _time.perf_counter_ns()
        程序计时开始 = _time.process_time()
        程序计时开始_ns = _time.process_time_ns()

        # 执行目标方法
        运行结果 = 目标方法(*args, **kwargs)

        时钟计数结束 = _time.perf_counter()
        时钟计数结束_ns = _time.perf_counter_ns()
        程序计时结束 = _time.process_time()
        程序计时结束_ns = _time.process_time_ns()
        秒表结束时间 = _time.time()

        时钟计时 = 时钟计数结束 - 时钟计数开始
        时钟计时_ns = 时钟计数结束_ns - 时钟计数开始_ns

        程序计时 = 程序计时结束 - 程序计时开始
        程序计时_ns = 程序计时结束_ns - 程序计时开始_ns

        秒表计时 = 秒表结束时间 - 秒表启动时间

        # 准备打印内容
        画板.准备表格('lll')
        画板.添加分隔行(提示文本='秒表信息', 修饰方法=红字, 重复=True, 适应窗口=True)
        画板.添加一行('项目', '值', '计时器', '备注').修饰行(青字)
        if 目标方法.__doc__:
            画板.添加一行('方法名称', 目标方法.__name__, '', 目标方法.__doc__)
        else:
            画板.添加一行('方法名称', 目标方法.__name__)
        画板.添加一行('秒表启动:', _datetime.fromtimestamp(秒表启动时间), 'time')

        if 秒表计时 > 1:
            画板.添加一行('计时/s:', 绿字(秒表计时), 'time.time')
        else:
            画板.添加一行('计时/ms:', 绿字(秒表计时 * 1000), 'time')

        if 时钟计时 > 1:
            画板.添加一行('计时/s:', 绿字(时钟计时), 'perf_counter')
        elif 时钟计时 > 0.001:
            画板.添加一行('计时/ms:', 绿字(时钟计时 * 1000), 'perf_counter')
        elif 时钟计时 > 0.000001:
            画板.添加一行('计时/us:', 绿字(时钟计时_ns * 0.001), 'perf_counter_ns')
        else:
            画板.添加一行('计时/ns:', 绿字(时钟计时_ns), 'perf_counter_ns')

        if 程序计时 > 1:
            画板.添加一行('计时/s:', 绿字(程序计时), 'process_time')
        elif 程序计时 > 0.001:
            画板.添加一行('计时/ms:', 绿字(程序计时 * 1000), 'process_time')
        elif 程序计时 > 0.000001:
            画板.添加一行('计时/us:', 绿字(程序计时_ns * 0.001), 'process_time_ns')
        else:
            画板.添加一行('计时/ns:', 绿字(程序计时_ns), 'process_time_ns')

        画板.添加一行('秒表结束:', _datetime.fromtimestamp(秒表结束时间), 'time')

        # 以默认列间距展示表格内容
        画板.展示表格()
        return 运行结果

    return 参数接收器

# endregion

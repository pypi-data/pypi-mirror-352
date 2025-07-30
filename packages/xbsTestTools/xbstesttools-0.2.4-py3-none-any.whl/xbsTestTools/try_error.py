# coding: utf-8
# Project：xbsTestTools
# File：try_error.py
# Author：张炼武
# Date ：2025/5/15 11:12
# IDE：PyCharm
from functools import wraps

def try_catch(func):
    """
    异常捕获装饰类
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"执行方法 {func.__name__} 时发生错误: {str(e)}")
            return None
    return wrapper
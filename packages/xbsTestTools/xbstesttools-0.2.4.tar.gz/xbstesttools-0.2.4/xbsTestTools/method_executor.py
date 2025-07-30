# coding: utf-8
# Project：xbsTestTools
# File：method_executor.py
# Author：张炼武
# Date ：2025/5/14 19:22
# IDE：PyCharm
import time
from typing import List, Callable, Any, Dict

class MethodExecutor:
    """
    方法执行器，用于按顺序执行多个方法
    """
    def __init__(self):
        self.methods: List[Dict[str, Any]] = []
        self.current_index = 0

    def add_method(self, method: Callable, *args, **kwargs) -> 'MethodExecutor':
        """
        添加要执行的方法
        :param method: 要执行的方法
        :param args: 方法的参数
        :param kwargs: 方法的关键字参数
        :return: 方法执行器实例
        """
        self.methods.append({
            'method': method,
            'args': args,
            'kwargs': kwargs
        })
        return self

    def execute(self, stop_on_error: bool = True) -> bool:
        """
        按顺序执行所有方法
        :param stop_on_error: 是否在遇到错误时停止执行
        :return: 是否所有方法都执行成功
        """
        success = True
        for i, method_info in enumerate(self.methods):
            method = method_info['method']
            args = method_info['args']
            kwargs = method_info['kwargs']

            try:
                print(f"开始执行第 {i + 1} 个方法: {method.__name__}")
                start_time = time.time()

                result = method(*args, **kwargs)

                end_time = time.time()
                execution_time = round(end_time - start_time, 2)

                print(f"方法 {method.__name__} 执行完成，耗时: {execution_time}秒")

                if not result:
                    print(f"方法 {method.__name__} 执行失败")
                    success = False
                    if stop_on_error:
                        # 执行过程失败停止
                        break

            except Exception as e:
                print(f"执行方法 {method.__name__} 时发生错误: {str(e)}")
                success = False
                if stop_on_error:
                    break

        return success

    def clear(self):
        """
        清空所有待执行的方法
        """
        self.methods.clear()
        self.current_index = 0


def for_run(v,fun):
    if type(v) != list and type(v) != int:
        print("传入的参数有误 只能是int或list")
        return False

    if v == int:
        for index in range(v):
            result = fun(index)
    else:
        for index in v:
            fun(index)

# 使用示例
if __name__ == "__main__":
    def method1(bb):
        print(f"执行方法1 等待4s {bb}")
        time.sleep(4)
        print("执行方法1 等待4s 完成")
        return True


    def method2():
        print("执行方法2 开始")
        return True


    def method3():
        print("执行方法3")
        print("执行方法3 等待2s")
        time.sleep(2)
        print("执行方法3 等待2s 完成")

        return True


    # 创建执行器实例
    executor = MethodExecutor()

    # 添加要执行的方法
    executor.add_method(method1,"111") \
        .add_method(method2) \
        .add_method(method3)

    # 执行所有方法
    success = executor.execute(stop_on_error=True)
    print(f"执行结果: {'成功' if success else '失败'}")

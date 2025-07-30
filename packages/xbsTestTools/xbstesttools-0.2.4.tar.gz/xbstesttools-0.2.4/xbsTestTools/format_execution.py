# coding: utf-8
# Project：xbsTestTools
# File：format_execution.py
# Author：张炼武
# Date ：2025/5/15 14:15
# IDE：PyCharm
import subprocess
from operate_controller import XbsUiOperate

class FormatExecution:
    def __init__(self, dev):
        self.dev = dev
        self.xuo = XbsUiOperate(dev)

    def return_var(self,widget_info):
        """返回操作参数"""
        var_s = {
            "text": None,
            "index": None,
            "resourceId": None,
            "class_": None,
            "image_path": None,
            "threshold": 0.98,
            "value": "",
            "timeout": 3
        }
        if widget_info.get("text"):
            var_s["text"] = widget_info["text"]
        if widget_info.get("index"):
            var_s["index"] = widget_info["index"]
        if widget_info.get("resourceId"):
            var_s["resourceId"] = widget_info["resourceId"]
        if widget_info.get("class_"):
            var_s["class_"] = widget_info["class_"]
        if widget_info.get("image_path"):
            var_s["image_path"] = widget_info["image_path"]
        if widget_info.get("threshold"):
            var_s["threshold"] = widget_info["threshold"]
        if widget_info.get("value"):
            var_s["value"] = widget_info["value"]
        if widget_info.get("timeout"):
            var_s["timeout"] = widget_info["timeout"]

        return var_s
    def operation_analysis(self, widget_info):
        rv = self.return_var(widget_info)
        if widget_info.get("operate") == "click":
            # 点击
            return self.xuo.click(text=rv['text'], index=rv['index'], resourceId=rv['resourceId'], class_=rv['class_'], image_path=rv['image_path'], threshold=rv['threshold'])

        elif widget_info.get("operate") == "seek_click":
            # 滑动找到目标再点击
            return self.xuo.click_roll(text=rv['text'], index=rv['index'], resourceId=rv['resourceId'], class_=rv['class_'], image_path=rv['image_path'], threshold=rv['threshold'])
        elif widget_info.get("operate") == "set_text":
            # 输入文本
            return self.xuo.input(text=rv['text'], index=rv['index'], resourceId=rv['resourceId'], class_=rv['class_'], image_path=rv['image_path'], content=rv['value'],threshold=rv['threshold'])
        elif widget_info.get("operate") == "positioning":
            # 定位
            return self.xuo.exists(text=rv['text'], index=rv['index'], resourceId=rv['resourceId'], class_=rv['class_'], image_path=rv['image_path'], threshold=rv['threshold'],timeout=rv['timeout'])

    def actuator(self, widget_list, retry_count=3):
        """控件执行操作"""
        start_type = False
        for retry in range(1, retry_count + 1):
            print(f"执行ID: {retry}")
            subprocess.run(f"adb -s {self.dev} shell input keyevent 266")
            for index, widget in enumerate(widget_list):
                # 循环遍历执行前置操作
                if widget.get("preconditions"):
                    if not isinstance(widget.get("preconditions"), list):
                        widget.get("preconditions")()
                    else:
                        # 前置操作时一个list
                        for pre in widget.get("preconditions"):
                            self.operation_analysis(pre)
                result = self.operation_analysis(widget)
                print(result)
                # 后置操作
                if widget.get("post_operation"):
                    # 后置操作时一个方法的话执行方法
                    if not isinstance(widget.get("post_operation"), list):
                        widget.get("post_operation")()
                    else:
                        # 后置操作时一个list
                        for post_oper in widget.get("post_operation"):
                            self.operation_analysis(post_oper)
                if len(widget_list) == index + 1 and result:
                    start_type = True
                    break
            if start_type:
                break
        return start_type
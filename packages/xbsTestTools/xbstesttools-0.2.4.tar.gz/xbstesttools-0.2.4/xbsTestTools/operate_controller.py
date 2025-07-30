# coding: utf-8
# Project：xbsUiOperate
# File：operate_controller.py
# Author：65
# Date ：2025/4/29 18:11
# IDE：PyCharm
import datetime
import os
from time import sleep
import uiautomator2 as u2
from xml.dom import minidom
import subprocess
import cv2

class XbsUiTest:
    """UI控件信息查询"""

    def __init__(self, dev):
        self.dev = dev

    def get_xml(self):
        u2xml = self.get_u2_xml()
        if not u2xml:
            return self.get_shell_xml()
        return u2xml

    def get_u2_xml(self):
        """
        通过U2获取XML
        """
        try:
            try:
                d = u2.connect(self.dev)
            except:
                print(f"adb -s {self.dev} shell /data/local/tmp/atx-agent server --stop")
                subprocess.run(f"adb -s {self.dev} shell /data/local/tmp/atx-agent server --stop")  # 停止服务

                print(f"adb -s {self.dev} shell /data/local/tmp/atx-agent server -d")
                subprocess.run(f"adb -s {self.dev} shell /data/local/tmp/atx-agent server -d")  # 启动服务
                sleep(2)

                print(f"adb -s {self.dev} uninstall com.github.uiautomator.test")
                os.system(f"adb -s {self.dev} uninstall com.github.uiautomator.test")

                print(f"adb -s {self.dev} uninstall com.github.uiautomator")
                os.system(f"adb -s {self.dev} uninstall com.github.uiautomator")
                sleep(2)
                try:
                    d = u2.connect(self.dev)
                except:
                    print(f"{self.dev} U2 初始化失败")
                    return False
            xml = d.dump_hierarchy()
            return xml
        except Exception as e:
            # print(f"{self.dev} U2查找报错:{e}")
            return

    def get_shell_xml(self):
        """
        通过adb获取XML
        """
        dev = str(self.dev).replace("?", "").replace("？", "")
        os.popen(f"adb -s {self.dev} shell uiautomator dump /sdcard/{dev}_ui.xml")
        sleep(3)
        os.popen(f"adb -s {self.dev} pull /sdcard/{dev}_ui.xml")
        sleep(3)
        # 解析XML文件
        dom = minidom.parse(f'{dev}_ui.xml')
        raw_xml = dom.toprettyxml(indent='   ')
        # 去除多余空行
        formatted_xml = '\n'.join(
            line for line in raw_xml.split('\n') if line.strip()
        )
        return formatted_xml

    @staticmethod
    def return_dict(content):
        xpath_info = {
            # "index": "",
            "text": "",
            "resourceId": "",
            "class": "",
            "bounds": "",
            "checkable": "",
            "checked": "",
            "clickable": "",
            "enabled": "",
            "scrollable": ""
        }
        dict_ = content.strip().split(" ")
        for index, dx in enumerate(dict_):
            dx = str(dx.replace('"', ""))
            try:
                if "resource-id" in dx:
                    xpath_info['resourceId'] = dx[dx.find('=') + 1:]
                elif "text" in dx:
                    xpath_info['text'] = dx[dx.find('=') + 1:]
                elif "class" in dx:
                    xpath_info['class'] = dx[dx.find('=') + 1:]
                elif "checkable" in dx:
                    xpath_info['checkable'] = dx[dx.find('=') + 1:]
                elif "checked" in dx:
                    xpath_info['checked'] = dx[dx.find('=') + 1:]
                elif "clickable" in dx:
                    xpath_info['clickable'] = dx[dx.find('=') + 1:]
                elif "enabled" in dx:
                    xpath_info['enabled'] = dx[dx.find('=') + 1:]
                elif "scrollable" in dx:
                    xpath_info['scrollable'] = dx[dx.find('=') + 1:]
                elif "bounds" in dx:
                    coordinate = dx[dx.find('=') + 1:].split('][')
                    coordinate = [
                        i.replace("[", "").replace("]", "").replace("/>", "").replace("<", "").replace(">", "") for i in
                        coordinate]
                    x_ = coordinate[0].split(",")
                    y_ = coordinate[1].split(",")
                    x = int((int(x_[0]) + int(y_[0])) / 2)
                    y = int((int(x_[1]) + int(y_[1])) / 2)
                    xpath_info['bounds'] = [x, y]
            except:
                print("异常")
                print(dx)

        return xpath_info

    def get_dict_by_xml(self, text=None, index=None, resourceId=None, class_=None, scrollable=None):
        xml_content = self.get_xml()
        if not xml_content:
            return False
        xpath_list = []
        for content in xml_content.split("\n"):
            if scrollable:
                # 如果是寻找滑动元素则
                content_dict = self.return_dict(content)
                if content_dict['scrollable'] == 'true':
                    xpath_list.append(content_dict)
                continue

            content_dict = self.return_dict(content)
            if text and text != content_dict['text']:
                continue

            if resourceId and resourceId != content_dict['resourceId']:
                continue

            if class_ and class_ != content_dict['class']:
                continue
            xpath_list.append(content_dict)
        if not xpath_list:
            return False

        if index:
            try:
                return xpath_list[index]
            except:
                ...
        if scrollable:
            return xpath_list
        return xpath_list[0]


class XbsUiOperate:
    """执行UI操作"""
    def __init__(self, dev):
        self.dev = dev
        self.xut = XbsUiTest(dev)

    def get_image_in_screenshot(self, small_image_path, threshold):
        """传入一张图片 获取在当前屏幕画面中的坐标位置"""
        ui_screenshot = self.screenshot(file="ui_screenshot", folder="current_screen")  # 获取当前画面信息
        # 读取截图和小图片
        screenshot = cv2.imread(ui_screenshot)  # cv2读取当前画面信息
        small_image = cv2.imread(small_image_path)  # cv2读取查找元素图片信息
        height, width, channels = small_image.shape  # 获取查找元素图片的高宽
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
        # 使用模板匹配
        result = cv2.matchTemplate(screenshot, small_image, cv2.TM_CCOEFF_NORMED)

        coordinate = []
        try:
            # 找到相似度最高的位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= threshold:
                # 这里 max_loc 就是相似度最高的匹配位置
                coordinate.append(max_loc[0])
                coordinate.append(max_loc[1])
            coordinate[0] += width // 2  # 获取x轴中心
            coordinate[1] += height // 2  # 获取y轴中心
        except:
            return []
        return coordinate

    def click(self, text=None, index=None, resourceId=None, class_=None, image_path=None,threshold=0.98):
        if image_path:
            # 点击图片方式
            coordinate = self.get_image_in_screenshot(image_path,threshold)
            if not coordinate:
                return False
            os.system(f"adb -s {self.dev} shell input tap {coordinate[0]} {coordinate[1]}")
        else:
            # 点击控件方式
            widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_)
            if not widget_info:
                return False
            pos = widget_info['bounds']
            if not pos:
                return False
            os.system(f"adb -s {self.dev} shell input tap {pos[0]} {pos[1]}")
        return True

    def click_long(self, text=None, index=None, resourceId=None, class_=None, image_path=None,threshold=0.98):
        if image_path:
            # 点击图片方式
            coordinate = self.get_image_in_screenshot(image_path,threshold)
            if not coordinate:
                return False
            os.system(f"adb -s {self.dev} shell input tap {coordinate[0]} {coordinate[1]}")
        else:
            widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_)
            if not widget_info:
                return False
            pos = widget_info['bounds']
            if not pos:
                return False
            os.system(f"adb -s {self.dev} shell input swipe {pos[0]} {pos[1]} {pos[0]} {pos[1]} 2000")  # 长按2s
        return True

    def click_roll(self, text=None, index=None, resourceId=None, class_=None, image_path=None,threshold=0.98):
        """
        滑动找到元素再点击
        """
        if image_path:
            # 点击图片方式
            widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_,
                                                   scrollable=True)
            for widget in widget_info:
                for index in range(10):
                    os.system(
                        f"adb -s {self.dev} shell input swipe {widget['bounds'][0]} {widget['bounds'][1]} {widget['bounds'][0]} {int(widget['bounds'][1]) + 400}")
                for index in range(10):
                    os.system(
                        f"adb -s {self.dev} shell input swipe {widget['bounds'][0]} {widget['bounds'][1]} {widget['bounds'][0]} {int(widget['bounds'][1]) - 200}")
                    coordinate = self.get_image_in_screenshot(image_path,threshold)
                    if not coordinate:
                        continue

                    os.system(f"adb -s {self.dev} shell input tap {coordinate[0]} {coordinate[1]}")
                    return True
        else:
            widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_,
                                                   scrollable=True)
            for widget in widget_info:
                for index in range(10):
                    os.system(
                        f"adb -s {self.dev} shell input swipe {widget['bounds'][0]} {widget['bounds'][1]} {widget['bounds'][0]} {int(widget['bounds'][1]) + 400}")
                for index in range(10):
                    os.system(
                        f"adb -s {self.dev} shell input swipe {widget['bounds'][0]} {widget['bounds'][1]} {widget['bounds'][0]} {int(widget['bounds'][1]) - 200}")
                    widget_click_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId,
                                                                 class_=class_)
                    if not widget_click_info:
                        continue
                    pos = widget_click_info['bounds']
                    if not pos:
                        return False
                    os.system(f"adb -s {self.dev} shell input tap {pos[0]} {pos[1]}")
                    return True
        return False

    def exists(self, text=None, index=None, resourceId=None, class_=None, image_path=None, timeout=3,threshold=0.98):
        if image_path:
            for i in range(timeout):
                coordinate = self.get_image_in_screenshot(image_path,threshold)
                if coordinate:
                    return True
                sleep(1)
        else:
            for i in range(timeout):
                widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_)
                if widget_info:
                    return True
                sleep(1)
        return False

    def input(self, text=None, index=None, resourceId=None, class_=None, image_path=None, content=None, threshold=0.98):
        if image_path:
            coordinate = self.get_image_in_screenshot(image_path, threshold)
            if not coordinate:
                return False
            subprocess.run(f"adb -s {self.dev} shell input tap {coordinate[0]} {coordinate[1]}")
        else:
            self.click(text=text, index=index, resourceId=resourceId, class_=class_)
        subprocess.run(f"adb -s {self.dev} shell input keyevent 111")  # 关闭键盘
        subprocess.run(f"adb -s {self.dev} shell input text '{content}'")
        input_test = self.get_text(text=content)
        if not input_test:
            return False
        return True

    def input_del(self, text=None, index=None, resourceId=None, class_=None):
        content = self.get_text(text=text, index=index, resourceId=resourceId, class_=class_)
        if not content:
            return True
        try:
            for n in range(len(content)):  # 根据文本的长度执行删除
                subprocess.run(f"adb -s {self.dev} shell input keyevent 67", shell=True, check=True)
            return True
        except:
            return False

    def roll(self, roll_type="down_to_top", ratio="middle", edge=False):
        size = self.get_size()  # 高  宽
        if not size:
            return False

        if ratio == "left":
            # 左边滑动
            x_start_t = int(int(size[1]) / 4)
            y_start_t = int(int(size[0]) / 3)
        elif ratio == "right":
            # 右边滑动
            x_start_t = int(int(size[1]) / 4) * 3
            y_start_t = int(int(size[0]) / 3)
        else:
            # 中间滑动
            x_start_t = int(int(size[1]) / 4) * 2
            y_start_t = int(int(size[0]) / 3)

        if roll_type == "down_to_top":
            # 从下往上滑动
            x_start = x_start_t
            x_end = x_start
            y_end = y_start_t
            y_start = y_start_t * 2
            os.system(f"adb -s {self.dev} shell input swipe {x_start} {y_start} {x_end} {y_end}")
        elif roll_type == "top_to_down":
            # 从上往下滑动
            x_start = x_start_t
            x_end = x_start
            y_end = y_start_t * 2
            y_start = y_start_t
            os.system(f"adb -s {self.dev} shell input swipe {x_start} {y_start} {x_end} {y_end}")
        elif roll_type == "left_to_right":
            # 从左往右滑动
            x_start = int(x_start_t - (x_start_t / 4))
            x_end = int(x_start_t + (x_start_t / 4))
            y_end = y_start_t + int(y_start_t / 4)
            y_start = y_start_t + int(y_start_t / 4)
            os.system(f"adb -s {self.dev} shell input swipe {x_start} {y_start} {x_end} {y_end}")
        elif roll_type == "right_to_left":
            # 从右往左滑动
            x_start = int(x_start_t + (x_start_t / 4))
            x_end = int(x_start_t - (x_start_t / 10))
            y_end = y_start_t + int(y_start_t / 4)
            y_start = y_start_t + int(y_start_t / 4)
            os.system(f"adb -s {self.dev} shell input swipe {x_start} {y_start} {x_end} {y_end}")

    def app_start(self, package_name):
        self.app_stop(package_name)  # 启动应用之前先关闭应用
        try:
            os.popen(f"adb -s {self.dev} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        except Exception as e:
            return False
        return True

    def app_stop(self, package_name):
        os.system(f"adb -s {self.dev} shell am force-stop {package_name}")
        return True

    def install_app(self, apk_file):
        if not os.path.exists(apk_file):
            return False
        os.system(f"adb -s {self.dev} install {apk_file}")
        return True

    def uninstall_app(self, package_name):
        os.system(f"adb -s {self.dev} uninstall {package_name}")
        return True

    def screen(self):
        """唤醒屏幕"""
        os.system(f"adb -s {self.dev} shell input keyevent 266")
        return True

    def screen_no(self):
        """休眠"""
        os.system(f"adb -s {self.dev} shell input keyevent 266")
        os.system(f"adb -s {self.dev} shell input keyevent 26")
        return True

    def reboot(self):
        """重启"""
        os.system(f"adb -s {self.dev} reboot")
        return True

    def reboot_p(self):
        """关机"""
        os.system(f"adb -s {self.dev} reboot -p")
        return True

    def get_text(self, text=None, index=None, resourceId=None, class_=None):
        widget_info = self.xut.get_dict_by_xml(text=text, index=index, resourceId=resourceId, class_=class_)
        if not widget_info:
            return False
        return widget_info['text'].strip()

    def screenshot(self, file=None, folder="debug"):
        """截图"""
        root_path = os.path.dirname(os.path.abspath(__file__)) + os.sep
        current_folder = f"{root_path}screenshot_folder{os.sep}{folder}{os.sep}"
        if not os.path.exists(current_folder):
            os.makedirs(current_folder)  # 创建文件夹

        if not file:
            file = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        try:
            os.system(f'adb -s {self.dev} exec-out screencap -p > "{current_folder}{file}.png"')
        except:
            return False
        return f"{current_folder}{file}.png"

    def screenrecord(self, file=None, time=30):
        """
        录制视频
        """
        try:
            if not file:
                file = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            os.system(f'adb -s {self.dev} shell screenrecord --time-limit {time} "/sdcard/{file}.mp4"')
            os.system(f'adb -s {self.dev} pull "/sdcard/{file}.mp4"')
        except:
            return False
        return f"{file}.mp4"
    def sound_recording(self):
        file = self.screenrecord()
        print(file)

    def get_size(self):
        try:
            result = os.popen("adb -s 03084S000080 shell wm size").read()
            size = result.replace("Physical size: ", "").strip().split("x")
            return size
        except:
            print(f"{self.dev} 获取屏幕分辨率失败")
            return False


if __name__ == '__main__':
    # dev = "03076S000002"
    # xuo = XbsUiOperate(dev)
    # print(xuo.screenshot())
    # xut = XbsUiTest(dev)
    # xml_content = xut.get_u2_xml()
    # print(xml_content)
    # print(xut.get_dict_by_xml(xml_content, text="系统"))
    ...

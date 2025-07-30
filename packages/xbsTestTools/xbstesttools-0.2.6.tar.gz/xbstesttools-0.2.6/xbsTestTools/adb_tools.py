# coding: utf-8
# Project：xbsTestTools
# File：adb_tools.py
# Author：张炼武
# Date ：2025/5/15 11:23
# IDE：PyCharm
import subprocess
from time import sleep

class AdbTools:
    def __init__(self, dev):
        self.dev = dev

    def wifi_assertion_internet(self):
        """
        断言WiFi是否可以上网
        :return: 网络连接状态，True表示正常，False表示异常
        :rtype: bool
        """
        try:
            cmd = f"adb -s {self.dev} shell ping -c 3 www.baidu.com"
            response = subprocess.run(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, check=False)

            if response.returncode != 0 or response.stderr:
                print(f"{self.dev} 网络互联网异常: {response.stderr}")
                return False

            ping_data = response.stdout
            # 正则表达式提取丢包率
            import re
            match = re.search(r'(\d+)% packet loss', ping_data)
            if not match:
                print(f"{self.dev} 无法解析ping结果: {ping_data}")
                return False

            packet_loss = float(match.group(1))

            if packet_loss <= 20:
                print(f"{self.dev} 网络正常，丢包率: {packet_loss}%")
                return True
            elif packet_loss >= 80:
                print(f"{self.dev} 设备Ping 网络丢包较高: {packet_loss}%")
                return True
            elif packet_loss == 100:
                print(f"{self.dev} 设备Ping 网络丢包100%，网络不可上网")
                return False
            else:
                print(f"{self.dev} 设备Ping 网络丢包率: {packet_loss}%")
                return packet_loss < 50  # 根据丢包率决定返回值
        except Exception as e:
            print(f"{self.dev} 网络检测过程出错: {str(e)}")
            return False

    
    def assertion_dev_type(self, timeout_=60):
        """
        获取设备在线状态，默认超时时间60s，每2s检查一次
        :param timeout_: 超时时间
        :type timeout_: 超时时间
        :return: boole
        :rtype: boole
        """
        for t in range((timeout_ // 2)):
            response = subprocess.run("adb devices", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if response.stderr:
                print(f"获取ADB设备失败 重新获取中")
                continue
            adb_data = str(response.stdout).replace("List of devices attached", "").strip()

            for adb_info in adb_data.split("\n"):
                adb_info = adb_info.split("\t")
                if adb_info[0] == self.dev and adb_info[1] == "device":
                    return True
            sleep(2)

    @staticmethod
    def select_dev_list(conditional="ALL"):
        """
        获取连接的全部ADB设备，可根据连接方式条件获取（ALL/USB/IP）
        :param conditional: 条件
        :type conditional: 条件
        :return: list
        :rtype: list
        """
        for t in range(3):
            response = subprocess.run("adb devices", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if response.stderr:
                print(f"获取ADB设备失败 重新获取中")
                continue
            adb_data = str(response.stdout).replace("List of devices attached", "").strip()
            dev_list = []
            for adb_info in adb_data.split("\n"):
                adb_info = adb_info.split("\t")
                if conditional == "USB" and "." not in adb_info[0]:
                    dev_list.append({"dev": adb_info[0], "type": adb_info[1]})
                elif conditional == "IP" and "." in adb_info[0]:
                    dev_list.append({"dev": adb_info[0], "type": adb_info[1]})
                elif conditional == "ALL":
                    dev_list.append({"dev": adb_info[0], "type": adb_info[1]})
            print(dev_list)
            return dev_list

    
    def dow_screen(self):
        response = subprocess.run(f"adb -s {self.dev} shell dumpsys power", stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        if not response.stderr:
            if "mWakefulness=Awake" not in response.stdout:
                subprocess.run(f"adb -s {self.dev} shell input keyevent KEYCODE_WAKEUP")
                print(f"{self.dev} 屏幕唤醒成功")
                return True
        print(f"{self.dev} 获取屏幕状态信息异常,屏幕唤醒失败")

    
    def assertion_dev_launcher(self, Launcher_name, timeout_=60):
        """
        获取设备 当前Launcher，默认超时时间60s，每2s检查一次
        :param Launcher_name:
        :type Launcher_name:
        :param timeout_: 超时时间
        :type timeout_: 超时时间
        :return: boole
        :rtype: boole
        """
        for t in range((timeout_ // 2)):
            response = subprocess.run(f"adb -s {self.dev} shell dumpsys window | grep mCurrentFocus",
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if response.stderr:
                print(f"{self.dev} 获取ADB设备Launcher失败 重新获取中")
                sleep(2)
                continue
            launcher_info = str(response.stdout).strip()
            print(f"{self.dev} {launcher_info}")
            if Launcher_name in launcher_info:
                return True
            sleep(2)

    
    def assertion_wifi_type(self, type_=""):
        """
        获取WIFI开关状态，0为关闭 1为打开  写入条件时返回对应的结果  如果为空的话 则返回当前WIFI状态
        :param type_: 条件  1or2
        :type type_:
        :return: boole or str
        :rtype:
        """
        for t in range(3):
            response = subprocess.run(f"adb -s {self.dev} shell settings get global wifi_on", stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True)
            if response.stderr:
                print(f"{self.dev} 获取ADB设备WIFI开关状态失败 重新获取中")
                sleep(2)
                continue
            wifi_onoff_info = str(response.stdout).strip()
            print(f"{self.dev} WIFI 开关状态 {wifi_onoff_info}")
            if type_:
                if type_ in wifi_onoff_info:
                    return True
            else:
                return wifi_onoff_info
            break

    
    def onoff_wifi(self, type_=False):
        """
        WIFI开关  打开 or 关闭  默认关闭
        :param type_:
        :type type_:
        :return: boole
        :rtype: boole
        """
        for t in range(3):
            if type_:
                response = subprocess.run(f"adb -s {self.dev} shell cmd wifi set-wifi-enabled enabled")
                if response.stderr:
                    print(f"{self.dev} 打开WIFI开关失败 重新打开中")
                    sleep(2)
                    continue
                if self.assertion_wifi_type("1"):
                    print(f"{self.dev} WIFI开关打开")
                    return True
                print(f"{self.dev} WIFI开关打开失败")
            else:
                response = subprocess.run(f"adb -s {self.dev} shell cmd wifi set-wifi-enabled disabled")
                if response.stderr:
                    print(f"{self.dev} 关闭WIFI开关失败 重新关闭中")
                    sleep(2)
                    continue
                if self.assertion_wifi_type("0"):
                    print(f"{self.dev} WIFI开关 关闭")
                    return True
                print(f"{self.dev} WIFI开关关闭失败")
            break

    
    def select_wifi_type(self):
        """
        获取WIFI 状态
        :return: str
        :rtype: str
        """
        for t in range(3):
            response = subprocess.run(f"adb -s {self.dev} shell cmd wifi status", stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True)
            if response.stderr:
                print(f"{self.dev} WIFI状态信息获取失败，重新获取中")
                sleep(2)
                continue

            wifi_info = str(response.stdout)
            # print(f"{self.dev} {wifi_info}")

            if "Wifi is disabled" in wifi_info and "Wifi scanning is only available when wifi is enabled" in wifi_info:
                print(f"{self.dev} WIFI 未开启")
                return "is not enabled not connected"

            if "Wifi is not connected" in wifi_info:
                print(f"{self.dev} WIFI 已开启 未连接")
                return "is enabled not connected"

            wifi_info_data = wifi_info.split("\n")
            if "connected to" in wifi_info:
                wifi_name = wifi_info_data[3]
                print(f"{self.dev} WIFI 已开启 已连接 {wifi_name}")
                return "is enabled connected"

            break
        return "select error"

    
    def continuous_click(self, x, y, cn):
        """
        快速连点
        :param x: x轴
        :type x: str
        :param y: y轴
        :type y: str
        :param cn: 点击次数
        :type cn: int
        :return: True\False
        :rtype: boole
        """
        interval = 0.1
        for i in range(cn):
            subprocess.run(["adb", "-s", self.dev, "shell", "input", "tap", str(x), str(y)])
            sleep(interval)

    
    def select_packages(self, type_="ALL", package_name=None):
        """
        获取设备的所有应用包名
        :param type_: 类型  可以设置 3 表示未三方应用   或者 系统应用  默认为全部应用
        :type type_: str
        :param package_name: 查询指定的package
        :type package_name:str
        :return: 包名列表 or True\False
        :rtype: lsit boole
        """
        if type_ == "ALL":
            cmd = f"adb -s {self.dev} shell pm list packages"
        elif type_ == "三方":
            cmd = f"adb -s {self.dev} shell pm list packages -3"
        elif type_ == "系统":
            cmd = f"adb -s {self.dev} shell pm list packages -s"
        elif type_ == "当前":
            cmd = f"adb -s {self.dev} shell dumpsys window | grep mCurrentFocus"
        else:
            print(f"获取包名参数错误 {type_} 只能为一下分类['三方','系统','当前','ALL']")
            return

        response = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if response.stderr:
            print(f"{self.dev} WIFI状态信息获取失败，重新获取中")
            return
        package_data = str(response.stdout).strip().replace("package:", "")

        # 查询是否存在指定应用包名
        if package_name:
            if package_name not in package_data:
                return
            return True

        # 查询当前运行的应用包名
        if type_ != "当前":
            package = package_data[package_data.find("u0") + 2:package_data.find("/")].strip()
            print(package)
            return package

        # 查询指定类型的包名list
        package_list = package_data.split("\n")
        print(f"[{len(package_list)}个] - {package_list}")
        return package_list

    
    def select_size(self):
        """
        获取设备的分辨率
        :return: int
        :rtype:
        """
        result = subprocess.run(['adb', '-s', self.dev, 'shell', 'wm', 'size'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{self.dev} 获取设备分辨率失败")
            return

        size = result.stdout.strip().split('size:')[-1].split('x')
        width = int(size[1])
        height = int(size[0])
        return width, height

    
    def swipe(self, start_x, start_y, end_x, end_y, duration_ms=300):
        """
        滑动  可按照像素点来  也可以按照百分比来
        :param start_x: 开始位置X
        :type start_x: int/str
        :param start_y: 开始位置Y
        :type start_y: int/str
        :param end_x: 结束位置x
        :type end_x:int/str
        :param end_y:结束位置Y
        :type end_y:int/str
        :param duration_ms: 执行完成速度
        :type duration_ms: int
        :return:
        :rtype: boole
        """
        width, height = self.select_size()
        if not width or not height:
            print(f"{self.dev}滑动失败")
            return

        if "%" in str(start_x) and "%" in str(start_y) and "%" in str(end_x) and "%" in str(end_y):
            # 计算百分比坐标
            print(f"{self.dev} 滑动百分比 {start_x} {start_y} {end_x} {end_y}")
            start_x = int(width * int(start_x.replace('%', '')) / 100)
            start_y = int(height * int(start_y.replace('%', '')) / 100)
            end_x = int(width * int(end_x.replace('%', '')) / 100)
            end_y = int(height * int(end_y.replace('%', '')) / 100)

        command = f"adb -s {self.dev} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
        subprocess.run(command)
        print(f"{self.dev} 滑动成功 {start_x} {start_y} {end_x} {end_y} {duration_ms}")
        return True

    
    def click(self, start_x, end_x, duration_ms=300):
        """
        点击  可按照像素点来  也可以按照百分比来
        :param start_x: 开始位置X
        :type start_x: int/str
        :param end_x: 结束位置x
        :type end_x:int/str
        :param duration_ms: 执行完成速度
        :type duration_ms: int
        :return:
        :rtype: boole
        """
        width, height = self.select_size()
        if not width or not height:
            print(f"{self.dev}滑动失败")
            return

        if "%" in str(start_x) and "%" in str(end_x):
            # 计算百分比坐标
            print(f"{self.dev} 点击百分比 {start_x} {end_x}")
            start_x = int(width * int(start_x.replace('%', '')) / 100)
            end_x = int(width * int(end_x.replace('%', '')) / 100)

        command = f"adb -s {self.dev} shell input tap {start_x} {end_x} {duration_ms}"
        subprocess.run(command)
        print(f"{self.dev} 点击成功 {start_x} {end_x} {duration_ms}")
        return True

    
    def reboot(self):
        """
        重启
        :return:
        :rtype:
        """
        subprocess.run(f"adb -s {self.dev} shell reboot")

    
    def shutdown(self):
        """
        关机
        :return:
        :rtype:
        """
        subprocess.run(f"adb -s {self.dev} shell reboot -p")


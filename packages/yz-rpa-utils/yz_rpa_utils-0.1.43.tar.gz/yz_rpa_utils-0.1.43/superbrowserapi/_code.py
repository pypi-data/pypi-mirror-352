import time
import os
import random
import uuid
import json
import requests
import subprocess
import psutil
import xml.etree.ElementTree as ET
import shutil
from time import sleep
import hashlib, traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retrying import retry


def kill_all_by_names(process_names):
    processes = psutil.process_iter(['pid', 'name'])
    for process_name in process_names:
        for process in processes:
            try:
                if process_name in process.info['name'] and process.is_running():
                    process.terminate()
                    process.wait(timeout=3)
            except Exception as ex:
                print(ex)


def encrypt_sha1(fpath: str) -> str:
    with open(fpath, 'rb') as f:
        return hashlib.new('sha1', f.read()).hexdigest()


def download_file(url, save_path):
    # 发送GET请求获取文件内容
    response = requests.get(url, stream=True)
    # 检查请求是否成功
    if response.status_code == 200:
        # 创建一个本地文件并写入下载的内容（如果文件已存在，将被覆盖）
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"文件已成功下载并保存到：{save_path}")
    else:
        print(f"下载失败，响应状态码为：{response.status_code}")


class SuperBrowserAPI:

    def __init__(self, company, username, password, _print=print):
        self.exe_path = self.get_super_browser_exe_path()
        self.print = _print
        # 获取当前运行路径
        self.driver_folder_path = os.path.join(os.getcwd(), "ziniao_driver")
        self.download_driver(self.driver_folder_path)

        assert company and username and password, "登录信息都是必选,请检查"
        self.user_info = {"company": company, "username": username, "password": password}
        self.socket_port = None
        # 初始化一个端口
        self.socket_port = self.get_port()
        self.web_driver = None

    def get_driver(self, open_ret_json):
        core_type = open_ret_json.get('core_type')
        if core_type == 'Chromium' or core_type == 0:
            major = open_ret_json.get('core_version').split('.')[0]
            chrome_driver_path = os.path.join(self.driver_folder_path, 'chromedriver%s.exe') % major
            self.print(f"chrome_driver_path: {chrome_driver_path}")
            port = open_ret_json.get('debuggingPort')
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", '127.0.0.1:' + str(port))
            return webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        else:
            return None

    def download_driver(self, driver_folder_path):
        config_url = "https://cdn-superbrowser-attachment.ziniao.com/webdriver/exe_32/config.json"
        response = requests.get(config_url)
        # 检查请求是否成功
        if response.status_code == 200:
            # 获取文本内容
            txt_content = response.text
            config = json.loads(txt_content)
        else:
            self.print(f"下载驱动失败，状态码：{response.status_code}")
            exit()
        if not os.path.exists(driver_folder_path):
            os.makedirs(driver_folder_path)

        # 获取文件夹中所有chromedriver文件
        driver_list = [filename for filename in os.listdir(driver_folder_path) if filename.startswith('chromedriver')]

        for item in config:
            filename = item['name']
            filename = filename + ".exe"
            local_file_path = os.path.join(driver_folder_path, filename)
            if filename in driver_list:
                # 判断sha1是否一致
                file_sha1 = encrypt_sha1(str(local_file_path))
                if file_sha1 == item['sha1']:
                    self.print(f"驱动{filename}已存在，sha1校验通过...")
                else:
                    self.print(f"驱动{filename}的sha1不一致，重新下载...")
                    download_file(item['url'], local_file_path)
            else:
                self.print(f"驱动{filename}不存在，开始下载...")
                download_file(item['url'], local_file_path)

    @staticmethod
    def get_super_browser_exe_path():
        """获取紫鸟浏览器启动文件路径"""

        config_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')

        if not os.path.exists(config_path):
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找匹配的产品名称
        matching_nodes = root.findall(".//ChromiumBrowserInfo[ProductName='{}']".format("superbrowser"))
        if len(matching_nodes) == 0:
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")
        # 提取ProcessName和ExePath
        node = matching_nodes[0]
        ProcessName, ExePath = node.find('ProcessName').text, node.find('ExePath').text
        assert ProcessName == "superbrowser", "紫鸟浏览器插件未正确安装，请检查"
        assert os.path.basename(ExePath) != "superbrowser.exe", "紫鸟浏览器插件未正确安装，请检查"
        return ExePath

    def get_port(self):
        procarr = []
        for conn in psutil.net_connections():
            if conn.raddr and conn.status == 'LISTEN':
                procarr.append(conn.laddr.port)
        # 判断当前端口是否占用,如果占用刷新端口
        if not self.socket_port or self.socket_port in procarr:
            tt = random.randint(15000, 20000)
            if tt not in procarr:
                return tt
            else:
                return self.get_port()
        else:
            return self.socket_port

    def start_exe_browser(self):
        """
        启动紫鸟客户端
        :return:
        """
        self.kill_all_super_browser()
        self.kill_all_store_process()
        cmd_text = None
        try:
            self.socket_port = self.get_port()
            cmd_text = [self.exe_path, '--run_type=web_driver', '--ipc_type=http', '--port=' + str(self.socket_port)]
            self.print(" ".join(cmd_text))
            subprocess.Popen(cmd_text)
            self.print("start ..")
            time.sleep(3)
        except Exception as e:
            self.print("start_ExeBrowser err...", e)
            try:
                self.socket_port = self.get_port()
                subprocess.Popen(cmd_text)
                time.sleep(3)
            except Exception as e:
                self.print('start browser process failed', e)
                raise Exception(f'start browser process failed {e}')

    @retry(
        stop_max_attempt_number=10,  # 最大重试次数
        wait_fixed=1000,  # 每次重试间隔 1 秒
    )
    def send_http(self, data):
        """
        通讯方式
        :param data:
        :return:
        """
        try:
            sleep(1)
            url = 'http://127.0.0.1:{}'.format(self.socket_port)
            # response = requests.post(url, json.dumps(data).encode('utf-8'), timeout=120)
            response = requests.post(url, json=data, timeout=60)
            r = json.loads(response.text)
            status_code = str(r.get("statusCode"))
            if status_code == "0":
                return r
            elif status_code == "-10003":
                raise Exception(json.dumps(r, ensure_ascii=False))
            else:
                raise Exception(json.dumps(r, ensure_ascii=False))
        except Exception as err:
            raise

    def open_store(self, store_info,
                   close_other_store=True,
                   isWebDriverReadOnlyMode=0,
                   isprivacy=0,
                   cookieTypeLoad=0,
                   cookieTypeSave=0,
                   isHeadless=False,
                   jsInfo="",
                   pluginIdList="16312716772451"):
        # 关闭其他店铺
        if close_other_store:
            self.kill_all_store_process()
        """
        打开店铺
        """
        requestId = str(uuid.uuid4())
        data = {
            "action": "startBrowser",
            "internalPluginList": "SBShopReport.zip,SBRPAEditor.zip,SBMessage.zip,SBCRM.zip,SBEcology.zip,SBHelp.zip,SBPassword.zip,SBRPA.zip,SBSems.zip,SBSetting.zip,SBShop.zip",
            "isWaitPluginUpdate": True,
            "isHeadless": isHeadless,
            "requestId": requestId,
            "isWebDriverReadOnlyMode": isWebDriverReadOnlyMode,
            "cookieTypeLoad": cookieTypeLoad,
            "cookieTypeSave": cookieTypeSave,
            "runMode": "2",
            "isLoadUserPlugin": False,
            "notPromptForDownload": 0,
            "pluginIdType": 1,
            "pluginIdList": pluginIdList,
            "privacyMode": isprivacy,
        }
        data.update(self.user_info)

        data["browserId"] = store_info

        if len(str(jsInfo)) > 2:
            data["injectJsInfo"] = json.dumps(jsInfo)
        res_result = self.send_http(data)

        self.web_driver = self.get_driver(res_result)
        # 隐式等待 5s
        self.web_driver.implicitly_wait(5)

        # 检测ip
        if self.open_ip_check("https://4.ipw.cn/", res_result.get('ipDetectionPage'), res_result):
            return res_result
        else:
            raise Exception("ip检测失败")

    def find_element_by_xpath(self, xpath):
        try:
            return self.web_driver.find_element(By.XPATH, xpath)
        except Exception as e:
            self.print(f"找不到元素 {xpath}")
            return None

    def open_ip_check(self, ip_check_url, ip_detection_page: str, res_result: dict):
        """
        打开ip检测页检测ip是否正常
        :param ip_detection_page:
        :param res_result:
        :param ip_check_url ip检测页地址
        :return 检测结果
        """
        # 先进入紫鸟官方插件,可自动优化IP
        self.web_driver.get(ip_detection_page)
        next_button = self.find_element_by_xpath('//span[contains(text(),"继续访问")]/..')
        if next_button:
            next_button.click()
        try:
            next_button = WebDriverWait(self.web_driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="打开账号"]/..'))
            )
        except Exception as ex:
            self.print("等待打开店铺按钮异常:" + traceback.format_exc())
        current_url = self.web_driver.current_url
        max_retry = 5
        check_flag = False
        while current_url != ip_check_url and max_retry > 0 and not check_flag:
            try:
                try:
                    self.web_driver.get(ip_check_url)
                except Exception as ex:
                    if "ERR_CONNECTION_CLOSED" in traceback.format_exc():
                        next_button = self.find_element_by_xpath('//span[contains(text(),"一键优化")]/..')
                        if next_button:
                            next_button.click()
                    else:
                        raise ex
                current_url = self.web_driver.current_url
                wait_time = 30
                web_ip = ""
                while str(web_ip).strip() != res_result.get("ip") and wait_time > 0:
                    web_ip = self.web_driver.find_element(By.XPATH, '//body').text
                    if web_ip and str(web_ip).strip() == res_result.get("ip"):
                        check_flag = True
                        break
                    time.sleep(1)
                    wait_time -= 1
            except Exception as e:
                self.print("ip检测异常:" + traceback.format_exc())
            finally:
                time.sleep(1)
                max_retry -= 1
        return check_flag

    def close_store(self, ziniao_shop_id):
        request_id = str(uuid.uuid4())
        data = {
            "action": "stopBrowser"
            , "requestId": request_id
            , "duplicate": 0
            , "browserOauth": ziniao_shop_id
        }
        data.update(self.user_info)

        r = self.send_http(data)
        if str(r.get("statusCode")) == "0":
            return r
        elif str(r.get("statusCode")) == "-10003":
            self.print(f"login Err {json.dumps(r, ensure_ascii=False)}")
        else:
            self.print(f"Fail {json.dumps(r, ensure_ascii=False)} ")

    def get_browser_list(self):
        requestId = str(uuid.uuid4())
        data = {
            "action": "getBrowserList",
            "requestId": requestId
        }
        data.update(self.user_info)

        r = self.send_http(data)
        return r.get("browserList")

    def get_store_name_list(self):
        browser_list = self.get_browser_list()
        store_name_list = []
        for item in browser_list:
            store_name_list.append(item.get("browserName"))
        return store_name_list

    def delete_all_cache(self):
        """
        删除所有店铺缓存
        非必要的，如果店铺特别多、硬盘空间不够了才要删除
        """
        self.kill_all_store_process()
        self.kill_all_super_browser()
        local_appdata = os.getenv('LOCALAPPDATA')
        cache_path = os.path.join(local_appdata, 'SuperBrowser')
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
            except Exception as ex:
                pass

    @staticmethod
    def kill_all_store_process():
        kill_all_by_names(["superbrowser", "chromedriver"])

    @staticmethod
    def kill_all_super_browser():
        kill_all_by_names(["SuperBrowser", "ziniao", "chromedriver"])

    def get_exit(self):
        """
        关闭客户端
        :return:
        """
        data = {"action": "exit", "requestId": str(uuid.uuid4())}
        # data.update(self.user_info)
        self.print('@@ get_exit...' + json.dumps(data))
        self.kill_all_store_process()
        self.kill_all_super_browser()


def go_home(url, timeout=20):
    pass


def main(args):
    pass

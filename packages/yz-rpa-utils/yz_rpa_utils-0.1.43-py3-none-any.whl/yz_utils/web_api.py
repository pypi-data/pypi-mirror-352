import traceback

import requests, json, time, base64
import threading
from retrying import retry


# 定义重试条件
def retry_in_expected_code(response, expected_code_list):
    """状态码在范围内"""
    return response.status_code in expected_code_list


class ApiClient:
    def __init__(self, base_url, user_name, password, _print=print):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        # 初始化当前令牌和刷新时间
        self.token = None
        self.token_refresh_time = 0
        self.print = _print

        if not self.base_url.startswith('http'):
            raise Exception('请检查base_url格式是否正确')
        if not self.user_name or not self.password:
            raise Exception('请配置正确的用户名和密码')
        # 创建的时候获取令牌
        self.get_access_token()
        # 创建定时器,每一分钟检测一次
        self.token_thread = threading.Thread(target=self.token_thread_func)
        self.token_thread_running = True
        self.token_thread.start()

    def token_thread_func(self):
        while self.token_thread_running:
            try:
                self.get_access_token()
            except Exception as ex:
                self.print(traceback.format_exc())
            finally:
                time.sleep(30)

    # 定义重试装饰器,最多30分钟还是失败就报错
    @retry(
        retry_on_result=lambda response: retry_in_expected_code(response, [401, 408, 429, 500, 502, 503, 504]),  # 重试条件
        stop_max_attempt_number=120,  # 最大重试次数
        wait_fixed=10000,  # 每次重试间隔 30 秒
    )
    def retry_request(self, func):
        try:
            response = func()
            self.print(f"请求结果:{response.text}")
            return response
        except Exception as ex:
            self.print(traceback.format_exc())
            raise Exception('请求异常:', ex)

    def get_access_token(self):
        if not self.token or int(time.time()) > self.token_refresh_time:
            token_result = self.handle_response(self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1/oauth2/token?grant_type=client_credentials",
                                                                                         headers={
                                                                                             'Authorization': 'Basic ' + base64.b64encode(f"{self.user_name}:{self.password}".encode('utf-8')).decode()
                                                                                         },
                                                                                         verify=False)))
            self.token = token_result.get('accessToken')
            self.print(f"更新令牌:{self.token}")
            # 减一分钟，防止网络延迟
            self.token_refresh_time = int(time.time()) + int(token_result.get('expiresIn')) - 60
        else:
            self.print(f"当前时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))}")
            self.print(f"令牌过期时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_refresh_time))}")

    @staticmethod
    def handle_response(response):
        return response.json().get('data')

    def get(self, request_path, request_body=None):
        if request_body is None:
            request_body = {}
        response = self.retry_request(lambda: requests.get(url=f"{self.base_url}/api/v1{request_path}",
                                                           headers={
                                                               'Authorization': 'Bearer ' + self.token
                                                           },
                                                           params=request_body,
                                                           verify=False))
        return self.handle_response(response)

    def post(self, request_path, request_body=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            data=request_body,
                                                            verify=False))
        return self.handle_response(response)

    def post_json(self, request_path, request_body=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            json=request_body,
                                                            verify=False))
        return self.handle_response(response)

    def post_file(self, request_path, request_body=None, files=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        if not files:
            raise Exception('请传入文件')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            data=request_body,
                                                            files=files,
                                                            verify=False))
        return self.handle_response(response)

    def close(self):
        self.token_thread_running = False
        self.token_thread.join()

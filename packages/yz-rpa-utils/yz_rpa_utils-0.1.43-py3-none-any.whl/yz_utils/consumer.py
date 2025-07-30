import json, traceback, pretty_errors
import gc
from .web_api import ApiClient
import threading, time, copy


class YuanmeiJob:
    def __init__(self,
                 jobId: str,
                 status: str,
                 companyCode: str,
                 platform: str,
                 queueName: str,
                 jobData: str,
                 resultData: str,
                 msg: str,
                 fileName: str,
                 errorFile: str,
                 shopId: int,
                 startDate: int,
                 endDate: int,
                 totalTime: int,
                 createDate: int,
                 successCount: int,
                 errorCount: int,
                 errorMsg: str,
                 taskName: str,
                 requestId: str,
                 createStaffId: str,
                 lastHeartbeatTime: int,
                 jobLockKey: str
                 ):
        self.jobId = jobId
        self.status = status
        self.companyCode = companyCode
        self.platform = platform
        self.queueName = queueName
        self.jobData = jobData
        self.resultData = resultData
        self.msg = msg
        self.fileName = fileName
        self.errorFile = errorFile
        self.shopId = shopId
        self.startDate = self.date_str_to_int(startDate)
        self.endDate = self.date_str_to_int(endDate)
        self.totalTime = totalTime
        self.createDate = self.date_str_to_int(createDate)
        self.successCount = successCount
        self.errorCount = errorCount
        self.errorMsg = errorMsg
        self.taskName = taskName
        self.requestId = requestId
        self.createStaffId = createStaffId
        self.lastHeartbeatTime = self.date_str_to_int(lastHeartbeatTime)
        self.jobLockKey = jobLockKey
        # 临时信息
        self.error_msg_list = []
        self.log_list = []

    @staticmethod
    def date_str_to_int(date_str):
        if type(date_str) == str:
            return int(time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))
        else:
            return date_str

    @staticmethod
    def date_int_to_str(obj: dict):
        for key in ["startDate", "endDate", "createDate", "lastHeartbeatTime"]:
            if obj.get(key):
                if len(str(obj[key])) == 10:
                    lt = time.localtime(obj[key])
                else:
                    lt = time.localtime(obj[key] / 1000)
                obj[key] = time.strftime('%Y-%m-%d %H:%M:%S', lt)

    def sum_total_time(self):
        self.totalTime = self.endDate - self.startDate

    def to_json(self):
        res_json = copy.deepcopy(self.__dict__)
        self.date_int_to_str(res_json)
        if self.error_msg_list is not None:
            self.errorMsg = json.dumps(self.error_msg_list, ensure_ascii=False)
        return res_json

    def get_job_vars(self):
        local_vars = {}
        if self.jobData:
            job_data = json.loads(self.jobData)
            for job_param in job_data:
                if job_param.get("yingdaoFlag"):
                    local_vars[job_param.get("name")] = job_param.get("value")
        return local_vars


class Consumer:
    def __init__(self, api_client: ApiClient, queue_name: str = None, _print=print):
        self.api_client = api_client
        self.queue_name = queue_name
        self.print = _print
        self.currentJob = None
        # 创建定时器,心跳
        self.consumer_running = True
        self.heart_beat_thread = threading.Thread(target=self.token_thread_func)
        self.heart_beat_thread.start()

    def run(self):
        while self.consumer_running:
            try:
                self.get_job()
                # 获取到任务才执行
                if self.currentJob:
                    app_code = self.get_app_code()
                    try:
                        self.start_job()
                        # 配置一些方法和参数
                        local_vars = self.currentJob.get_job_vars()
                        local_vars["log"] = self.log
                        local_vars["error_log"] = self.error_log
                        local_vars["api_client"] = self.api_client
                        local_vars["job"] = self.currentJob
                        # 处理代码,使用函数作用域,能保证代码完整运行
                        code_block = "def run_code():\n"
                        for line in str(app_code).splitlines():
                            code_block += f"\t{line}\n"
                        code_block += "run_code()"
                        exec(code_block, local_vars, local_vars)
                        del code_block, local_vars
                        if self.currentJob.errorCount == 0:
                            self.end_job("SUCCESS")
                        else:
                            self.error_job()
                    except Exception as ex:
                        self.error_log(traceback.format_exc())
                        self.error_job()
                    finally:
                        self.update_job()
                else:
                    self.print("没有任务,休息10秒")
            except Exception as e:
                self.print(traceback.format_exc())
            finally:
                time.sleep(10)
                # 执行完清空任务
                self.currentJob = None
                gc.collect()  # 强制垃圾回收，清理内存

    def update_result_data(self, local_vars):
        result_data = {}
        for key in local_vars:
            if type(local_vars.get(key)) in [str, int, float, dict, list]:
                result_data[key] = local_vars.get(key)
        # 更新任务结果
        self.currentJob.resultData = json.dumps(result_data, ensure_ascii=False)
        self.update_job()

    def log(self, msg):
        self.currentJob.log_list.append(msg)
        self.currentJob.msg = msg
        self.print(msg)
        self.update_job()

    def error_log(self, error_msg):
        self.currentJob.error_msg_list.append(error_msg)
        self.update_job()

    def start_job(self):
        self.print("开始任务")
        self.currentJob.status = "PROCESS"
        self.currentJob.startDate = int(time.time() * 1000)
        self.update_job()

    @staticmethod
    def convert_milliseconds_to_hms(milliseconds):
        # 首先将毫秒转换为秒
        seconds = milliseconds / 1000.0

        # 计算小时、分钟和秒
        hours = int(seconds // 3600)  # 整小时数
        minutes = int((seconds % 3600) // 60)  # 剩余的秒数换算成分钟
        secs = int(seconds % 60)  # 最终剩余的秒数（取整）

        # 格式化输出
        return f"{hours}小时 {minutes}分钟 {secs}秒"

    def end_job(self, status="SUCCESS"):
        self.print("结束任务")
        self.currentJob.status = status
        self.currentJob.endDate = int(time.time() * 1000)
        self.currentJob.sum_total_time()
        # 判断成功和失败
        if status == "ERROR":
            self.currentJob.msg = f"{self.currentJob.taskName}-任务执行失败, 耗时{self.convert_milliseconds_to_hms(self.currentJob.totalTime)}毫秒"
        else:
            self.currentJob.msg = f"{self.currentJob.taskName}-任务执行成功, 耗时{self.convert_milliseconds_to_hms(self.currentJob.totalTime)}毫秒"

    def error_job(self):
        self.print("任务异常")
        self.end_job("ERROR")

    # 心跳线程 60s 一次
    def token_thread_func(self):
        while self.consumer_running:
            try:
                self.heart_beat()
            except Exception as ex:
                self.print(traceback.format_exc())
            time.sleep(60)

    def heart_beat(self):
        if self.currentJob and self.currentJob.jobId:
            self.api_client.post("/YuanmeiJob/open/sendHeartbeat", {"jobId": self.currentJob.jobId})

    def get_job(self):
        req_url = "/YuanmeiJob/open/getOneWaitJob"
        if self.queue_name:
            req_url += f"?queueName={self.queue_name}"
        job_result = self.api_client.get(req_url)
        if job_result:
            self.print(f"获取任务成功:{json.dumps(job_result, ensure_ascii=False)}")
            del job_result["id"]
            del job_result["isDel"]
            self.currentJob = YuanmeiJob(**job_result)
            return self.currentJob
        else:
            return None

    def get_app_code(self):
        if self.currentJob and self.currentJob.queueName:
            return self.api_client.get("/YuanmeiYingdaoApp/open/getApp", request_body={"queueName": self.currentJob.queueName}).get("pythonCodeBlock")
        else:
            raise Exception("未知任务队列")

    def update_job(self):
        job_json = self.currentJob.to_json()
        self.print(f"任务Id:{self.currentJob.jobId},更新")
        self.api_client.post_json("/YuanmeiJob/open/updateJob", request_body=job_json)

    def close(self):
        self.consumer_running = False
        self.api_client.close()

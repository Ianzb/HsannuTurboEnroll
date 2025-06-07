import time
import traceback
from logging.config import dictConfig

import requests
import urllib3

from .program import *
from .setting import *
import logging

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
translator = FluentTranslator()
app.installTranslator(translator)
# 关闭SSL证书验证
import ssl

ssl._create_default_https_context = ssl._create_unverified_context()

# 日志设置
open(program.LOGGING_FILE_PATH, "w").close() if not zb.existPath(program.LOGGING_FILE_PATH) or zb.fileSize(program.LOGGING_FILE_PATH) >= 1024 * 128 else None

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
        "log_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": program.LOGGING_FILE_PATH,
            "encoding": "utf-8",
        },

    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "log_file"],
    },
}
)

logging.info(f"程序启动参数{program.STARTUP_ARGUMENT}!")


class School:
    def __init__(self):
        self.student_data = None
        self.sessionStorage = None
        self.query_type = None
        self.query_data = None
        self.task_data = None
        self.club_data = None

        setting.changeSignal.connect(self.updateSetting)

        urllib3.util.connection.DEFAULT_MAX_POOL_SIZE = setting.read("threadNumber") + 1
        self.session = requests.session()

    def updateSetting(self, msg):
        if msg == "threadNumber":
            urllib3.util.connection.DEFAULT_MAX_POOL_SIZE = setting.read("threadNumber") + 1

    def login(self, username, password):
        login_data = {
            "username": username, "password": password, "schoolCode": "2201023001",
        }
        response = self.session.post("https://service.do-ok.com/b/common/api/user/v1/loginForXk", data=login_data, headers=zb.REQUEST_HEADER)
        self.student_data = json.loads(response.text)
        self.sessionStorage = {
            "schoolCode": self.student_data["commonInfo"]["user"]["schoolCode"],
            "token": self.student_data["commonInfo"]["jwt"],
            "user": self.student_data["commonInfo"]["user"],
            "casUser": self.student_data["commonInfo"]["user"]["loginName"],
            "studentMessage": self.student_data["studentInfo"],
            "class": [i for i in self.student_data["studentInfo"]["treeviewStudentDtoList"] if i["tvType"] == "g-c"][0],
            "userId": self.student_data["studentInfo"]["treeviewStudentDtoList"][0]["userId"],
        }
        self.header = {
            "Authorization": self.sessionStorage.get("token"),
        }
        return self.student_data

    def getQueryType(self, courseType: int):
        """
        0：校本选课，1：模块选修课
        :param courseType:
        """
        params = {
            "schoolCode": "2201023001",
            "subcourseType": courseType,
            "_": str(int(time.time() * 1000)),
        }

        response = self.session.get("https://service.do-ok.com/b/jwgl/api/infosubcategory/v1/query", params=params, headers=self.header)
        self.query_type = json.loads(response.text)

        return self.query_type

    def getOldCourse(self, course_type: int = 0):
        params = {
            "subcourseType": course_type,
            "userId": self.sessionStorage["userId"],
            "_": str(int(time.time() * 1000)),
        }
        response = self.session.get("https://service.do-ok.com/b/jwgl/api/subcoursestudent/v1/getSubcourseByStudentId", params=params, headers=self.header)
        return json.loads(response.text)

    def getQueryData(self):
        params = {
            "start": "0",
            "limit": "99999",
            "searchValue": "",
            "schoolCode": "2201023001",
            "status": "1",
            "nowDate": "2018-10-10 12:12:12",
            "taskType": "1",
            "classId": self.sessionStorage["class"]["treeviewId"],
            "_": str(int(time.time() * 1000)),
        }
        response = self.session.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentQuery", params=params, headers=self.header)
        self.query_data = json.loads(response.text)

        return self.query_data

    def getTaskData(self, task_id: str):
        params = {
            "id": task_id,
            "userId": self.sessionStorage["userId"],
            "_": str(int(time.time() * 1000)),
        }
        response = self.session.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentGetTask", params=params, headers=self.header)
        self.task_data = json.loads(response.text)

        return self.task_data

    def getClubData(self, club_id: str):
        params = {
            "id": club_id,
        }
        response = self.session.get("https://service.do-ok.com/b/jwgl/api/infosubcourse/v1/get", params=params, headers=self.header)
        self.club_data = json.loads(response.text)

        return self.club_data

    def joinClub(self, club_id: str, stmesterId, taskId):
        try:
            data = {
                "joinId": club_id,
                "number": 1,
                "userId": self.sessionStorage["user"]["userId"],
                "userName": self.sessionStorage["user"]["realName"],
                "schoolCode": "2201023001",
                "getresourceApproach": 0,
                "gradeId": self.sessionStorage["class"]["tvParentid"],
                "gradeName": self.sessionStorage["class"]["tvParentname"],
                "classId": self.sessionStorage["class"]["treeviewId"],
                "className": self.sessionStorage["class"]["itemName"],
                "taskId": taskId,
                "loginName": self.student_data["studentInfo"]["infoStudent"]["studentCode"],
                "semesterId": stmesterId,
                "sex": self.student_data["studentInfo"]["infoStudent"]["sex"],
            }
            response = self.session.post("https://service.do-ok.com/b/jwgl/api/inforesource/v1/studentSelectResource", data=data, headers=self.header)
            return json.loads(response.text)
        except:
            logging.error(f"抢课错误，报错信息{traceback.format_exc()}！")

    def getResult(self, course_id):
        params = {
            "subcourseId": course_id,
            "userId": self.sessionStorage["userId"],
        }
        response = self.session.get("https://service.do-ok.com/b/jwgl/api/inforesource/v1/getResult", params=params, headers=self.header)
        status = json.loads(response.text)["data"]["status"]
        logging.info(f"结果查询：{response.text}")
        if status == 0:
            return "选课成功"
        elif status == 1:
            return "未排队"
        elif status == 2:
            return "排队中"
        else:
            return "未知错误"


school = School()

logging.info("程序动态数据api初始化成功！")

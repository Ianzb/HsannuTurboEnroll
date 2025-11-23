from logging.config import dictConfig

from .program import *
from .setting import *

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

        setting.changeSignal.connect(self.updateSetting)

        urllib3.util.connection.DEFAULT_MAX_POOL_SIZE = setting.read("threadNumber") + 1
        self.session = requests.session()

    def updateSetting(self, msg):
        if msg == "threadNumber":
            urllib3.util.connection.DEFAULT_MAX_POOL_SIZE = setting.read("threadNumber") + 1

    def get(self, url: str, times: int = 5, **kwargs):
        """
        可重试的get请求
        :param url: 链接
        :param header: 请求头
        :param timeout: 超时
        :param times: 重试次数
        :return:
        """
        logging.info(f"正在Get请求{url}的信息！")
        for i in range(times):
            try:
                response = self.session.get(url, **kwargs, stream=True, verify=False)
                logging.info(f"Get请求{url}成功！")
                return response
            except:
                logging.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{traceback.format_exc()}，正在重试中！")
                continue
        logging.error(f"Get请求{url}失败！")

    def post(self, url: str, times: int = 5, **kwargs):
        """
        可重试的post请求
        :param url: 链接
        :param times: 重试次数
        :return:
        """
        logging.info(f"正在Post请求{url}的信息！")
        for i in range(times):
            try:
                response = self.session.post(url, **kwargs, verify=False)
                logging.info(f"Post请求{url}成功！")
                return response
            except:
                logging.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{traceback.format_exc()}，正在重试中！")
                continue
        logging.error(f"Post请求{url}失败！")

    @property
    def header(self):
        """
        通过学生信息获取请求头
        :param student_data: 学生信息
        :return: 请求头
        """
        return {"Authorization": self.student_data.get("commonInfo").get("jwt")}

    @property
    def getClass(self):
        """
        通过学生信息获取班级
        :param student_data: 学术信息
        :return: 班级信息
        """
        return [i for i in self.student_data.get("studentInfo", {}).get("treeviewStudentDtoList", []) if i.get("tvType") == "g-c"][0]

    @property
    def getUserInfo(self):
        return self.student_data.get("commonInfo", {}).get("user")

    def login(self, username, password):
        """
        登录
        :param username: 用户名
        :param password: 密码
        :return: 学生信息student_data
        """
        login_data = {
            "username": username,
            "password": password,
            "schoolCode": "2201023001",
        }
        student_data = json.loads(self.post("https://service.do-ok.com/b/common/api/user/v1/loginForXk", data=login_data, headers=zb.REQUEST_HEADER, timeout=(2.5, 5)).text)
        self.student_data = student_data
        return student_data

    def getCourseList(self, course_type: int):
        """
        获取选课列表
        :param course_type: 选课类别 0：校本选课，1：模块选修课
        :return: 选课列表query_type
        """
        params = {
            "schoolCode": "2201023001",
            "subcourseType": course_type,
            "_": str(int(time.time() * 1000)),
        }

        course_list = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/infosubcategory/v1/query", params=params, headers=self.header, timeout=(2.5, 5)).text)
        return course_list

    def getHistoryClass(self, course_type: int):
        """
        获取历史选课列表
        :param course_type: 选课类别 0：校本选课，1：模块选修课
        :return: 选课列表
        """
        params = {
            "subcourseType": course_type,
            "userId": self.getUserInfo.get("userId"),
            "_": str(int(time.time() * 1000)),
        }
        history_class = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/subcoursestudent/v1/getSubcourseByStudentId", params=params, headers=self.header, timeout=(2.5, 5)).text)
        return history_class

    def getCourseData(self, course_type: int):
        """
        获取选课任务信息
        :param course_type: 选课类别 0：校本选课，1：模块选修课
        :return: 课程列表
        """
        params = {
            "start": "0",
            "limit": "99999",
            "searchValue": "",
            "schoolCode": "2201023001",
            "status": "1",
            "nowDate": "2018-10-10 12:12:12",
            "taskType": str(course_type),
            "classId": self.getClass.get("treeviewId"),
            "_": str(int(time.time() * 1000)),
        }
        course_data = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentQuery", params=params, headers=self.header, timeout=(2.5, 5)).text)
        return course_data

    def getCourseClass(self, course_id: str):
        """
        获取任务课程列表
        :param course_id: 任务id
        :return: 课程列表
        """
        params = {
            "id": course_id,
            "userId": self.getUserInfo.get("userId"),
            "_": str(int(time.time() * 1000)),
        }
        course_class = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentGetTask", params=params, headers=self.header, timeout=(2.5, 5)).text)

        return course_class

    def getClassData(self, class_id: str):
        """
        获取课程信息
        :param class_id: 课程id
        :return: 课程信息
        """
        params = {
            "id": class_id,
        }
        class_data = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/infosubcourse/v1/get", params=params, headers=self.header, timeout=(2.5, 5)).text)
        return class_data

    def joinClass(self, class_id: str, semester_id, task_id, user_info, get_class, student_data, header):
        """
        加入课程
        :param class_id: 课程id
        :param semester_id: 学期id
        :param task_id: 任务id
        :param user_info:
        :param get_class:
        :param student_data:
        :param header:
        :return:
        """
        try:
            data = {
                "joinId": class_id,
                "number": 1,
                "userId": user_info.get("userId"),
                "userName": user_info.get("realName"),
                "schoolCode": "2201023001",
                "getresourceApproach": 0,
                "gradeId": get_class.get("tvParentid"),
                "gradeName": get_class.get("tvParentname"),
                "classId": get_class.get("treeviewId"),
                "className": get_class.get("itemName"),
                "taskId": task_id,
                "loginName": student_data.get("studentInfo", {}).get("infoStudent", {}).get("studentCode"),
                "semesterId": semester_id,
                "sex": student_data.get("studentInfo", {}).get("infoStudent", {}).get("sex"),
            }
            return json.loads(self.post("https://service.do-ok.com/b/jwgl/api/inforesource/v1/studentSelectResource", data=data, headers=header, timeout=(2.5, 5)).text)
        except:
            logging.error(f"抢课错误，报错信息{traceback.format_exc()}！")

    def getResult(self, class_id, user_id, header):
        """
        获取结果
        :param class_id: 课程id
        :return: 结果字符串
        :param user_id:
        :param header:
        """
        params = {
            "subcourseId": class_id,
            "userId": user_id,
        }
        status = json.loads(self.get("https://service.do-ok.com/b/jwgl/api/inforesource/v1/getResult", params=params, headers=header, timeout=(2.5, 5)).text).get("data", {}).get("status")
        logging.info(f"结果查询：{status}")
        if status == 0:
            return "选课成功"
        elif status == 1:
            return "未排队"
        elif status == 2:
            return "排队中"
        else:
            return f"未知状态{status}"


school = School()

logging.info("程序动态数据api初始化成功！")

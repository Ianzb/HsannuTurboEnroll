import json
import logging
import time
import traceback
from functools import wraps

import requests
import zbToolLib as zb


class School:
    def __init__(self):
        self.student_data = None
        self.sessionStorage = None
        self.header = None
        self.query_type = None
        self.query_data = None
        self.task_data = None
        self.club_data = None

    def login(self, username, password):
        login_data = {
            "username": username, "password": password, "schoolCode": "2201023001",
        }
        response = requests.post("https://service.do-ok.com/b/common/api/user/v1/loginForXk", data=login_data, headers=zb.REQUEST_HEADER)
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

        response = requests.get("https://service.do-ok.com/b/jwgl/api/infosubcategory/v1/query", params=params, headers=self.header)
        self.query_type = json.loads(response.text)

        return self.query_type

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
        response = requests.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentQuery", params=params, headers=self.header)
        self.query_data = json.loads(response.text)

        return self.query_data

    def getTaskData(self, task_id: str):
        params = {
            "id": task_id,
            "userId": self.sessionStorage["userId"],
            "_": str(int(time.time() * 1000)),
        }
        response = requests.get("https://service.do-ok.com/b/jwgl/api/infotask/v1/studentGetTask", params=params, headers=self.header)
        self.task_data = json.loads(response.text)

        return self.task_data

    def getClubData(self, club_id: str):
        params = {
            "id": club_id,
        }
        response = requests.get("https://service.do-ok.com/b/jwgl/api/infosubcourse/v1/get", params=params, headers=self.header)
        self.club_data = json.loads(response.text)

        return self.club_data

    def joinClub(self, club_id: str,stmesterId,taskId):
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
            response = requests.post("https://service.do-ok.com/b/jwgl/api/inforesource/v1/studentSelectResource", data=data, headers=self.header)
            return json.loads(response.text)
        except:
            traceback.print_exc()

    def getResult(self, course_id):
        params = {
            "subcourseId": course_id,
            "userId": self.sessionStorage["userId"],
        }
        response = requests.get("https://service.do-ok.com/b/jwgl/api/inforesource/v1/getResult", params=params, headers=self.header)
        status = json.loads(response.text)["data"]["status"]
        logging.info(f"当前报名状态为：{response.text}")
        if status == 0:
            return "success"
        elif status == 1:
            return "loading"
        elif status == 404:
            return "error"
        else:
            return "error"


school = School()

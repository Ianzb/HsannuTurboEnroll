from ..program import *


class CourseInfoCard(zbw.SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, data: dict, parent=None, task_id=None, can_enroll: bool = True):
        super().__init__(parent=parent)
        self.data = data
        self.task_id = task_id

        self.setTitle(self.data["sName"])
        self.setText(f"任课教师：{self.data["teacherName"]}", 0)
        if self.data.get("numberLimit"):
            self.setText(f"已报名{self.data["numberLimit"] - self.data["number"]}人，剩余{self.data["number"]}人，人数限制{self.data["numberLimit"]}人", 1)
            self.setText(f"{self.data["number"]}/{self.data["numberLimit"]}", 3)

        self.image.deleteLater()
        self.mainButton.deleteLater()

        self.detailButton = PushButton(self)
        self.detailButton.setText("详细信息")
        self.detailButton.clicked.connect(self.showDetail)

        self.mainButton = PrimaryPushButton(self)
        self.mainButton.setText("报名")
        self.mainButton.clicked.connect(self.joinCourse)
        self.mainButton.setVisible(can_enroll)

        self.hBoxLayout.insertSpacing(-3, -16)
        self.hBoxLayout.addWidget(self.detailButton, 0)
        self.hBoxLayout.addWidget(self.mainButton, 0)
        self.hBoxLayout.addSpacing(8)

    def joinCourse(self):
        infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "已提交选课任务！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        infoBar.show()
        self.window().taskPage.addTask(self.data, self.task_id)

    def showDetail(self):
        school.getClubData(self.data["id"])
        data = school.club_data["data"]
        content = (f"课程名称：{data["sName"]}\n"
                   f"课程类型：{data["cName"]}，{data["category"]}\n"
                   f"学期：{data["semesterName"]}\n"
                   f"上课教师：{data["className"]}\n"
                   f"上课地点：{data["adress"]}\n"
                   f"课程人数：已报名{data["numberLimit"] - data["number"]}人，剩余{data["number"]}人，人数限制{data["numberLimit"]}人\n"
                   f"课程简介：{data["introduction"]}\n"
                   f"教师简介：{data["teacherIntroduction"]}\n"
                   f"能力水平：{data["abilityLevel"]}\n"
                   f"特殊要求：{data["specialAsk"]}\n"
                   f"评价方式：{data["evaluateType"]}\n")
        messageBox = CoureseMessageBox(data["sName"], content, self.window())

        messageBox.show()


class CoureseMessageBox(MessageBox):
    def __init__(self, title, content, parent=None):
        super().__init__(title, content, parent)
        self.widget.setMaximumSize(600, 400)
        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")

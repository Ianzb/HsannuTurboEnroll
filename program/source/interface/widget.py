import webbrowser

from ..program import *


class ErrorMessageBox(zbw.ScrollMessageBox):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        logging.error(content)

        self.contentLabel.setSelectable()
        self.cancelButton.setText("关闭")
        self.yesButton.hide()
        self.yesButton.deleteLater()

        self.reportButton = PrimaryPushButton("反馈", self, FIF.FEEDBACK)
        self.reportButton.clicked.connect(lambda: webbrowser.open(zb.joinUrl(program.GITHUB_URL, "issues/new")))

        self.restartButton = PrimaryPushButton("重启", self, FIF.SYNC)
        self.restartButton.clicked.connect(program.restart)
        self.buttonLayout.insertWidget(0, self.reportButton, 2)
        self.buttonLayout.insertWidget(1, self.restartButton, 2)


class ClassInfoCard(zbw.SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, data: dict, parent=None, task_id=None, begin_time: int = None):
        super().__init__(parent, True)
        self.data = data
        self.task_id = task_id
        self.begin_time = begin_time

        self.setTitle(self.data.get("sName"))
        self.setText(f"任课教师：{self.data.get("teacherName")}", 0)
        if self.data.get("numberLimit"):
            self.setText(f"已报名{self.data.get("numberLimit") - self.data.get("number")}人，剩余{self.data.get("number")}人，人数限制{self.data.get("numberLimit")}人", 1)
            self.setText(f"{self.data.get("number")}/{self.data.get("numberLimit")}", 3)

        self.image.deleteLater()
        self.mainButton.deleteLater()

        self.detailButton = PushButton(self)
        self.detailButton.setText("详细信息")
        self.detailButton.clicked.connect(self.showDetail)

        self.mainButton = PrimaryPushButton(self)
        self.mainButton.setText("报名")
        self.mainButton.clicked.connect(self.joinClass)
        self.mainButton.setVisible(bool(self.task_id))

        self.hBoxLayout.insertSpacing(-3, -16)
        self.hBoxLayout.addWidget(self.detailButton, 0)
        self.hBoxLayout.addWidget(self.mainButton, 0)
        self.hBoxLayout.addSpacing(8)

    def joinClass(self):
        infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "已提交选课任务！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        infoBar.show()
        self.window().taskPage.addTask(self.data, self.task_id, self.begin_time)

    def showDetail(self):
        class_data = school.getClassData(self.data.get("id"))
        data = class_data.get("data", {})
        content = (f"课程名称：{zb.getInfo(data, "sName", "无")}<br>"
                   f"课程类型：{zb.getInfo(data, "cName", "无")}，{zb.getInfo(data, "category", "无")}<br>"
                   f"学期：{zb.getInfo(data, "semesterName", "无")}<br>"
                   f"上课教师：{zb.getInfo(data, "teacherName", "无")}<br>"
                   f"上课地点：{zb.getInfo(data, "adress", "无")}<br>"
                   f"课程人数：已报名{data.get("numberLimit") - data.get("number")}人，剩余{data.get("number")}人，人数限制{data.get("numberLimit")}人<br>"
                   f"课程简介：{zb.getInfo(data, "introduction", "无")}<br>"
                   f"教师简介：{zb.getInfo(data, "teacherIntroduction", "无")}<br>"
                   f"能力水平：{zb.getInfo(data, "abilityLevel", "无")}<br>"
                   f"特殊要求：{zb.getInfo(data, "specialAsk", "无")}<br>"
                   f"评价方式：{zb.getInfo(data, "evaluateType", "无")}<br>")
        messageBox = zbw.ScrollMessageBox(data.get("sName"), content, self.window())
        messageBox.widget.setMaximumWidth(500)
        messageBox.titleLabel.setSelectable()
        messageBox.contentLabel.setSelectable()
        messageBox.contentLabel.setTextFormat(Qt.TextFormat.RichText)
        messageBox.yesButton.deleteLater()
        messageBox.cancelButton.setText("关闭")
        messageBox.show()

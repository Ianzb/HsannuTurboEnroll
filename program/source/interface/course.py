from ..program import *

from zbWidgetLib import *


class CoursePage(BasicTabPage):
    getQuerySignal = Signal()
    title = "课程"

    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(FIF.ADD_TO)
        self.getQuerySignal.connect(self.setTaskInfo)

    def setTaskInfo(self):
        if not school.query_data["data"]:
            return
        for i in school.query_data["data"]:
            page = CourseChoosePage(i, self)
            page.getTaskData()
            self.addPage(page, i["taskName"])

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def getQueryData(self):
        school.getQueryData()
        self.getQuerySignal.emit()


class CourseChoosePage(BasicTab):
    getTaskFinishedSignal = Signal(dict)

    def __init__(self, data: dict, parent):
        super().__init__(parent)
        self.data = data
        self.card1 = GrayCard("课程管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getTaskData)

        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = CardGroup("课程", self)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.cardGroup1)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignmentFlag.AlignCenter)

        self.getTaskFinishedSignal.connect(self.addTaskCard)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def getTaskData(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup1.clearCard()
        self.loadingCard.show()
        data = school.getTaskData(self.data["id"])
        self.getTaskFinishedSignal.emit(data)

    def addTaskCard(self, data):
        self.loadingCard.hide()
        for i in data["data"]["infoSubcourseList"]:
            card = CourseInfoCard(i, self)

            self.cardGroup1.addCard(card, i["sName"])
        self.reloadButton.setEnabled(True)


class CourseInfoCard(SmallInfoCard):
    """
    插件信息卡片
    """
    getResultSignal = Signal(bool)
    getJoinMessageSignal = Signal(str)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent=parent)
        self.data = data

        self.setTitle(self.data["sName"])
        self.setText(f"任课教师：{self.data["teacherName"]}", 0)
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

        self.hBoxLayout.insertSpacing(-3, -16)
        self.hBoxLayout.addWidget(self.detailButton, 0)
        self.hBoxLayout.addWidget(self.mainButton, 0)
        self.hBoxLayout.addSpacing(8)

        self.getResultSignal.connect(self.getResultMessage)
        self.getJoinMessageSignal.connect(self.getJoinMessage)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def joinCourse(self):
        school.getClubData(self.data["id"])
        result = school.joinClub(self.data["id"])
        self.getJoinMessageSignal.emit(result["msg"])
        self.check()

    def getJoinMessage(self, msg):
        infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", msg, Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        infoBar.show()
    @zb.threadPoolDecorator(program.THREAD_POOL)
    def check(self):
        while True:
            result = school.getResult(self.data["id"])
            if not result is None:
                break
            time.sleep(1)
        self.getResultSignal.emit(result)

    def getResultMessage(self, msg):
        if msg:
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "选课成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "选课失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        infoBar.show()

    def showDetail(self):
        school.getClubData(self.data["id"])
        data = school.club_data["data"]
        content = (f"课程名称：{data["sName"]}\n"
                   f"课程类型：{data["cName"]}，{data["category"]}\n"
                   f"学期：{data["semesterName"]}\n"
                   f"上课教师：{data["className"]}\n"
                   f"上课地点：{data["adress"]}\n"
                   f"课程人数：已报名{data["numberLimit"] - data["number"]}人，剩余{data["number"]}位，人数限制{data["numberLimit"]}人\n"
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
        self.cancelButton.deleteLater()
        # self.cancelButton.clicked.connect(self.close)

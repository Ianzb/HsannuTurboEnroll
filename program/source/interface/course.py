from .widget import *


class CoursePage(zbw.BasicTabPage):
    getQuerySignal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(FIF.ADD_TO)
        self.setTitle("选课列表")
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


class CourseChoosePage(zbw.BasicTab):
    getTaskFinishedSignal = pyqtSignal(dict)

    def __init__(self, data: dict, parent):
        super().__init__(parent)
        self.data = data
        self.card1 = zbw.GrayCard("课程管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getTaskData)

        self.label = BodyLabel(self)
        self.label.setText(f"时间：{self.data["startTime"]}-{self.data["endTime"]}")

        self.card1.addWidget(self.reloadButton)
        self.card1.addWidget(self.label,1,Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignVCenter)
        self.reloadButton.setEnabled(False)

        self.cardGroup1 = zbw.CardGroup("课程", self)

        self.loadingCard = zbw.LoadingCard(self)
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
            card = CourseInfoCard(i, self,data["data"]["id"])

            self.cardGroup1.addCard(card, i["sName"])
        self.reloadButton.setEnabled(True)



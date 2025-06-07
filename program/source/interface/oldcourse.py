from .widget import *


class OldCoursePage(zbw.BasicTabPage):
    getQuerySignal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(FIF.TILES)
        self.setTitle("已选课程")
        self.getQuerySignal.connect(self.setTaskInfo)

    def setTaskInfo(self):
        for k, v in {1: "模块选修课", 0: "校本选课"}.items():
            page = CourseChoosePage(k, v, self)
            page.getTaskData()
            self.addPage(page, v)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def getQueryData(self):
        school.getOldCourse(0)
        self.getQuerySignal.emit()


class CourseChoosePage(zbw.BasicTab):
    getTaskFinishedSignal = pyqtSignal(dict)

    def __init__(self, id: int, name: str, parent):
        super().__init__(parent)
        self.id = id
        self.card1 = zbw.GrayCard("课程管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getTaskData)

        self.card1.addWidget(self.reloadButton)
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
        data = school.getOldCourse(self.id)
        self.getTaskFinishedSignal.emit(data)

    def addTaskCard(self, data):
        self.loadingCard.hide()
        for i in data["data"]:
            card = CourseInfoCard(i, self, i, False)

            self.cardGroup1.addCard(card, i["sName"])
        self.reloadButton.setEnabled(True)

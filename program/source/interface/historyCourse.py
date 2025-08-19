from .widget import *


class HistoryCoursePage(zbw.BasicTabPage):

    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(FIF.TILES)
        self.setTitle("已选课程")

    def loadClassPage(self):
        for course_type, course_type_name in {1: "模块选修课", 0: "校本选课"}.items():
            page = HistoryClassPage(course_type, self)
            page.getHistoryClass()
            self.addPage(page, course_type_name)


class HistoryClassPage(zbw.BasicTab):
    getHistoryClassFinishedSignal = pyqtSignal(dict)

    def __init__(self, task_type: int, parent):
        super().__init__(parent)
        self.task_type = task_type
        self.card = zbw.GrayCard("历史课程", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getHistoryClass)

        self.card.addWidget(self.reloadButton)
        self.reloadButton.setEnabled(False)

        self.cardGroup = zbw.CardGroup("课程", self)

        self.loadingCard = zbw.LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card)
        self.vBoxLayout.addWidget(self.cardGroup)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.getHistoryClassFinishedSignal.connect(self.getHistoryClassFinished)

    def getHistoryClass(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup.clearCard()
        self.cardGroup.hide()
        self.loadingCard.show()
        self._getHistoryClass()

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _getHistoryClass(self):
        try:
            logging.info(f"正在获取课程信息{self.task_type}！")
            history_class = school.getHistoryClass(self.task_type)
            self.getHistoryClassFinishedSignal.emit(history_class)
        except:
            logging.error(f"获取课程信息失败{self.task_type}，报错信息：{traceback.format_exc()}！")
            self.getHistoryClassFinishedSignal.emit({})

    def getHistoryClassFinished(self, history_class):
        if history_class:
            for _class in history_class.get("data", []):
                card = ClassInfoCard(_class, self, None)
                self.cardGroup.addCard(card, _class.get("sName"))
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "加载历史选课失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            infoBar.show()
        self.reloadButton.setEnabled(True)
        self.cardGroup.show()
        self.loadingCard.hide()

from .widget import *


class CoursePage(zbw.BasicTabPage):
    getCourseDataFinishedSignal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(FIF.ADD_TO)
        self.setTitle("选课列表")
        self.getCourseDataFinishedSignal.connect(self.getCourseDataFinished)

    def getCourseData(self):
        self._getCourseData()

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _getCourseData(self):
        try:
            logging.info("正在获取选课任务信息！")
            course_data = school.getCourseData()
            self.getCourseDataFinishedSignal.emit(course_data)
        except:
            logging.error(f"获取选课任务信息失败，报错信息：{traceback.format_exc()}！")
            self.getCourseDataFinishedSignal.emit({})

    def getCourseDataFinished(self, course_data):
        if course_data:
            for course in course_data.get("data"):
                page = ClassPage(course, self)
                page.getCourseClass()
                self.addPage(page, course.get("taskName"))
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "获取选课任务信息失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            infoBar.show()


class ClassPage(zbw.BasicTab):
    getCourseClassFinishedSignal = pyqtSignal(dict)

    def __init__(self, data: dict, parent):
        super().__init__(parent)
        self.data = data
        self.card = zbw.GrayCard("课程管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getCourseClass)

        self.label = BodyLabel(self)
        self.label.setText(f"时间：{time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(self.data.get("startTime"), "%Y-%m-%d %H:%M:%S"))} - {time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(self.data.get("endTime"), "%Y-%m-%d %H:%M:%S"))}")

        self.card.addWidget(self.reloadButton)
        self.card.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.reloadButton.setEnabled(False)

        self.cardGroup = zbw.CardGroup("课程", self)

        self.loadingCard = zbw.LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card)
        self.vBoxLayout.addWidget(self.cardGroup)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignmentFlag.AlignCenter)

        self.getCourseClassFinishedSignal.connect(self.getCourseClassFinished)

    def getCourseClass(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup.clearCard()
        self.cardGroup.hide()
        self.loadingCard.show()
        self._getCourseClass()

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _getCourseClass(self):
        try:
            logging.info(f"正在获取任务课程列表{self.data.get("id")}")
            course_class = school.getCourseClass(self.data.get("id"))
            self.getCourseClassFinishedSignal.emit(course_class)
        except:
            logging.error(f"获取任务课程列表{self.data.get("id")}失败，报错信息：{traceback.format_exc()}！")
            self.getCourseClassFinishedSignal.emit({})

    def getCourseClassFinished(self, course_class):
        if course_class:
            for _class in course_class.get("data", {}).get("infoSubcourseList", []):
                card = ClassInfoCard(_class, self, course_class.get("data").get("id"))
                self.cardGroup.addCard(card, _class.get("sName"))
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "获取选课任务列表失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            infoBar.show()
        self.reloadButton.setEnabled(True)
        self.cardGroup.show()
        self.loadingCard.hide()

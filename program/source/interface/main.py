import time
import traceback

from ..program import *

from zbWidgetLib import *


class LoginPage(BasicTab):
    loginSignal = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.label1 = BodyLabel(self)
        self.label1.setText("用户名")

        self.lineEdit1 = LineEdit(self)
        self.lineEdit1.setText(setting.read("username"))
        self.lineEdit1.setPlaceholderText("example@example.com")
        self.lineEdit1.setClearButtonEnabled(True)

        self.label2 = BodyLabel(self)
        self.label2.setText("密码")

        self.lineEdit2 = LineEdit(self)
        self.lineEdit2.setText(setting.read("password"))
        self.lineEdit2.setPlaceholderText("••••••••••••")
        self.lineEdit2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit2.setClearButtonEnabled(True)

        self.checkBox = CheckBox(self)
        self.checkBox.setText("记住密码")
        self.checkBox.setChecked(True)

        self.pushButton1 = PrimaryPushButton(self)
        self.pushButton1.setText("登录")
        setToolTip(self.pushButton1, "登录账户")
        self.pushButton1.clicked.connect(self.loginButtonClicked)

        self.vBoxLayout.addWidget(self.label1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.lineEdit1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.label2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.lineEdit2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.checkBox, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.pushButton1, 0, Qt.AlignTop)

        self.loginSignal.connect(self.loginSuccess)

    def loginButtonClicked(self):
        self.pushButton1.setEnabled(False)
        if self.checkBox.isChecked():
            setting.save("username", self.lineEdit1.text())
            setting.save("password", self.lineEdit2.text())
        try:
            school.login(self.lineEdit1.text(), self.lineEdit2.text())
            self.loginSignal.emit(True)
        except Exception as ex:
            logging.error(f"登录失败，报错信息：{traceback.format_exc()}！")
            self.loginSignal.emit(False)

    def loginSuccess(self, msg):
        if msg:
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "登录成功！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
            program.THREAD_POOL.submit(self.parent().page["coursePage"].getQueryData)
            self.parent().showPage("coursePage")
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "登录失败！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        infoBar.show()
        self.pushButton1.setEnabled(True)


class CoursePage(BasicTab):
    getTaskFinishedSignal = Signal(dict)
    getTaskSignal = Signal()
    getQuerySignal = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.card1 = GrayCard("课程管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.clicked.connect(self.getQuerySignal)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("科目")
        self.comboBox1.currentIndexChanged.connect(lambda x: self.getTaskSignal.emit())

        self.card1.addWidget(self.comboBox1)
        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = CardGroup("课程", self)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.cardGroup1)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignmentFlag.AlignCenter)

        self.getQuerySignal.connect(lambda: program.THREAD_POOL.submit(self.getQueryData))
        self.getTaskSignal.connect(lambda: program.THREAD_POOL.submit(self.getTaskData))
        self.getTaskFinishedSignal.connect(self.addTaskCard)

    def getQueryData(self):
        self.loadingCard.show()
        self.comboBox1.setEnabled(False)
        self.reloadButton.setEnabled(False)
        self.cardGroup1.hide()
        self.comboBox1.currentIndexChanged.disconnect(self.getTaskSignal.emit)

        data = school.getQueryData()["data"]
        self.comboBox1.clear()
        for i in data:
            self.comboBox1.addItem(i["taskName"])
        self.comboBox1.currentIndexChanged.connect(self.getTaskSignal.emit)
        self.comboBox1.setCurrentIndex(0)
        self.getTaskSignal.emit()

    def getTaskData(self):
        self.cardGroup1.hide()
        self.loadingCard.show()
        task_id = [i["id"] for i in school.query_data["data"] if i["taskName"] == self.comboBox1.currentText()][0]
        data = school.getTaskData(task_id)
        self.getTaskFinishedSignal.emit(data)

    def addTaskCard(self, data):
        self.cardGroup1.clearCard()
        self.loadingCard.hide()
        self.cardGroup1.show()
        self.cardGroup1.setTitle(data["data"]["taskName"])
        for i in data["data"]["infoSubcourseList"]:
            card = CourseInfoCard(i, self)

            self.cardGroup1.addCard(card, i["sName"])
        self.comboBox1.setEnabled(True)
        self.reloadButton.setEnabled(True)


class CourseInfoCard(SmallInfoCard):
    """
    插件信息卡片
    """
    getResultEvent = Signal(bool)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent=parent)
        self.data = data

        self.setTitle(self.data["sName"])
        self.setInfo(f"任课教师：{self.data["teacherName"]}", 0)
        self.setInfo(f"已报名{self.data["numberLimit"] - self.data["number"]}人，剩余{self.data["number"]}人，人数限制{self.data["numberLimit"]}人", 1)
        self.setInfo(f"{self.data["number"]}/{self.data["numberLimit"]}", 3)

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

        self.getResultEvent.connect(self.getResultMssage)

    def joinCourse(self):
        school.getClubData(self.data["id"])
        result = school.joinClub(self.data["id"])
        infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", result["msg"], Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        infoBar.show()
        program.THREAD_POOL.submit(self.check)

    def check(self):
        while True:
            result = school.getResult(self.data["id"])
            if not result is None:
                break
            time.sleep(1)
        self.getResultEvent.emit(result)

    def getResultMssage(self, msg):
        if msg:
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "选课成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "选课失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
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


class MainPage(ChangeableTab):
    """
    主页
    """
    title = "主页"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.loginPage = LoginPage(self)
        self.coursePage = CoursePage(self)
        self.addPage(self.loginPage, "loginPage")
        self.addPage(self.coursePage, "coursePage")
        self.showPage("loginPage")

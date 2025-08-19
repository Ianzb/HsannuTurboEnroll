from .widget import *


class LoginPage(zbw.BasicTab):
    loginFinishedSignal = pyqtSignal(bool)

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

        self.loginButton = PrimaryPushButton(self)
        self.loginButton.setText("登录")
        zbw.setToolTip(self.loginButton, "登录账户")
        self.loginButton.clicked.connect(self.login)

        self.vBoxLayout.addWidget(self.label1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.lineEdit1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.label2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.lineEdit2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.checkBox, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.loginButton, 0, Qt.AlignTop)

        self.loginFinishedSignal.connect(self.loginFinished)

    def login(self):
        self.loginButton.setEnabled(False)
        if self.checkBox.isChecked():
            setting.save("username", self.lineEdit1.text())
            setting.save("password", self.lineEdit2.text())
        self.loadingMessageBox = zbw.LoadingMessageBox(self.window())
        self.loadingMessageBox.show()
        self._login()

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _login(self):
        try:
            logging.info(f"正在登录{self.lineEdit1.text()}，{self.lineEdit2.text()}。")
            school.login(self.lineEdit1.text(), self.lineEdit2.text())
            self.loginFinishedSignal.emit(True)
        except Exception as ex:
            logging.error(f"登录{self.lineEdit1.text()}，{self.lineEdit2.text()}失败，报错信息：{traceback.format_exc()}！")
            self.loginFinishedSignal.emit(False)

    def loginFinished(self, msg):
        if msg:
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "登录成功！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
            self.parent().getPage("userInfoPage").setUserInfo()
            self.parent().showPage("userInfoPage")
            self.window().coursePage.getCourseData()
            self.window().historyCoursePage.loadClassPage()
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "登录失败！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        infoBar.show()
        self.loginButton.setEnabled(True)
        self.loadingMessageBox.close()


class UserInfoPage(zbw.BasicTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.bigInfoCard = zbw.BigInfoCard(self, tag=False)
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.deleteLater()
        self.bigInfoCard.image.deleteLater()
        self.vBoxLayout.addWidget(self.bigInfoCard)

    def setUserInfo(self):
        student_data = school.student_data
        self.bigInfoCard.setTitle(student_data.get("studentInfo", {}).get("infoStudent", {}).get("name"))
        self.bigInfoCard.addUrl("浏览器中打开", "http://ms.do-ok.com:1001/login?sc=2201023001")
        self.bigInfoCard.addData("创建日期", time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(student_data.get("studentInfo", {}).get("infoStudent", {}).get("createTime"), "%Y-%m-%d %H:%M:%S")))
        self.bigInfoCard.addData("更新日期", time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(student_data.get("studentInfo", {}).get("infoStudent", {}).get("updateTime"), "%Y-%m-%d %H:%M:%S")))


class MainPage(zbw.ChangeableTab):
    """
    主页
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitle("主页")
        self.setIcon(FIF.HOME)

        self.loginPage = LoginPage(self)
        self.userInfoPage = UserInfoPage(self)
        self.addPage(self.loginPage, "loginPage")
        self.addPage(self.userInfoPage, "userInfoPage")
        self.showPage("loginPage")

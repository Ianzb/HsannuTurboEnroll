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
            self.parent().getPage("userInfoPage").setUserInfo()
            self.parent().showPage("userInfoPage")
            self.window().coursePage.getQueryData()
            self.window().oldCoursePage.getQueryData()
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "登录失败！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        infoBar.show()
        self.pushButton1.setEnabled(True)


class UserInfoPage(BasicTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.bigInfoCard = BigInfoCard(self,tag=False)
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.deleteLater()
        self.bigInfoCard.image.deleteLater()
        self.vBoxLayout.addWidget(self.bigInfoCard)

    def setUserInfo(self):
        user_info = school.student_data
        self.bigInfoCard.setTitle(user_info["studentInfo"]["infoStudent"]["name"])
        self.bigInfoCard.addUrl("浏览器打开", "http://ms.do-ok.com:1001/login?sc=2201023001")
        self.bigInfoCard.addData("创建日期", time.strftime("%Y-%m-%d", time.strptime(user_info["studentInfo"]["infoStudent"]["createTime"], "%Y-%m-%d %H:%M:%S")))
        self.bigInfoCard.addData("更新日期", time.strftime("%Y-%m-%d", time.strptime(user_info["studentInfo"]["infoStudent"]["updateTime"], "%Y-%m-%d %H:%M:%S")))

class MainPage(ChangeableTab):
    """
    主页
    """
    title = "主页"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.loginPage = LoginPage(self)
        self.userInfoPage = UserInfoPage(self)
        self.addPage(self.loginPage, "loginPage")
        self.addPage(self.userInfoPage, "userInfoPage")
        self.showPage("loginPage")

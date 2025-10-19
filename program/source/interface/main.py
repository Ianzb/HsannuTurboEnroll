from .widget import *


class AccountInfoCard(zbw.SmallInfoCard):
    def __init__(self, parent=None, username: str = None, password: str = None):
        super().__init__(parent, True)
        self.username = username
        self.password = password

        self.image.deleteLater()

        self.checkBox = CheckBox("自动登录", self)

        autoLogin = setting.read("autoLogin")
        self.checkBox.setChecked(autoLogin == self.username)
        if self.checkBox.isChecked() or autoLogin == "":
            self.checkBox.show()
        else:
            self.checkBox.setHidden(bool(autoLogin))
        self.checkBox.stateChanged.connect(self.comboBoxClicked)

        self.deleteButton = PushButton("删除", self)
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        self.editButton = PushButton("修改", self)
        self.editButton.clicked.connect(self.editButtonClicked)

        self.mainButton.clicked.connect(self.mainButtonClicked)
        self.mainButton.setText("登录")

        self.setTitle(self.username)
        self.setText(self.password, 0)

        self.hBoxLayout.addSpacing(-16)
        self.hBoxLayout.insertWidget(4, self.editButton)
        self.hBoxLayout.insertWidget(4, self.deleteButton)
        self.hBoxLayout.insertWidget(4, self.checkBox)
        self.hBoxLayout.addSpacing(12)

        setting.changeSignal.connect(self.set)

    def comboBoxClicked(self):
        if self.checkBox.isChecked():
            setting.save("autoLogin", self.username)
        else:
            setting.save("autoLogin", "")

    def set(self, msg):
        if msg == "autoLogin":
            self.checkBox.blockSignals(True)
            autoLogin = setting.read("autoLogin")
            self.checkBox.setChecked(autoLogin == self.username)
            if self.checkBox.isChecked() or autoLogin == "":
                self.checkBox.show()
            else:
                self.checkBox.setHidden(bool(autoLogin))
            self.checkBox.blockSignals(False)

    def deleteButtonClicked(self):
        self.parent().parent().parent().parent()._remove(self.username)

    def editButtonClicked(self):
        messageBox = AccountMessageBox(self.window(), self.username, self.password)
        messageBox.show()

    def mainButtonClicked(self):
        self.mainButton.setEnabled(False)
        self.parent().parent().parent().parent().loginSignal.connect(self.loginFinished)
        self.parent().parent().parent().parent().login(self.username, self.password)

    def loginFinished(self, msg):
        self.parent().parent().parent().parent().loginSignal.disconnect(self.loginFinished)

        self.mainButton.setEnabled(True)


class AccountMessageBox(MessageBoxBase):
    def __init__(self, parent=None, username: str = None, password: str = None):
        super().__init__(parent)
        self.username = username
        self.password = password

        self.yesButton.setText("确认")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.titleLabel = TitleLabel("登录账号", self)
        self.label1 = BodyLabel(self)
        self.label1.setText("用户名")

        self.lineEdit1 = LineEdit(self)
        if username:
            self.lineEdit1.setText(username)
        self.lineEdit1.setPlaceholderText("账号")
        self.lineEdit1.setClearButtonEnabled(True)

        self.lineEdit1.textChanged.connect(self.textChanged)

        self.label2 = BodyLabel(self)
        self.label2.setText("密码")

        self.lineEdit2 = LineEdit(self)
        if password:
            self.lineEdit2.setText(password)
        self.lineEdit2.setPlaceholderText("••••••••••••")
        self.lineEdit2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit2.setClearButtonEnabled(True)
        self.lineEdit2.textChanged.connect(self.textChanged)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.label1, 0, Qt.AlignTop)
        self.viewLayout.addWidget(self.lineEdit1, 0, Qt.AlignTop)
        self.viewLayout.addWidget(self.label2, 0, Qt.AlignTop)
        self.viewLayout.addWidget(self.lineEdit2, 0, Qt.AlignTop)

        self.widget.setFixedWidth(300)

        self.textChanged()

    def textChanged(self):
        self.yesButton.setEnabled(bool(self.lineEdit1.text() and self.lineEdit2.text()))

    def yesButtonClicked(self):
        if self.username:
            self.window().mainPage._remove(self.username, False)
        self.window().mainPage._set(self.lineEdit1.text(), self.lineEdit2.text())


class MainPage(zbw.BasicTab):
    """
    主页
    """
    loginSignal = pyqtSignal(dict)
    loadAccountSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)
        self.setTitle("主页")

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.grayCard = zbw.GrayCard("账号管理", self)

        self.addAccountButton = PrimaryPushButton("添加账号", self, FIF.ADD)
        self.addAccountButton.clicked.connect(self.addAccount)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.setEnabled(True)
        self.reloadButton.clicked.connect(self.loadAccount)

        self.grayCard.addWidget(self.addAccountButton)
        self.grayCard.addWidget(self.reloadButton)

        self.cardGroup = zbw.CardGroup("账号列表", self)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.grayCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup, 0, Qt.AlignTop)

        self.loginSignal.connect(self.loginFinished)
        self.loadAccountSignal.connect(self.loadAccountFinished)

        self.loadAccount()

    def _get(self):
        if zb.existPath(program.ACCOUNTS_PATH):
            with open(zb.joinPath(program.ACCOUNTS_PATH), "r", encoding="utf-8") as file:
                accounts: dict = json.load(file)
            return accounts
        else:
            with open(zb.joinPath(program.ACCOUNTS_PATH), "w", encoding="utf-8") as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
            return {}

    def _set(self, username: str, password: str, reset: bool = True):
        accounts = self._get()
        accounts.update({username: password})
        with open(zb.joinPath(program.ACCOUNTS_PATH), "w", encoding="utf-8") as file:
            json.dump(accounts, file, ensure_ascii=False, indent=4)
        if reset:
            self.loadAccount()

    def _remove(self, account: str, reset: bool = True):
        accounts = self._get()
        if account in accounts.keys():
            del accounts[account]
        with open(zb.joinPath(program.ACCOUNTS_PATH), "w", encoding="utf-8") as file:
            json.dump(accounts, file, ensure_ascii=False, indent=4)
        if reset:
            self.loadAccount()

    def loadAccount(self):
        """
        加载账号列表
        """
        self.reloadButton.setEnabled(False)
        self.cardGroup.clearCard()

        self._loadAccount()

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _loadAccount(self):
        try:
            logging.info("正在读取账号列表。")
            accounts = self._get()
            self.loadAccountSignal.emit(accounts)
        except:
            logging.error(f"读取账号列表失败，报错信息：{traceback.format_exc()}！")
            self.loadAccountSignal.emit({})

    def loadAccountFinished(self, accounts: dict):
        if setting.get("autoLogin") not in accounts.keys():
            setting.set("autoLogin", "")
        for username, password in accounts.items():
            card = AccountInfoCard(self, username, password)
            self.cardGroup.addCard(card, username)
            if username == setting.get("autoLogin"):
                card.mainButton.click()
        self.reloadButton.setEnabled(True)

    def login(self, username: str, password: str):
        self.loadingMessageBox = zbw.LoadingMessageBox(self.window())
        self.loadingMessageBox.show()
        self._login(username, password)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def _login(self, username: str, password: str):
        try:
            logging.info(f"正在登录{username}，{password}。")
            student_data = school.login(username, password)
            self.loginSignal.emit(student_data)
        except:
            logging.error(f"登录{username}，{password}失败，报错信息：{traceback.format_exc()}！")
            self.loginSignal.emit({})

    def loginFinished(self, student_data):
        if student_data:
            if student_data.get("msg") == "密码错误":
                infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "密码错误！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
            else:
                try:
                    self.vBoxLayout.removeWidget(self.bigInfoCard)
                    self.bigInfoCard.deleteLater()
                except:
                    pass
                self.bigInfoCard = zbw.BigInfoCard(self, tag=False, select_text=True)
                self.bigInfoCard.backButton.deleteLater()
                self.bigInfoCard.mainButton.deleteLater()
                self.bigInfoCard.image.deleteLater()

                self.bigInfoCard.setTitle(student_data.get("studentInfo", {}).get("infoStudent", {}).get("name"))
                self.bigInfoCard.addUrl("浏览器中打开", "http://ms.do-ok.com:1001/login?sc=2201023001")
                self.bigInfoCard.addData("账号", student_data.get("studentInfo", {}).get("infoStudent", {}).get("studentCode"))
                self.bigInfoCard.addData("身份证号码", student_data.get("studentInfo", {}).get("infoStudent", {}).get("idNo"))
                self.bigInfoCard.addData("创建日期", time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(student_data.get("studentInfo", {}).get("infoStudent", {}).get("createTime"), "%Y-%m-%d %H:%M:%S")))
                self.bigInfoCard.addData("更新日期", time.strftime("%Y年%#m月%#d日 %H:%M:%S", time.strptime(student_data.get("studentInfo", {}).get("infoStudent", {}).get("updateTime"), "%Y-%m-%d %H:%M:%S")))

                self.vBoxLayout.insertWidget(2, self.bigInfoCard)

                self.window().coursePage.getCourseData()
                self.window().historyCoursePage.loadClassPage()

                infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "登录成功！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "登录失败！", Qt.Orientation.Vertical, True, 2500, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
        infoBar.show()
        self.loadingMessageBox.close()

    def addAccount(self):
        messageBox = AccountMessageBox(self.window())
        messageBox.show()

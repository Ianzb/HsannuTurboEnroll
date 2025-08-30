from .widget import *


class ThemeSettingCard(ExpandSettingCard):
    """
    主题设置卡片
    """
    themeChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, parent=None):
        super().__init__(FIF.BRUSH, "模式", "更改显示的颜色", parent)
        self.label = BodyLabel(self)

        self.addWidget(self.label)

        self.radioButton1 = RadioButton("浅色", self.view)

        self.radioButton2 = RadioButton("深色", self.view)

        self.radioButton3 = RadioButton("跟随系统设置", self.view)

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

        self.buttonGroup.addButton(self.radioButton1)
        self.buttonGroup.addButton(self.radioButton2)
        self.buttonGroup.addButton(self.radioButton3)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        self.viewLayout.addWidget(self.radioButton1)
        self.viewLayout.addWidget(self.radioButton2)
        self.viewLayout.addWidget(self.radioButton3)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self._adjustViewSize()

    def setEvent(self, msg):
        if msg == "theme":
            self.set()

    def set(self):
        self.buttonGroup.buttonClicked.disconnect(self.buttonGroupClicked)
        if setting.read("theme") == "Theme.LIGHT":
            self.radioButton1.setChecked(True)
            setTheme(Theme.LIGHT, lazy=True)
            self.label.setText("浅色")
        elif setting.read("theme") == "Theme.DARK":
            self.radioButton2.setChecked(True)
            setTheme(Theme.DARK, lazy=True)
            self.label.setText("深色")
        elif setting.read("theme") == "Theme.AUTO":
            self.radioButton3.setChecked(True)
            setTheme(Theme.AUTO, lazy=True)
            self.label.setText("跟随系统设置")
        self.label.adjustSize()
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

    def buttonGroupClicked(self, button: RadioButton):
        if button.text() == self.label.text():
            return
        if button is self.radioButton1:
            setting.save("theme", "Theme.LIGHT")
            setTheme(Theme.LIGHT, lazy=True)
        elif button is self.radioButton2:
            setting.save("theme", "Theme.DARK")
            setTheme(Theme.DARK, lazy=True)
        else:
            setting.save("theme", "Theme.AUTO")
            setTheme(Theme.AUTO, lazy=True)

        self.label.setText(button.text())
        self.label.adjustSize()


class ColorSettingCard(ExpandGroupSettingCard):
    """
    主题色设置卡片
    """
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(FIF.PALETTE, "主题色", "更改程序的主题色", parent=parent)
        self.label1 = BodyLabel(self)

        self.addWidget(self.label1)

        self.radioWidget = QWidget(self.view)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)

        self.label2 = BodyLabel("自定义颜色", self.customColorWidget)

        self.radioLayout = QVBoxLayout(self.radioWidget)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        self.button1 = RadioButton("系统默认", self.radioWidget)

        self.button2 = RadioButton("自定义", self.radioWidget)

        self.button3 = QPushButton("选择颜色", self.customColorWidget)
        self.button3.setNewToolTip("选择自定义颜色")
        self.button3.clicked.connect(self.showColorDialog)

        self.radioLayout.addWidget(self.button1)
        self.radioLayout.addWidget(self.button2)

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.button1)
        self.buttonGroup.addButton(self.button2)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)

        self.customColorLayout.addWidget(self.label2, 0, Qt.AlignLeft)
        self.customColorLayout.addWidget(self.button3, 0, Qt.AlignRight)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.customColorWidget)

        self._adjustViewSize()

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def getDefaultColor(self):
        from qframelesswindow.utils import getSystemAccentColor
        sysColor = getSystemAccentColor()
        if sysColor.isValid():
            return sysColor.name()
        else:
            return "#0078D4"

    def set(self):
        self.buttonGroup.buttonClicked.disconnect(self.buttonGroupClicked)
        if setting.read("themeColor") == "default":
            self.button1.setChecked(True)
            self.button3.setEnabled(False)
            self.color = QColor(self.getDefaultColor())
        else:
            self.button2.setChecked(True)
            self.button3.setEnabled(True)
            self.color = QColor(setting.read("themeColor"))

        self.label1.setText(self.buttonGroup.checkedButton().text())
        self.label1.adjustSize()
        setThemeColor(self.color, lazy=True)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

    def setEvent(self, msg):
        if msg == "themeColor":
            self.set()

    def buttonGroupClicked(self, button: RadioButton):
        if button.text() == self.label1.text():
            return

        self.label1.setText(button.text())
        self.label1.adjustSize()

        if button is self.button1:
            self.button3.setDisabled(True)
            setting.save("themeColor", "default")
            setThemeColor(QColor(self.getDefaultColor()), lazy=True)
        else:
            self.button3.setDisabled(False)
            setting.save("themeColor", self.color.name())
            setThemeColor(self.color, lazy=True)

    def showColorDialog(self):
        colorDialog = ColorDialog(setting.read("themeColor"), "选择颜色", self.window())
        colorDialog.colorChanged.connect(self.__colorChanged)
        colorDialog.exec()

    def __colorChanged(self, color):
        setThemeColor(color, lazy=True)
        self.color = QColor(color)
        setting.save("themeColor", self.color.name())
        self.colorChanged.emit(color)


class MicaEffectSettingCard(SettingCard):
    """
    云母效果设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.TRANSPARENT, "云母效果", "", parent)
        self.button1 = SwitchButton(self, IndicatorPosition.RIGHT)
        self.button1.setChecked(setting.read("micaEffect"))
        self.button1.checkedChanged.connect(self.button1Clicked)
        self.button1.setNewToolTip("开启 Windows 11 的窗口模糊效果")

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def set(self):
        self.button1.checkedChanged.disconnect(self.button1Clicked)
        self.button1.setChecked(setting.read("micaEffect"))
        self.window().setMicaEffectEnabled(setting.read("micaEffect"))
        self.button1.checkedChanged.connect(self.button1Clicked)

    def setEvent(self, msg):
        if msg == "micaEffect":
            self.set()

    def button1Clicked(self):
        setting.save("micaEffect", self.button1.checked)
        self.window().setMicaEffectEnabled(self.button1.checked)


class ThreadNumberSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.SEND, "线程数", "设置抢课线程数量", parent)
        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("线程数")
        self.lineEdit.setNewToolTip("设置抢课线程数量")
        self.lineEdit.textChanged.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QIntValidator())

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def set(self):
        self.lineEdit.textChanged.disconnect(self.textChanged)
        self.lineEdit.returnPressed.disconnect(self.textChanged)
        self.lineEdit.setText(str(setting.read("threadNumber")))
        self.lineEdit.textChanged.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)

    def setEvent(self, msg):
        if msg == "threadNumber":
            self.set()

    def textChanged(self):
        if self.lineEdit.text().isdigit():
            setting.save("threadNumber", int(self.lineEdit.text()))


class RequestDelaySettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.SPEED_HIGH, "延迟", "发送新抢课请求间的延迟", parent)
        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("延迟秒数")
        self.lineEdit.setNewToolTip("发送新抢课请求间的延迟")
        self.lineEdit.textChanged.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QDoubleValidator())

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def set(self):
        self.lineEdit.textChanged.disconnect(self.textChanged)
        self.lineEdit.returnPressed.disconnect(self.textChanged)
        self.lineEdit.setText(str(setting.read("requestDelay")))
        self.lineEdit.textChanged.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)

    def setEvent(self, msg):
        if msg == "requestDelay":
            self.set()

    def textChanged(self):
        try:
            float(self.lineEdit.text())
        except:
            return
        setting.save("requestDelay", float(self.lineEdit.text()))


class SettingPage(zbw.BasicPage):
    """
    设置页面
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setViewportMargins(0, 70, 0, 0)
        self.setTitle("设置")
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = zbw.CardGroup("外观", self)
        self.cardGroup2 = zbw.CardGroup("功能", self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.threadNumberSettingCard = ThreadNumberSettingCard(self)
        self.requestDelaySettingCard = RequestDelaySettingCard(self)

        self.cardGroup1.addCard(self.themeSettingCard, "themeSettingCard")
        self.cardGroup1.addCard(self.colorSettingCard, "colorSettingCard")
        self.cardGroup1.addCard(self.micaEffectSettingCard, "micaEffectSettingCard")

        self.cardGroup2.addCard(self.threadNumberSettingCard, "threadNumberSettingCard")
        self.cardGroup2.addCard(self.requestDelaySettingCard, "requestDelaySettingCard")

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)

        if not (zb.SYSTEM_VERSION[0] >= 10 and zb.SYSTEM_VERSION[2] >= 22000):
            self.micaEffectSettingCard.hide()

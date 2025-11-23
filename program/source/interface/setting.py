from .widget import *


class ThemeSettingCard(ExpandSettingCard):
    """
    主题设置卡片
    """

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

        setting.connect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self._adjustViewSize()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(100)

    def timerEvent(self):
        if self.window().isVisible() and setting.read("theme") == "Theme.AUTO":
            t = darkdetect.theme()
            t = Theme(t) if t else Theme.LIGHT
            if qconfig._cfg._theme != t:
                setTheme(t)
                qconfig.themeChanged.emit(t)

            qconfig._cfg._theme = t

    def setEvent(self, msg):
        if msg == "theme":
            self.set()

    def set(self):
        self.buttonGroup.blockSignals(True)
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
        self.buttonGroup.blockSignals(False)

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

        setting.connect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(100)

    def timerEvent(self):
        if self.window().isVisible() and setting.read("themeColor") == "default":
            color = QColor(self.getDefaultColor())
            if self.color != color:
                self.color = color
                setThemeColor(QColor(self.color), lazy=True)

    def getDefaultColor(self):
        from qframelesswindow.utils import getSystemAccentColor
        sysColor = getSystemAccentColor()
        if sysColor.isValid():
            return sysColor.name()
        else:
            return "#0078D4"

    def set(self):
        self.buttonGroup.blockSignals(True)
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
        self.buttonGroup.blockSignals(False)

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


class WindowEffectSettingCard(ExpandSettingCard):
    """
    背景材质设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.TRANSPARENT, "背景材质", "设置窗口背景材质，需要系统支持", parent)
        self.label = BodyLabel(self)

        self.addWidget(self.label)

        self.radioButton1 = RadioButton("无", self.view)

        self.radioButton2 = RadioButton("Mica", self.view)

        self.radioButton3 = RadioButton("Mica Alt", self.view)
        self.radioButton4 = RadioButton("Acrylic", self.view)
        self.radioButton5 = RadioButton("Aero", self.view)

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

        self.buttonGroup.addButton(self.radioButton1)
        self.buttonGroup.addButton(self.radioButton2)
        self.buttonGroup.addButton(self.radioButton3)
        self.buttonGroup.addButton(self.radioButton4)
        self.buttonGroup.addButton(self.radioButton5)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        self.viewLayout.addWidget(self.radioButton1)
        self.viewLayout.addWidget(self.radioButton2)
        self.viewLayout.addWidget(self.radioButton3)
        self.viewLayout.addWidget(self.radioButton4)
        self.viewLayout.addWidget(self.radioButton5)

        setting.connect(self.setEvent)
        qconfig.themeChangedFinished.connect(self.set)
        self.window().initFinished.connect(self.set)

        self._adjustViewSize()

    def setEvent(self, msg):
        if msg == "windowEffect":
            self.set()

    def set(self):
        self.buttonGroup.blockSignals(True)
        window_effect = setting.read("windowEffect")
        if window_effect:
            self.window().setEffect(window_effect)
            self.label.setText(window_effect)
            for i in self.buttonGroup.buttons():
                if i.text() == window_effect:
                    i.setChecked(True)
        else:
            self.window().removeEffect()
            self.label.setText("无")
            self.radioButton1.setChecked(True)
        self.label.adjustSize()
        self.buttonGroup.blockSignals(False)

    def buttonGroupClicked(self, button: RadioButton):
        text = button.text()
        if text == self.label.text():
            return
        if text == "无":
            setting.save("windowEffect", "")
        else:
            setting.save("windowEffect", text)


class ThreadNumberSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.SEND, "线程数", "设置抢课线程数量", parent)
        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("线程数")
        self.lineEdit.setNewToolTip("设置抢课线程数量")
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QIntValidator())

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.connect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("threadNumber")))
        self.lineEdit.blockSignals(False)

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
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QDoubleValidator())

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.connect(self.setEvent)
        self.window().initFinished.connect(self.set)

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("requestDelay")))
        self.lineEdit.blockSignals(False)

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
        self.windowEffectSettingCard = WindowEffectSettingCard(self)

        self.threadNumberSettingCard = ThreadNumberSettingCard(self)
        self.requestDelaySettingCard = RequestDelaySettingCard(self)

        self.cardGroup1.addCard(self.themeSettingCard, "themeSettingCard")
        self.cardGroup1.addCard(self.colorSettingCard, "colorSettingCard")
        self.cardGroup1.addCard(self.windowEffectSettingCard, "windowEffectSettingCard")

        self.cardGroup2.addCard(self.threadNumberSettingCard, "threadNumberSettingCard")
        self.cardGroup2.addCard(self.requestDelaySettingCard, "requestDelaySettingCard")

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)

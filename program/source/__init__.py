from .interface import *


class Window(zbw.Window):
    """
    主窗口
    """
    initFinished = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.mainPage = MainPage(self)
        self.coursePage = CoursePage(self)
        self.taskPage = TaskPage(self)
        self.historyCoursePage = HistoryCoursePage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)
        self.addPage(self.mainPage, self.mainPage.title(), self.mainPage.icon(), "top")
        self.addSeparator("top")
        self.addPage(self.coursePage, self.coursePage.title(), self.coursePage.icon(), "scroll")
        self.addPage(self.historyCoursePage, self.historyCoursePage.title(), self.historyCoursePage.icon(), "scroll")
        self.addPage(self.taskPage, self.taskPage.title(), self.taskPage.icon(), "scroll")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, self.settingPage.title(), self.settingPage.icon(), "bottom")
        self.addPage(self.aboutPage, self.aboutPage.title(), self.aboutPage.icon(), "bottom")

        # 外观调整
        self.navigationInterface.setAcrylicEnabled(True)
        # 窗口属性
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.ICON))
        self.setWindowTitle(program.TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        self.show()
        self.resize(900, 700)
        # 窗口居中
        desktop = QApplication.screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 设置数据异常提醒
        if setting.errorState:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "设置文件数据错误，已自动恢复至默认选项，具体错误原因请查看程序日志！", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()
        self.initFinished.emit()

    def closeEvent(self, QCloseEvent):
        program.close()


logging.debug("程序主窗口类初始化成功！")

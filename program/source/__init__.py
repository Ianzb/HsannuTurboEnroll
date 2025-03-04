from .interface import *
from .interface.course import CoursePage


class Window(FluentWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()

        self.mainPage = MainPage(self)
        self.coursePage = CoursePage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addSeparator("top")
        self.addPage(self.coursePage, "scroll")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

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

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key.Key_Escape:
            if setting.read("hideWhenClose"):
                self.hide()

    def addPage(self, page, pos: str):
        """
        添加导航栏页面简易版
        @param page: 页面对象
        @param pos: 位置top/scroll/bottom
        """
        return self.addSubInterface(page, page.getIcon(), page.objectName(), eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))


logging.debug("程序主窗口类初始化成功！")

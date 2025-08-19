from ..program import *


class ClassInfoCard(zbw.SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, data: dict, parent=None, task_id=None):
        super().__init__(parent=parent)
        self.data = data
        self.task_id = task_id

        self.setTitle(self.data.get("sName"))
        self.setText(f"任课教师：{self.data.get("teacherName")}", 0)
        if self.data.get("numberLimit"):
            self.setText(f"已报名{self.data.get("numberLimit") - self.data.get("number")}人，剩余{self.data.get("number")}人，人数限制{self.data.get("numberLimit")}人", 1)
            self.setText(f"{self.data.get("number")}/{self.data.get("numberLimit")}", 3)

        self.image.deleteLater()
        self.mainButton.deleteLater()

        self.detailButton = PushButton(self)
        self.detailButton.setText("详细信息")
        self.detailButton.clicked.connect(self.showDetail)

        self.mainButton = PrimaryPushButton(self)
        self.mainButton.setText("报名")
        self.mainButton.clicked.connect(self.joinClass)
        self.mainButton.setVisible(bool(self.task_id))

        self.hBoxLayout.insertSpacing(-3, -16)
        self.hBoxLayout.addWidget(self.detailButton, 0)
        self.hBoxLayout.addWidget(self.mainButton, 0)
        self.hBoxLayout.addSpacing(8)

    def joinClass(self):
        infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "已提交选课任务！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().coursePage)
        infoBar.show()
        self.window().taskPage.addTask(self.data, self.task_id)

    def showDetail(self):
        class_data = school.getClassData(self.data.get("id"))
        data = class_data.get("data", {})
        content = (f"课程名称：{data.get("sName")}\n"
                   f"课程类型：{data.get("cName")}，{data.get("category")}\n"
                   f"学期：{data.get("semesterName")}\n"
                   f"上课教师：{data.get("teacherName")}\n"
                   f"上课地点：{data.get("adress")}\n"
                   f"课程人数：已报名{data.get("numberLimit") - data.get("number")}人，剩余{data.get("number")}人，人数限制{data.get("numberLimit")}人\n"
                   f"课程简介：{data.get("introduction")}\n"
                   f"教师简介：{data.get("teacherIntroduction")}\n"
                   f"能力水平：{data.get("abilityLevel")}\n"
                   f"特殊要求：{data.get("specialAsk")}\n"
                   f"评价方式：{data.get("evaluateType")}\n")
        messageBox = CoureseMessageBox(data.get("sName"), content, self.window())
        messageBox.show()


class CoureseMessageBox(MessageBoxBase):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(title, self)
        self.titleLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.widget.setMinimumWidth(500)
        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")

        self.scrollArea = zbw.BasicTab(self)
        self.scrollArea.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.contentLabel = BodyLabel(content, self)
        self.contentLabel.setWordWrap(True)
        self.contentLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.scrollArea.vBoxLayout.addWidget(self.contentLabel)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.scrollArea, 0)

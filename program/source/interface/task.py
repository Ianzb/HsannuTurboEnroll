from .widget import *


class TaskPage(zbw.BasicTab):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(FIF.LABEL)
        self.setTitle("任务")
        self.cardGroup = zbw.CardGroup("抢课任务", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def addTask(self, msg, task_id):
        id = msg["id"] + str(time.time())
        card = TaskCard(msg, task_id, id, self)
        self.cardGroup.addCard(card, id)
        card.thread_pool.submit(card.joinCourse)
        self.setNum()

    def setNum(self):
        item = self.window().navigationInterface.widget("任务")
        w = InfoBadge.attension(
            text=self.cardGroup.count(),
            parent=item.parent(),
            target=item,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )


class TaskCard(zbw.SmallInfoCard):
    getResultSignal = pyqtSignal(str)

    def __init__(self, data, task_id, id, parent):
        super().__init__(parent)
        self.data = data
        self.task_id = task_id
        self.id = id
        self.result = {}
        self.club_data = {}

        self.delay = setting.read("requestDelay")
        self.thread_pool = ThreadPoolExecutor(max_workers=setting.read("threadNumber") + 2)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateText)
        self.timer.start(100)

        self.image.deleteLater()
        self.setFixedHeight(73 * 2)
        self.setTitle(f"{self.data["sName"]} 抢课中...")
        self.mainButton.setText("停止")
        self.mainButton.clicked.connect(self.stop)
        self.getResultSignal.connect(self.getResultMessage)

    def stop(self):
        self.mainButton.setEnabled(False)
        self.thread_pool.shutdown(wait=False, cancel_futures=True)
        self.mainButton.setText("删除")
        self.mainButton.clicked.disconnect(self.stop)
        self.mainButton.clicked.connect(self.delete)
        self.setTitle(f"{self.data["sName"]} 已停止抢课")
        self.mainButton.setEnabled(True)

    def delete(self):
        self.parent().removeCard(self.id)
        self.parent().parent().parent().parent().setNum()

    def updateText(self):
        self.contentLabel1.setText("当前状态：\n" + "\n".join(sorted([f"{k} × {v}" for k, v in self.result.items()])))
        self.update()

    def setTaskText(self, msg):
        try:
            self.result.setdefault(msg, 0)
            self.result[msg] += 1
        except:
            traceback.print_exc()

    def joinCourse(self):
        self.thread_pool.submit(self.check)
        self.club_data = school.getClubData(self.data["id"])
        while True:
            self.thread_pool.submit(self._joinCourse)
            time.sleep(self.delay)

    def _joinCourse(self):
        result = school.joinClub(self.data["id"], self.club_data["data"]["semesterId"], self.task_id)
        logging.info(f"请求信息：{result}")
        self.setTaskText("请求信息：" + result["msg"])
        if result["msg"] in ["选择课程数量超出，您选择的课程已达到上限！", "资源数量为0", "选课已结束！"]:
            self.stop()

    def check(self):
        while True:
            result = school.getResult(self.data["id"])
            self.setTaskText(f"结果查询：{result}")

            if result == "选课成功":
                self.stop()
                break

            if self.mainButton.text() == "删除":
                result = "退出"
                break
        self.getResultSignal.emit(result)

    def getResultMessage(self, msg):
        if msg == "选课成功":
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "选课成功", Qt.Orientation.Vertical, True, -1, InfoBarPosition.BOTTOM, self.window().taskPage)
        elif msg == "error":
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "选课失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        elif msg == "退出":
            infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "退出选课", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        else:
            infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "未知状态", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        infoBar.show()

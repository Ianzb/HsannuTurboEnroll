from .widget import *


class TaskPage(zbw.BasicTab):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(FIF.LABEL)
        self.setTitle("任务")
        self.cardGroup = zbw.CardGroup("抢课任务", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def addTask(self, msg, task_id, begin_time: int = None):
        group_id = msg.get("id") + str(time.time())
        card = TaskCard(msg, task_id, group_id, self, begin_time)
        self.cardGroup.addCard(card, group_id, 0)
        card.thread_pool.submit(card.joinClass)
        self.setNum()

    def setNum(self):
        item = self.window().navigationInterface.widget("任务")
        infoBabge = InfoBadge.attension(
            text=self.cardGroup.count(),
            parent=item.parent(),
            target=item,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )


class TaskCard(zbw.SmallInfoCard):
    getResultSignal = pyqtSignal(str, float)

    def __init__(self, data, task_id, group_id, parent, begin_time: int = None):
        super().__init__(parent, True)
        self.data = data
        self.task_id = task_id
        self.group_id = group_id
        self.result = {}
        self.class_data = {}
        self.begin_time = begin_time
        self.user_info = deepcopy(school.getUserInfo)

        self.thread_pool = ThreadPoolExecutor(max_workers=setting.read("threadNumber") + 2)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateText)
        self.timer.start(100)

        self.image.deleteLater()
        self.setFixedHeight(73 * 2)
        self.setTitle(f"{self.user_info.get("realName")} {self.data.get("sName")} 抢课中...")
        self.mainButton.setText("停止")
        self.mainButton.clicked.connect(self.stop)
        self.getResultSignal.connect(self.getResultMessage)

        setting.changeSignal.connect(self.set)

    def set(self, msg):
        if msg == "threadNumber":
            self.thread_pool._max_workers = setting.read("threadNumber") + 2

    def stop(self):
        self.thread_pool.shutdown(wait=False, cancel_futures=True)
        self.mainButton.setText("删除")
        self.mainButton.clicked.disconnect(self.stop)
        self.mainButton.clicked.connect(self.delete)
        self.setTitle(f"{self.user_info.get("realName")} {self.data.get("sName")} 已停止抢课")

    def delete(self):
        self.parent().removeCard(self.group_id)
        self.parent().parent().parent().parent().setNum()

    def updateText(self):
        if self.checkTime():
            self.contentLabel1.setText("当前状态：\n" + "\n".join(sorted([f"{k} × {v}" for k, v in self.result.items()])))
        else:
            self.contentLabel1.setText(f"距离抢课开始还有{int(self.begin_time - time.time())}秒！")
        self.update()

    def setTaskText(self, msg):
        try:
            self.result.setdefault(msg, 0)
            self.result[msg] += 1
        except:
            logging.error(f"设置任务进度文本失败，报错信息：{traceback.format_exc()}！")

    def checkTime(self):
        if not self.begin_time:
            return True
        return bool(time.time() - self.begin_time >= -10)

    def joinClass(self):
        self.thread_pool.submit(self.check)
        self.class_data = school.getClassData(self.data.get("id"))
        user_info = self.user_info
        get_class = deepcopy(school.getClass)
        student_data = deepcopy(school.student_data)
        header = deepcopy(school.header)
        while True:
            if self.checkTime():
                self.thread_pool.submit(self._joinClass, user_info, get_class, student_data, header)
                time.sleep(setting.read("requestDelay"))
            else:
                time.sleep(0.05)

    def _joinClass(self, user_info, get_class, student_data, header):
        result = school.joinClass(self.data.get("id"), self.class_data.get("data", {}).get("semesterId"), self.task_id, user_info, get_class, student_data, header)
        logging.info(f"请求信息：{result}")
        self.setTaskText("请求信息：" + result.get("msg"))
        if result.get("msg") in ["选择课程数量超出，您选择的课程已达到上限！", "资源数量为0", "选课已结束！"]:
            self.stop()

    def check(self):
        user_id = deepcopy(school.getUserInfo.get("userId"))
        header = deepcopy(school.header)
        while True:
            if not self.checkTime():
                time.sleep(0.05)
                continue
            result = school.getResult(self.data.get("id"), user_id, header)
            self.setTaskText(f"结果查询：{result}")
            if result == "选课成功":
                self.stop()
                break
            if self.mainButton.text() == "删除":
                result = "退出"
                break
        self.getResultSignal.emit(result, time.time() - self.begin_time if self.begin_time else 0)

    def getResultMessage(self, msg, time):
        if msg == "选课成功":
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"选课成功{f"，用时{time:.3f}秒" if time != 0 else ""}！", Qt.Orientation.Vertical, True, -1, InfoBarPosition.BOTTOM, self.window().taskPage)
        elif msg == "error":
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "选课失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        elif msg == "退出":
            infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "退出选课！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        else:
            infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "未知状态！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().taskPage)
        infoBar.show()

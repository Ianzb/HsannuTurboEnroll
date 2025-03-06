import time
import traceback

from ..program import *

from zbWidgetLib import *


class TaskPage(BasicTab):
    title = "任务"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(FIF.LABEL)
        self.cardGroup = CardGroup("抢课任务", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def addTask(self, msg, task_id):
        id=msg["id"]+str(time.time())
        card = TaskCard(msg, task_id, self,id)
        self.cardGroup.addCard(card, id)
        card.thread_pool.submit(card.joinCourse)
        self.setNum()
    def setNum(self):
        item = self.window().navigationInterface.widget("任务")
        InfoBadge.attension(
            text=len(self.cardGroup._cards),
            parent=item.parent(),
            target=item,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )


class TaskCard(SmallInfoCard):
    getResultSignal = Signal(str)
    getJoinMessageSignal = Signal(str)

    def __init__(self, data, task_id, parent,id):
        super().__init__(parent)
        self.data = data
        self.task_id = task_id
        self.id=id
        self.result = {}
        self.club_data = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=64)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateText)
        self.timer.start(100)


        self.image.deleteLater()
        self.setFixedHeight(73 * 2)
        self.setTitle(self.data["sName"] + "抢课中")
        self.mainButton.setText("停止")
        self.mainButton.clicked.connect(self.stop)
        self.getResultSignal.connect(self.getResultMessage)
        # self.getJoinMessageSignal.connect(self.getJoinMessage)

    def stop(self):
        self.mainButton.setEnabled(False)
        self.thread_pool.shutdown(wait=False, cancel_futures=True)
        self.mainButton.setText("删除")
        self.mainButton.clicked.disconnect(self.stop)
        self.mainButton.clicked.connect(self.delete)
        self.setTitle(self.data["sName"] + "抢课中")
        self.mainButton.setEnabled(True)

    def delete(self):
        self.parent().removeCard(self.id)
        self.parent().parent().parent().parent().setNum()

    def updateText(self):
        self.contentLabel1.setText("当前状态：\n" + "\n".join([f"{k}x{v}" for k, v in self.result.items()]))
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
            time.sleep(0.005)
            # return

    def _joinCourse(self):
        result = school.joinClub(self.data["id"], self.club_data["data"]["semesterId"], self.task_id)
        logging.info(f"抢课请求返回信息：{result}")
        self.setTaskText("请求信息："+result["msg"])
        # self.getJoinMessageSignal.emit(result["msg"])

    # def getJoinMessage(self, msg):
    #     infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", msg, Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.window().taskPage)
    #     infoBar.show()

    def check(self):
        while True:
            result = school.getResult(self.data["id"])
            if result == "success":
                self.thread_pool.shutdown(wait=False, cancel_futures=True)
                self.setTaskText("结果查询：成功！")
                break
            elif result == "error":
                self.setTaskText("结果查询：失败！")
            elif result == "loading":
                self.setTaskText("结果查询：等待中！")
            if self.mainButton.text() == "删除":
                result = "exit"
                break
        self.getResultSignal.emit(result)

    def getResultMessage(self, msg):
        if msg == "success":
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "选课成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().taskPage)
        elif msg == "error":
            infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "选课失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().taskPage)
        elif msg == "exit":
            infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "退出选课", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().taskPage)
        else:
            infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "未知状态", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().taskPage)
        infoBar.show()

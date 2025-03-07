import subprocess

from zbWidgetLib import *
import os, sys, logging
from concurrent.futures import ThreadPoolExecutor


class Program:
    """
    程序信息
    """
    NAME = "东北师大附中抢课工具"  # 程序名称
    VERSION = "1.0.0"  # 程序版本
    TITLE = f"{NAME} {VERSION}"  # 程序标题
    URL = "https://ianzb.github.io/project/program.html"  # 程序网址
    LICENSE = "GPLv3"  # 程序许可协议
    UPDATE_URL = "http://123pan.ianzb.cn/Code/program/index.json"  # 更新网址
    UPDATE_INSTALLER_URL = "http://123pan.ianzb.cn/Code/program/zbProgram_setup.exe"  # 更新安装包链接
    UNINSTALL_FILE = "unins000.exe"  # 卸载程序名称

    AUTHOR_NAME = "Ianzb"  # 作者名称
    AUTHOR_URL = "https://ianzb.github.io/"  # 作者网址
    GITHUB_URL = "https://github.com/Ianzb/program/"  # Github网址

    MAIN_FILE_PATH = sys.argv[0]  # 程序主文件路径
    MAIN_FILE_NAME = os.path.basename(MAIN_FILE_PATH)  # 当前程序文件名称
    INSTALL_PATH = os.path.dirname(MAIN_FILE_PATH)  # 程序安装路径
    SOURCE_PATH = r"source\img"  # 程序资源文件路径
    PROGRAM_PID = os.getpid()  # 程序pid
    DATA_PATH = os.path.join(zb.USER_PATH, "zb")  # 程序数据路径
    SETTING_FILE_PATH = os.path.join(DATA_PATH, "HsannuTurboEnrollSettings.json")  # 程序设置文件路径
    LOGGING_FILE_PATH = os.path.join(DATA_PATH, "HsannuTurboEnrollLogging.log")  # 程序日志文件路径

    STARTUP_ARGUMENT = sys.argv[1:]  # 程序启动参数
    THREAD_POOL = ThreadPoolExecutor()  # 程序公用线程池

    def __init__(self):
        # 创建数据目录
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)

        # 切换运行路径
        os.chdir(self.INSTALL_PATH)

        # 设置任务栏
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.NAME)

    @property
    def ICON(self) -> str:
        return program.source("program.png")

    @property
    def isStartup(self) -> bool:
        """
        判断程序是否为开机自启动
        @return: bool
        """
        return "startup" in self.STARTUP_ARGUMENT

    @property
    def isExe(self) -> bool:
        """
        判断程序是否为
        @return:
        """
        return ".exe" in self.MAIN_FILE_NAME

    def source(self, name: str) -> str:
        """
        快捷获取程序资源文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return os.path.join(self.SOURCE_PATH, name)

    def cache(self, name: str) -> str:
        """
        快捷获取程序缓存文件路径
        @param name: 文件名
        @return: 文件路径
        """
        return os.path.join(self.DATA_PATH, "cache", name)

    def close(self):
        """
        退出程序
        """
        logging.info("程序已退出！")
        os._exit(0)

    def restart(self):
        """
        重启程序
        """
        subprocess.Popen(self.MAIN_FILE_PATH)
        logging.info("程序正在重启中！")
        os._exit(0)

    def getNewestVersion(self):
        """
        获取程序最新版本
        @return: 程序最新版本
        """
        response = zb.getUrl(program.UPDATE_URL, zb.REQUEST_HEADER, (15, 30))
        data = json.loads(response.text)["version"]
        logging.info(f"服务器最新版本：{data}")
        return data


program = Program()

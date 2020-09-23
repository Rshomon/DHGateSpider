import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter


class custom:
    def __init__(self) -> None:
        #第一步：创建一个日志收集器logger
        self.logger = logging.getLogger("autotest")

        #第二步：修改日志的输出级别
        self.logger.setLevel(logging.DEBUG)

        #第三步：设置输出的日志内容格式
        self.fmt = "%(log_color)s%(asctime)s  %(log_color)s%(filename)s  %(log_color)s%(funcName)s [line:%(log_color)s%(lineno)d] %(log_color)s%(levelname)s %(log_color)s%(message)s"
        self.datefmt = '%a, %d %b %Y %H:%M:%S'

        self.formatter = ColoredFormatter(fmt=self.fmt,
                                          datefmt=self.datefmt,
                                          reset=True,
                                          log_colors={
                                              'DEBUG': 'cyan',
                                              'INFO': 'green',
                                              'WARNING': 'yellow',
                                              'ERROR': 'red',
                                              'CRITICAL': 'red,bg_white'
                                          },
                                          secondary_log_colors={},
                                          style='%')

        #设置输出渠道--输出到控制台
        self.hd_1 = logging.StreamHandler()
        #在handler上指定日志内容格式
        self.hd_1.setFormatter(self.formatter)

        #第五步：将headler添加到日志logger上
        self.logger.addHandler(self.hd_1)

if __name__ == "__main__":
    a = custom()
    a.logger.info("aaa")
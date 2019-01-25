import  logging
import  sys

class LogHelper:

    def __init__(self,name='LogHelper', setLevel = logging.DEBUG):


        self.logger = logging.getLogger(name)
        self.formatter = logging.Formatter('%(asctime)s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s')


        #文件日志
        self.file_handler = logging.FileHandler(name +".log")
        self.file_handler.setFormatter(self.formatter)

        #终端日志
        self.consle_handler = logging.StreamHandler(sys.stdout)
        self.consle_handler.setFormatter(self.formatter)

        #日志级别
        self.logger.setLevel(setLevel)

        #添加到日志
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.consle_handler)

    #写日志
    def writeLog(self,info,level = 'debug'):
        if level == "critail":
            self.logger.critical(info)
        elif level == "error":
            self.logger.error(info)

        elif level == "warning":
            self.logger.warning(info)

        elif level == "info":
            self.logger.info(info)

        else:
            self.logger.debug(info)


    #删除日志
    def removeLog(self):
        self.logger.removeFilter(self.file_handler)
        self.logger.removeFilter(self.consle_handler)


logger = LogHelper()

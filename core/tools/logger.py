
from datetime import datetime

class Logger:

    LOG_TYPE_DEBUG=3
    LOG_TYPE_INFO=2
    LOG_TYPE_WARNING=1
    LOG_TYPE_ERROR=0

    LOG_LEVEL = 3
    SHOW_CONSOLE = False
    FILENAME = "logs/log_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    def write(log, type):
        if type <= Logger.LOG_LEVEL:
            formatedLog = Logger.getLogFormated(log, type)
            with open(Logger.getFileName(type), "a+") as filout:
                filout.write(formatedLog + "\n")
            if Logger.SHOW_CONSOLE:
                print(formatedLog)
        return None

    def getLogFormated(log, type):
        suffixe = ""
        if type == Logger.LOG_TYPE_DEBUG:
            suffixe = "[DEBUG]"
        if type == Logger.LOG_TYPE_INFO:
            suffixe = "[INFO]"
        if type == Logger.LOG_TYPE_WARNING:
            suffixe = "[WARNING]"
        if type == Logger.LOG_TYPE_ERROR:
            suffixe = "[ERROR]"
        return "[" + str(datetime.now()) + "]" + suffixe + f"\t{log}"

    def getFileName(type):
        return Logger.FILENAME
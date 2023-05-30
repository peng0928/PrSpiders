from loguru import logger as loguer


class Log():

    def loggering(self, file_log, level="info"):


        return loguer

class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass
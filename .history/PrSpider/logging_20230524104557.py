from loguru import logger as loguer


class Log():

    def loggering(self, file_log, level="info"):
        loguer.level("TRACE", color="<blue>")
        loguer.level("DEBUG", color="<green>")
        loguer.level("INFO", color="<cyan>")
        loguer.level("SUCCESS", color="<light-green>")
        loguer.level("WARNING", color="<yellow>")
        loguer.level("ERROR", color="<red>")
        loguer.level("CRITICAL", color="<red>")
        loguer.level("Print", no=30, color="<green>")

        return loguer

class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass
from loguru import logger as loguer


class Log():
    def __init__(self) -> None:
        self.level_dict = {
            "warn": 'WARNING',
            "info": 'INFO',
            "debug": 'DEBUG',
            "error": 'ERROR',
            "critical": 'CRITICAL',
        }
        self.level_stdout = {
            "critical": ['Print', 'CRITICAL'],
            "error": ['Print', 'ERROR', 'CRITICAL', ],
            "warn": ['Print', 'WARNING', 'ERROR', 'CRITICAL'],
            "info": ['Print', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            "debug": ['Print', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        }
        loguer.level("TRACE", color="<blue>")
        loguer.level("DEBUG", color="<green>")
        loguer.level("INFO", color="<cyan>")
        loguer.level("SUCCESS", color="<light-green>")
        loguer.level("WARNING", color="<yellow>")
        loguer.level("ERROR", color="<red>")
        loguer.level("CRITICAL", color="<red>")
        loguer.level("Print", no=30, color="<green>")

    def loggering(self, file_log, level="info"):
        levels = self.level_dict.get(level.lower())
        slevel = self.level_stdout.get(level.lower())

        return loguer

class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass
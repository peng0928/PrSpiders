import sys, os, re
from loguru import logger as loguer



class Log():
    def __init__(self, log_stdout=True, log_level='INFO', log_file=False) -> None:
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
        self.log_stdout, self.log_level, self.log_file = log_stdout, log_level, log_file
        loguer.level("TRACE", color="<blue>")
        loguer.level("DEBUG", color="<green>")
        loguer.level("INFO", color="<cyan>")
        loguer.level("SUCCESS", color="<light-green>")
        loguer.level("WARNING", color="<yellow>")
        loguer.level("ERROR", color="<red>")
        loguer.level("CRITICAL", color="<red>")
        loguer.level("Print", no=30, color="<green>")


    def loggering(self):
        levels = self.level_dict.get(self.log_level.lower())
        slevel = self.level_stdout.get(self.log_level.lower())
        stdout_handler = {
            "sink": sys.stdout,
            "filter": lambda record: record["level"].name in slevel,
            "format": "<light-green><b>{time:YYYY-MM-DD HH:mm:ss.SSS}</b></light-green> | <b><level>{level: ^8}</level></b> | <b>{message}</b>"
        }
        loguer.configure(handlers=[stdout_handler])
        if self.log_stdout:
            sys.stdout = InterceptHandler()
        if self.log_file:
            file_log = os.path.basename(__file__) if self.log_file is True else self.log_file
            file_log = (
                re.sub("\..*", ".log", file_log)
                if "." in file_log
                else file_log + ".log"
            )
            filename = f"./{file_log}"
            loguer.add(filename, level=levels)
        return loguer


class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass

import hashlib, orjson
from .log import loguercor

log_format = "<b><green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green></b><b><level> [{level: ^2}]: </level></b><b><i><color>{message}</color></i></b>"
Start = '{"Thread_Num": "%s", "Retry": "%s", "Pid": "%s", "Download_Delay": "%s", "Download_Num": "%s", "LOG_LEVEL": "%s"}'


def close_sign(data):
    column_widths = max(len(header) for header, _ in data) + 7
    m = f"\n"
    m += f"| {'Key':<{column_widths}} | {'Value':<{column_widths}} |\n"
    m += "| " + "-" * (column_widths + 1) + "| " + "-" * (column_widths + 1) + "|\n"
    for header, value in data:
        m += f"| `{header}`{' ' * (column_widths - len(header) - 2)} | `{value}`{' ' * (column_widths - len(str(value)) - 2)} |\n"
    return m


def dict_sort(item, reverse=True):
    return dict(sorted(item.items(), key=lambda x: x[1], reverse=reverse))


def dict_fmomat():
    pass


def log_start(self):
    if self.custom_settings:
        for key, value in self.custom_settings.items():
            key = key.lower()
            if key in filter_settions:
                continue
            if isinstance(value, str):
                if value.isdigit():
                    value = int(value)
            setattr(settions, key, value)
    assert self.thread_num > 0, 'thread_num must be > 0'
    self.init += 1
    if self.init <= 1:
        Log(self).loggering()
    self.loging = loging(loguercor)
    self.executor = ThreadPoolExecutor(self.thread_num)
    self.Request = requests.session() if self.session else requests
    self.pipelines = dict_sort(self.pipelines)
    loguercor.log('Start', Start % (self.thread_num, self.retry, self.pid, self.download_delay, self.download_num,
                                    self.log_level.upper()))
    pipelines_msg = f"{str(self.pipelines)}".replace(',', ',\n')
    loguercor.log('Pipelines', f'<red>Used Pipelines:\n{pipelines_msg}</red>')


def sha_hash(item: dict):
    string = orjson.dumps(item).decode()
    hex_dig = hashlib.sha256(str(string).encode()).hexdigest()
    return hex_dig

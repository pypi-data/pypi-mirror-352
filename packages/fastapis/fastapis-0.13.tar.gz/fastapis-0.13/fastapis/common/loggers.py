import json
import logging
import logging.config


class CustomFormatter(logging.Formatter):
    red = "\x1b[31m"
    red_dimmed = "\x1b[2;31m"
    red_bold = "\x1b[1;31m"

    yellow = "\x1b[32m"
    yellow_dimmed = "\x1b[2;32m"
    yellow_bold = "\x1b[1;32m"

    blue = "\x1b[34m"
    blue_dimmed = "\x1b[2;34m"
    blue_bold = "\x1b[1;34m"

    magenta = "\x1b[35m"
    magenta_dimmed = "\x1b[2;35m"
    magenta_bold = "\x1b[1;35m"

    cyan = "\x1b[36m"
    cyan_dimmed = "\x1b[2;36m"
    cyan_bold = "\x1b[1;36m"

    grey = "\x1b[37m"
    grey_dimmed = "\x1b[2;37m"
    grey_bold = "\x1b[1:37m"

    default = "\x1b[39m"
    default_dimmed = "\x1b[2;39m"
    default_bold = "\x1b[1;39m"

    reset = "\x1b[0m"

    format_level = "[%(levelname)s]"
    format_date = "%(asctime)s"
    format_name = "%(name)s"
    format_message = "%(asctime)s %(message)s"

    trace_template = (
        f"{grey_bold}[%(levelname)s]{reset} %(asctime)s "
        f":{grey_dimmed}%(name)s{reset}: {grey_dimmed}%(message)s{reset}"
    )

    debug_template = (
        f"{grey_bold}[%(levelname)s]{reset} %(asctime)s "
        f": {grey_dimmed}%(name)s{reset}: {grey_dimmed}%(message)s{reset}"
    )

    info_template = (
        f"{cyan_bold}[%(levelname)s]{reset} %(asctime)s "
        f":{grey_dimmed}%(name)s{reset}: {default_dimmed}%(message)s{reset}"
    )

    warning_template = (
        f"{yellow_bold}[%(levelname)s]{reset} %(asctime)s "
        f":{grey_dimmed}%(name)s{reset}: {yellow_dimmed}%(message)s{reset}"
    )

    error_template = (
        f"{magenta_bold}[%(levelname)s]{reset} %(asctime)s "
        f":{grey_dimmed}%(name)s{reset}: {magenta_dimmed}%(message)s{reset}"
    )

    critical_template = (
        f"{red_bold}[%(levelname)s]{reset} %(asctime)s "
        f":{grey_dimmed}%(name)s{reset}: {red_dimmed}%(message)s{reset}"
    )

    FORMATS = {
        5: trace_template,
        logging.DEBUG: debug_template,
        logging.INFO: info_template,
        logging.WARNING: warning_template,
        logging.ERROR: error_template,
        logging.CRITICAL: magenta_bold + format_level + reset + format_message,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# logger = logging.getLogger("payboy")
# sh = logging.StreamHandler()
# sh.setFormatter(CustomFormatter())
# logger.setLevel(10)
# logger.addHandler(sh)


class CustomJSONFormatter(logging.Formatter):
    def __init__(self, fmt):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        logging.Formatter.format(self, record)
        return json.dumps(self.get_log(record), indent=2)

    def get_log(self, record):
        d = {
            "time": record.asctime,
            "process_name": record.processName,
            "process_id": record.process,
            "thread_name": record.threadName,
            "thread_id": record.thread,
            "level": record.levelname,
            "logger_name": record.name,
            "pathname": record.pathname,
            "line": record.lineno,
            "message": record.message,
        }

        if hasattr(record, "extra_info"):
            d["req"] = record.extra_info["req"]
            d["res"] = record.extra_info["res"]
        return d

import logging
import logging.handlers
from datetime import datetime

ERROR = "ERROR"
INFO = "INFO"
WARNING = "WARNING"

class Logger:
    def __init__(self, base_path, log_name, max_bytes=10485760, backup_count=1):
        log_file = base_path + '/{0}.log'.format(log_name)
        self.logger = logging.getLogger('{0}_logger'.format(log_name))
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(log_file,
                                                       maxBytes=max_bytes,
                                                       backupCount=backup_count)
        self.logger.addHandler(handler)

    def print_log_to_file(self, message, print_to_file = True, type = INFO, print_out = True):
        self.print_log(message, type) if print_out else ''

        if print_to_file:
            self.logger.error("{0} [{1}] {2}".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type, message))

    def print_log(self, message, type=INFO):
        print "{0} [{1}] {2}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               type, message)
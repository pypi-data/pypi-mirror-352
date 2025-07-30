# redstream/utils/logging_helpers.py

import inspect
import logging
import os

class LoggerWithCaller:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _log(self, level, msg, *args, **kwargs):
        # Пробегаемся по стеку вызовов
        for frame_info in inspect.stack()[2:]:
            filename = frame_info.filename
            if "redstream" not in filename:
                location = f"{os.path.basename(filename)}:{frame_info.lineno}"
                break
        else:
            location = "unknown"

        self.logger.log(level, f"[{location}] {msg}", *args, **kwargs)

    def debug(self, msg, *args, **kwargs): self._log(logging.DEBUG, msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs): self._log(logging.INFO, msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs): self._log(logging.WARNING, msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs): self._log(logging.ERROR, msg, *args, **kwargs)
    def exception(self, msg, *args, **kwargs): self._log(logging.ERROR, msg, *args, exc_info=True, **kwargs)

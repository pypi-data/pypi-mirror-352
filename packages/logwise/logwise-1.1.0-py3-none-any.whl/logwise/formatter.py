import logging
import os
import shutil
import textwrap

BOX_LEVEL = 5
logging.addLevelName(BOX_LEVEL, "BOX")
logging.addLevelName(logging.WARNING, "WARN")


class CustomLogger:
    bold_cyan = "\x1b[36;1m"
    bold_green = "\x1b[1;32m"
    bold_yellow = "\x1b[1;33m"
    bold_red = "\x1b[31;1m"
    bold_white = "\x1b[1;39m"
    reset = "\x1b[0m"

    base_format = "%(asctime)s.%(msecs)03d [%(levelname)-5s] %(message)s (%(filename)s:%(lineno)d)"
    box_format = "%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d)\n%(message)s"

    class Formatter(logging.Formatter):
        def __init__(self, outer, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.outer = outer
            self._box_formatter = logging.Formatter(outer.box_format, datefmt='%Y-%m-%d %H:%M:%S')

        def format(self, record):
            record.filename = os.path.splitext(record.filename)[0]

            if record.levelno == BOX_LEVEL:
                return self.outer.bold_white + self._box_formatter.format(record) + self.outer.reset

            if record.levelno == logging.DEBUG:
                fmt = self.outer.bold_cyan + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.INFO:
                fmt = self.outer.bold_green + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.WARNING:
                fmt = self.outer.bold_yellow + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.ERROR:
                fmt = self.outer.bold_red + self.outer.base_format + self.outer.reset
            else:
                fmt = self.outer.bold_white + self.outer.base_format + self.outer.reset

            self._style._fmt = fmt
            return super().format(record)

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(BOX_LEVEL)

        handler = logging.StreamHandler()
        handler.setLevel(BOX_LEVEL)
        handler.setFormatter(self.Formatter(self, datefmt='%Y-%m-%d %H:%M:%S'))

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.logger.propagate = False

    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)

    def box(self, msg: str):
        term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
        box_width = max(40, min(term_width - 4, 120))
        wrapped_lines = textwrap.wrap(msg, width=box_width - 4)
        top = '╭' + '─' * (box_width - 2) + '╮'
        bottom = '╰' + '─' * (box_width - 2) + '╯'
        middle = [f'│ {line.ljust(box_width - 4)} │' for line in wrapped_lines]
        full_box = '\n'.join([top] + middle + [bottom])
        full_box = self.bold_white + full_box + self.reset
        self.logger.log(BOX_LEVEL, full_box, stacklevel=2)

    def get_logger(self): return self.logger
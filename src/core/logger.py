import logging
import sys

import loguru

DEFAULT_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    " | <level>{level: <8}</level> "
    " | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

JSON_LOG_FORMAT = "{message} | {extra}"


class InterceptHandler(logging.Handler):
    """Перехватывает логи стандартного лоигрования.

    Решение из официальной документации:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1
        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(config: dict) -> None:
    """Настройка логирования.

    Очистка стандартных настроек для каждой библиотеки(при их наличии).
    Определение собственного обработчика.
    """
    loguru.logger.remove()
    logging.root.handlers = []
    logging.root.setLevel(config["level"])
    for name in logging.root.manager.loggerDict.keys():  # noqa: SIM118
        if logging.getLogger(name).hasHandlers():
            logging.getLogger(name).handlers.clear()
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
    loguru.logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "colorize": True,
                "format": JSON_LOG_FORMAT if config["serializer"] is True else DEFAULT_LOG_FORMAT,
                "serialize": config["serializer"],
                "level": config["level"],
            }
        ],
    )

import logging
import os

LOG_LEVEL = 'INFO'
LOG_FOLDER = '../logs'

class AppLogger:
    """Wrapper for logging module."""

    def __init__(self) -> None:
        """App logger constructor."""
        self.__custom_loggers = {}
        
        self.__logger = logging.getLogger()
        self.__logger.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.__logger.addHandler(console_handler)

        # File handler
        log_file_path = os.path.join(LOG_FOLDER, "app.log")
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)

    def add_custom_file_logger(self, log_file_path: str, log_level: str) -> logging.Logger:
        # create directory if it doesn't exist
        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))
        
        c_logger = logging.getLogger(log_file_path)
        c_logger.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        c_logger.addHandler(file_handler)

        self.__custom_loggers[c_logger] = c_logger

        return c_logger
    
    def remove_custom_logger(self, c_logger: logging.Logger) -> None:
        if c_logger in self.__custom_loggers:
            del self.__custom_loggers[c_logger]

    def debug(self, msg: str) -> None:
        self.__logger.debug(msg)
        self.__forward_to_custom_loggers(msg, "debug")

    def info(self, msg: str) -> None:
        self.__logger.info(msg)
        self.__forward_to_custom_loggers(msg, "info")

    def warning(self, msg: str) -> None:
        self.__logger.warning(msg)
        self.__forward_to_custom_loggers(msg, "warning")

    def error(self, msg: str) -> None:
        self.__logger.error(msg)
        self.__forward_to_custom_loggers(msg, "error")

    def exception(self, msg: str, e: Exception) -> None:
        self.__logger.exception(msg)
        self.__forward_to_custom_loggers(msg, "exception")

    def __forward_to_custom_loggers(self, msg: str, level: str) -> None:        
        for c_logger in self.__custom_loggers.values():
            getattr(c_logger, level)(msg)


logger = AppLogger()

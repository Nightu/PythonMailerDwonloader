# %%
from logging import getLogger, Formatter, INFO, StreamHandler, Logger, DEBUG
from os import environ

class LoggerConfig:
    """
    Configure and return logger object.
    """

    @classmethod
    def logger(cls, cls_name) -> Logger:
        """
        :param cls_name: Class name to be further used in logger output
        :return: logger object
        """
        logger = getLogger(cls_name)
        logger.setLevel(environ.get('logger_lvl', INFO))
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = StreamHandler()
        ch.setFormatter(formatter)
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(ch)

        return logger

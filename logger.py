import logging
import colorlog


def setup_logger(name="samokat_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = colorlog.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s - %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

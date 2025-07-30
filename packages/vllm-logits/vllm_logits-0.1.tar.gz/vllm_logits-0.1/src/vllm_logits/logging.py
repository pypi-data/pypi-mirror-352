import logging


def init(format: str = None, datefmt: str = None, level: int = None) -> None:
    if format is None:
        format = "[%(asctime)s %(levelname)s %(name)s] %(message)s"
    if datefmt is None:
        datefmt = "%m/%d %H:%M:%S"
    if level is None:
        level = logging.INFO

    # Set logging format
    logging.basicConfig(
        format=format,
        datefmt=datefmt,
        level=level,
    )

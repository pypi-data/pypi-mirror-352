import logging
from pathlib import Path


def setup_logger(log_file: Path = None):
    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(str(log_file), encoding='utf-8'))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

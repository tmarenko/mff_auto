import logging
import time
import sys
from os.path import exists

LOGS_FOLDER = "logs"

root = logging.getLogger()
root.setLevel(logging.DEBUG)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def get_logger(name) -> logging.Logger:
    name = name.split(".")[-1]
    return logging.getLogger(name)


def create_file_handler(file_name=None):
    if not exists(LOGS_FOLDER):
        return None
    file_name = file_name if file_name else f"{LOGS_FOLDER}/{time.strftime('%Y-%m-%d--%H-%M-%S')}.log"
    fh = logging.FileHandler(file_name, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root.addHandler(fh)
    return fh

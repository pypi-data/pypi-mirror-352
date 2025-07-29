import logging
from logging.handlers import RotatingFileHandler
import platform
import os
import sys
import getpass


def setup_logging(reMoveOldHandler=True, filename='spider_tg.log'):
    """
    reMoveOldHandler: 替换根日志记录器的所有现有处理器
    """
    dir_path = os.path.expanduser("~")
    if not os.path.isdir(os.path.join(dir_path, 'logfile')):
        os.makedirs(os.path.join(dir_path, 'logfile'))

    log_file = os.path.join(dir_path, 'logfile', filename)
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=3*1024*1024,  # 3MB
        backupCount=10,
        encoding='utf-8'  # 明确指定编码（避免Windows乱码）
    )
    stream_handler = logging.StreamHandler()  # 终端输出Handler
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)  # 终端使用相同格式
    file_handler.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)

    # 获取根日志记录器并添加Handler
    logger = logging.getLogger()
    if reMoveOldHandler:
        # 移除根日志记录器的所有现有处理器
        for handler in logger.handlers[:]:  # 使用[:]来创建handlers列表的一个副本，因为我们在迭代时修改列表
            logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)  # 设置根日志级别
    return logger


if __name__ == '__main__':
    pass

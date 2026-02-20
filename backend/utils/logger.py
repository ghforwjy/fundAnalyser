"""
日志模块
提供统一的日志记录功能
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

# 创建logs目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(module)-20s | %(funcName)-20s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    获取配置好的logger实例
    
    Args:
        name: logger名称，通常使用__name__
        level: 日志级别，默认为DEBUG
    
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件handler
    log_file = LOG_DIR / f"fund_analyzer_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

# 根logger配置
def setup_root_logger():
    """配置根logger"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
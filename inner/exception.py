'''
Author: Mr.Car
Date: 2024-06-21 13:30:13
'''
import logging
import fiona as fiona
from functools import wraps
from rich.console import Console
console = Console()

# 配置日志记录：设置日志级别、格式和输出文件
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='error.log',  # 存储日志的文件名
                    filemode='a')  # 模式，'w'表示写入模式，会覆盖原有日志

def catch_key_error(func):
    '''
    捕获 KeyError, 一般发生在各种各样的 pandas 操作中
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            logging.error(f"KeyError occurred: {e}", exc_info=True)
            missing_key = e.args[0]
            console.print(f"\n [red bold underline][ERROR]: 快去检查一下，“输入文件” 或 “配置文件” 中的字段：{missing_key} \n[/red bold underline]")
        return 'Failed!'
    return wrapper

def catch_file_not_found_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, fiona.errors.DriverError) as e:
            logging.error(f"FileNotFoundError: {e}", exc_info=True)
            file_pth = e.args[0]
            console.print(f"\n [red bold underline][ERROR]: 快去检查一下 “输入文件” 的路径是否正确！：{file_pth} \n[/red bold underline]")
        return 'Failed!'
    return wrapper

def add_attention(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        console.print(f"\n [green underline][SUCCESS]: 成功了，如果结果不对，记得检查一下配置文件和输入文件的版本！ \n[/green underline]")
        return ""
    return wrapper


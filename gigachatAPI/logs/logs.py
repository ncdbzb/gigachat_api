import logging
import sys

logger_info = logging.getLogger('logger_info')
logger_info.setLevel(logging.DEBUG)

logger_context = logging.getLogger('logger_context')
logger_context.setLevel(logging.DEBUG)

console_handler_info = logging.StreamHandler()
console_handler_info.setLevel(logging.DEBUG)

file_handler_info = logging.FileHandler('gigachatAPI/data/info_logs.txt', 'a+', encoding='utf-8')
file_handler_info.setLevel(logging.INFO)

file_handler_context = logging.FileHandler('gigachatAPI/data/info_logs.txt', 'a+', encoding='utf-8')
file_handler_context.setLevel(logging.DEBUG)

formatter_info = logging.Formatter('%(levelname)s: %(message)s')
console_handler_info.setFormatter(formatter_info)

logger_info.addHandler(console_handler_info)
logger_info.addHandler(file_handler_info)

logger_context.addHandler(file_handler_context)

if 'pytest' in sys.argv[0]:
    logger_info.removeHandler(console_handler_info)
    logger_context.removeHandler(file_handler_context)
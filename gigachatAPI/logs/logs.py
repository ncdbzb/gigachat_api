import logging

logger_info = logging.getLogger('logger_info')
logger_info.setLevel(logging.DEBUG)

console_handler_info = logging.StreamHandler()
console_handler_info.setLevel(logging.DEBUG)

file_handler_info = logging.FileHandler('gigachatAPI/data/info_logs.txt', 'a+', encoding='utf-8')
file_handler_info.setLevel(logging.INFO)

formatter_info = logging.Formatter('%(levelname)s: %(message)s')
console_handler_info.setFormatter(formatter_info)

logger_info.addHandler(console_handler_info)
logger_info.addHandler(file_handler_info)
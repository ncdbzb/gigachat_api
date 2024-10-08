import logging
import sys

logger_info = logging.getLogger('logger_info')
logger_info.setLevel(logging.DEBUG)

error_test_logger = logging.getLogger('error_test_logger')
error_test_logger.setLevel(logging.DEBUG)

upload_doc_info = logging.getLogger('upload_doc_info')
upload_doc_info.setLevel(logging.DEBUG)

logger_context = logging.getLogger('logger_context')
logger_context.setLevel(logging.DEBUG)

console_handler_info = logging.StreamHandler()
console_handler_info.setLevel(logging.DEBUG)

error_test_console_handler = logging.StreamHandler()
error_test_console_handler.setLevel(logging.WARNING)

file_handler_info = logging.FileHandler('gigachatAPI/data/info_logs.txt', 'a+', encoding='utf-8')
file_handler_info.setLevel(logging.INFO)

error_test_file_handler = logging.FileHandler('gigachatAPI/data/error_test_logs.txt', 'a+', encoding='utf-8')
error_test_file_handler.setLevel(logging.INFO)

file_handler_context = logging.FileHandler('gigachatAPI/data/info_logs.txt', 'a+', encoding='utf-8')
file_handler_context.setLevel(logging.DEBUG)

formatter_info = logging.Formatter('%(levelname)s: %(message)s')
console_handler_info.setFormatter(formatter_info)
error_test_console_handler.setFormatter(formatter_info)

logger_info.addHandler(console_handler_info)
logger_info.addHandler(file_handler_info)

logger_context.addHandler(file_handler_context)

upload_doc_info.addHandler(console_handler_info)

error_test_logger.addHandler(error_test_file_handler)
error_test_logger.addHandler(error_test_console_handler)

if 'pytest' in sys.argv[0]:
    logger_info.removeHandler(console_handler_info)
    logger_context.removeHandler(file_handler_context)
    # upload_doc_info.removeHandler(console_handler_info)
    error_test_logger.removeHandler(error_test_console_handler)
    error_test_logger.removeHandler(error_test_file_handler)

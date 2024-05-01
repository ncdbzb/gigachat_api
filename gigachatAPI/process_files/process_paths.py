import os

from gigachatAPI.utils.help_methods import extract_zip


async def process_and_take_path(filename: str, file_path: str) -> str:
    """
    Если получен файл с расширением zip, предполагается, что это техническая документация, содержащая файлы .dita. Этот
    файл распаковывается и возвращается новый путь. Если расширение отличается от zip, этап распаковки пропускается.

    :param filename: Имя файла
    :param file_path: Путь к файлу
    :return: Новый путь
    """
    if filename.split('.')[-1] == 'zip':
        file_name_without_extension = '.'.join(filename.split('.')[:-1])
        unpack_path = f'gigachatAPI/data/{file_name_without_extension}'

        await extract_zip(file_path, unpack_path)

        os.remove(file_path)
        file_path = unpack_path
        print(f'unpacked {filename}')
    else:
        file_path = f'gigachatAPI/data/{filename}'
    return file_path

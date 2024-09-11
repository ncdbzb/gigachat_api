import os

from gigachatAPI.utils.help_methods import extract_zip


async def process_and_take_path(doc_name: str, extension: str, file_path: str) -> str:
    """
    Если получен файл с расширением zip, предполагается, что это техническая документация, содержащая файлы .dita. Этот
    файл распаковывается и возвращается новый путь. Если расширение отличается от zip, этап распаковки пропускается.

    :param doc_name: Имя файла
    :param extension: Расширение файла
    :param file_path: Путь к файлу
    :return: Новый путь
    """
    if extension == 'zip':
        unpack_path = f'gigachatAPI/data/initial_docs/{doc_name}'

        await extract_zip(file_path, unpack_path)

        os.remove(file_path)
        file_path = unpack_path
        print(f'unpacked {doc_name}.{extension}')

    return file_path


async def get_partial_path(full_path: str, filename: str) -> str:
    """
    Обрезает путь, оставляя только файлы из архива технической документации
    :param full_path: Полный путь
    :param filename: Имя файла
    :return: Обрезанный путь
    """
    start_index = full_path.find(filename)

    if start_index == -1:
        raise ValueError(f'No such filename: {filename} in data directory')

    start_index += len(filename)

    next_separator_index = full_path.find('/', start_index)
    if next_separator_index == -1:
        next_separator_index = full_path.find('\\', start_index)
        if next_separator_index == -1:
            raise ValueError(f'No such filename: {filename} in data directory')

    partial_path = full_path[next_separator_index + 1:]
    return partial_path
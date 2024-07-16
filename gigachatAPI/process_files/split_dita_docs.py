import re
import asyncio
import fnmatch
import os
import xml.etree.ElementTree as Et

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from gigachatAPI.process_files.split_long_elements import split_long_elements
from gigachatAPI.utils.help_methods import get_doc_length


async def get_dita_docs(
    dita_path: str,
    chunk_size: int = 0,
    min_doc_length: int = 0,
    max_doc_length: int = 0,
    with_xml_paths: bool = False,
    without_large_chunks: bool = False
) -> list[Document] | list[tuple[str, str]] | None:

    async def get_dita_paths(directory_path: str) -> dict[str | bytes, int]:
        dit = {}
        for root, dirs, files in os.walk(directory_path):
            for file in fnmatch.filter(files, '*.dita'):
                file_path = os.path.join(root, file)
                dit[file_path] = await get_doc_length(file_path)
        return dit

    dita_dict = await get_dita_paths(dita_path)

    if not dita_dict:
        return

    path_list_larger = [i for i, j in dita_dict.items() if j > min_doc_length]

    if chunk_size:
        # Парсим текст из каждого .dita файла и собираем в одну большую строку
        very_long_string = ''.join(await asyncio.gather(*(extract_text_from_xml(path, with_xml_paths)
                                                          for path in path_list_larger)))

        # Создаем из строки список, используя перенос строки, как разделитесь, удаляем пустые элементы и лишнии пробелы
        very_long_list = list(map(lambda x: ' '.join(x.split()), filter(None, very_long_string.split('\n'))))

        # Возвращаем обратно строку с переносами строк в нужных местах
        very_long_string = '\n '.join(very_long_list)

        document = [Document(page_content=very_long_string)]
        docs = (CharacterTextSplitter(separator='\n', chunk_size=chunk_size, chunk_overlap=0)
                .split_documents(document))

        if without_large_chunks:
            error_margin = int(chunk_size * 0.1)
            error_docs = []
            for doc in docs:
                if len(doc.page_content) - error_margin > chunk_size:
                    error_docs.append(doc)
            if error_docs:
                for error_doc in error_docs:
                    docs.remove(error_doc)
                error_split_docs = (CharacterTextSplitter(separator=' ', chunk_size=chunk_size, chunk_overlap=0)
                                    .split_documents(error_docs))
                docs += error_split_docs

    elif with_xml_paths:
        list_with_paths: list[tuple[str, str]] = list(await asyncio.gather(*(extract_text_from_xml(path, with_xml_paths)
                                                                             for path in path_list_larger)))
    else:
        result_list = await asyncio.gather(*(extract_text_from_xml(path, with_xml_paths) for path in path_list_larger))

        docs = [
            Document(
                page_content=split,
            )
            for split in result_list
        ]

    if max_doc_length:
        max_part_doc_len = max(len(i.page_content) for i in docs)
        if max_part_doc_len > max_doc_length:
            docs = await split_long_elements(docs, max_doc_length)
    if with_xml_paths:
        return list_with_paths
    return docs


async def extract_text_from_xml(xml_file_path: str, with_xml_paths: bool) -> str | tuple[str, str]:
    tree = Et.parse(xml_file_path)
    root = tree.getroot()

    def get_text(element) -> str:
        extracted_text = element.text if element.text else ''
        for child in element:
            extracted_text += get_text(child)
            if child.tail:
                extracted_text += child.tail
        return extracted_text

    text = get_text(root)

    # Удаляем повторяющиеся символы переноса строки
    cleaned_text = re.sub(r'\n\s*\n', '\n', text)
    
    if with_xml_paths:
        return xml_file_path, cleaned_text
    else:
        return cleaned_text
    
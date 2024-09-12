import os
from gigachatAPI.process_files.split_dita_docs import get_dita_docs
from gigachatAPI.process_files.process_paths import get_partial_path
from gigachatAPI.utils.path_to_doc.tf_idf_search import tf_idf_search


async def get_path_to_doc(source_documents: list, filename: str, answer: str) -> str:
    docs_with_paths = await get_dita_docs(os.path.join('gigachatAPI', 'data', 'initial_docs', filename), with_xml_paths=True)

    most_relevant_source_document = (await tf_idf_search(source_documents, answer))[1]

    file_id = (await tf_idf_search([i[1] for i in docs_with_paths], most_relevant_source_document))[0]

    most_relevant_dita_file_path = await get_partial_path(docs_with_paths[file_id - 1][0], filename)

    return most_relevant_dita_file_path
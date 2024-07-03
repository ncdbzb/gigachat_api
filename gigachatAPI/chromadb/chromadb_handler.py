from typing import Any
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from gigachatAPI.config_data.config import load_config, Config


async def initialize_chroma(split_docs: list[Document], filename: str) -> None:
    if filename == 'test_chroma':
        raise ValueError(f'Name \"{filename}\" is unavailable')
    persist_directory = f"gigachatAPI/data/chroma/{filename}"
    config: Config = load_config()
    embeddings = GigaChatEmbeddings(credentials=config.GIGA_CREDENTIALS,
                                    verify_ssl_certs=False)
    await Chroma.afrom_documents(documents=split_docs,
                                 embedding=embeddings,
                                 persist_directory=persist_directory)
    print(f'chroma initialized at {persist_directory}\n')

    return


async def get_chroma(filename: str) -> Any:
    persist_directory = f"gigachatAPI/data/chroma/{filename}"
    config: Config = load_config()
    embeddings = GigaChatEmbeddings(credentials=config.GIGA_CREDENTIALS,
                                    verify_ssl_certs=False)
    vectordb = Chroma(persist_directory=persist_directory,
                      embedding_function=embeddings)
    return vectordb

import time
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from gigachatAPI.config_data.config import load_config, Config
from gigachat.exceptions import ResponseError
from gigachatAPI.process_files.get_result_docs_list import CHUNK_SIZE
from gigachatAPI.logs.logs import upload_doc_info


class VectordbManager:
    def __init__(self):
        self.config: Config = load_config()
        # self.client = chromadb.PersistentClient(path=self.config.PERSIST_DIRECTORY)
        self.client = chromadb.HttpClient(host="chromadb", port=8800,
                          settings = Settings(
                              is_persistent=True,
                              persist_directory=self.config.PERSIST_DIRECTORY,
                              chroma_client_auth_provider=self.config.CHROMA_CLIENT_AUTH_PROVIDER,
                              chroma_client_auth_credentials=self.config.CHROMA_SERVER_AUTHN_CREDENTIALS,
                          )
                      )
        self.embeddings = GigaChatEmbeddings(credentials=self.config.GIGA_CREDENTIALS,
                                             verify_ssl_certs=False)

    def create_collection(self, collection_name: str, split_docs: list[Document], use_cycle: bool) -> None:
        if collection_name in self.get_list_collections() or collection_name == 'chroma':
            raise ValueError('Collection with this name is already exists')
        try:
            Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                collection_name=collection_name,
                client=self.client
            )
            upload_doc_info.debug(f'created chroma collection in {self.config.PERSIST_DIRECTORY} with name {collection_name}')
        except ResponseError:
            upload_doc_info.debug('Ошибка при загрузке!')
            if use_cycle:
                upload_doc_info.debug('Пробуем загрузить в цикле...')
                self._create_collection_cycle(collection_name, split_docs)

    def _create_collection_cycle(self, collection_name: str, split_docs: list[Document]) -> None:

        chunk_size = CHUNK_SIZE

        upload_doc_info.debug(f'Количество чанков загружаемого документа: {len(split_docs)}')
        upload_doc_info.debug(f'Суммарная длина всех чанков: {sum(map(lambda x: len(x.page_content), split_docs))}')

        # Создаем векторую бд только с первым чанком
        Chroma.from_documents(
            documents=[split_docs[0]],
            embedding=self.embeddings,
            collection_name=collection_name,
            client=self.client
        )

        # Получаем экземпляр только что созданной бд
        vectordb = self.get_langchain_chroma(collection_name)

        # Преобразуем list[Document] -> list[txt]
        split_docs = list(map(lambda x: x.page_content, split_docs))

        failed_chunks_list = []
        start_time = time.time()

        # Цикл с перебором всех чанков, кроме первого
        for text_id, text in enumerate(split_docs[1:], start=1):
            try:
                # Пытаемся добавить чанк в бд
                vectordb.add_texts([text])
            except ResponseError:
                upload_doc_info.warning(f'Чанк #{text_id} не прошел. Его длина: {len(text)}')
                # Если ошибка, добавляем чанк в список failed_chunks_list
                failed_chunks_list.append(text)
                continue
            if text_id % 100 == 0:
                upload_doc_info.debug(f'Добавлено {text_id} чанков за {time.time() - start_time} секунд')
        upload_doc_info.debug(f'Добавлено {len(split_docs) - len(failed_chunks_list)}/{len(split_docs)} чанков,'
                              f' {len(failed_chunks_list)} чанков не прошли\n')

        # Преобразуем list[txt] -> list[Document], чтобы воспользоваться сплиттером
        failed_chunks_list = [Document(page_content=split) for split in failed_chunks_list]

        # Заходим в бесконечный цикл
        while True:
            # Выходим из цикла, если failed_chunks_list пустой (Не осталось недобавленных чанков)
            if not failed_chunks_list:
                break
            # Уменьшаем чанк сайз на 100 в каждой новой итерации
            chunk_size -= 100

            # Уменьшаем чанк сайз для всех элементов failed_chunks_list
            failed_chunks_list = (CharacterTextSplitter(separator=' ', chunk_size=chunk_size, chunk_overlap=0)
                                  .split_documents(failed_chunks_list))

            upload_doc_info.debug(f'Добавляем непрошедние чанки с chunk_size={chunk_size}, всего нужно еще добавить:'
                                  f' {len(failed_chunks_list)}.Их общая длина:'
                                  f' {sum(map(lambda x: len(x.page_content), failed_chunks_list))}')

            # Цикл с перебором всех значений failed_chunks_list
            for i in range(len(failed_chunks_list)):
                # Извлекаем первый элемент failed_chunks_list
                text = failed_chunks_list.pop(0)
                try:
                    # Пытаемся добавить в бд уже с уменьшенным чанк сайзом
                    vectordb.add_texts([text.page_content])
                except ResponseError:
                    upload_doc_info.warning(f'Чанк #{i} снова не прошел. Его длина: {len(text.page_content)}')
                    # Если опять ошибка, то добавляем этот элемент обратно в failed_chunks_list
                    # и он пойдет на второй круг еще с более маленьким чанк сайзом
                    failed_chunks_list.append(text)
                    continue

        # Раз вышли из цикла, значит все чанки добавлены в бд
        upload_doc_info.debug(f'created chroma collection in {self.config.PERSIST_DIRECTORY} with name {collection_name}')

        return

    def delete_collection(self, collection_name: str) -> None:
        if collection_name not in self.get_list_collections():
            raise ValueError('Collection with this name is not exist')
        collection = self.get_langchain_chroma(collection_name)
        collection.delete_collection()
        return

    def get_list_collections(self) -> list[str]:
        list_collections = self.client.list_collections()
        return list(map(lambda x: x.name, list_collections))

    def change_collection_name(self, current_collection_name: str, new_collection_name: str) -> None:
        if new_collection_name in self.get_list_collections():
            raise ValueError('Collection with this name is already exists')

        collection = self.client.get_collection(current_collection_name)
        collection.modify(new_collection_name)
        return

    def get_langchain_chroma(self, collection_name: str) -> Chroma:
        if collection_name not in self.get_list_collections():
            raise ValueError('Collection with this name is not exist')
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def sim_search(
        self,
        collection_name: str,
        query: str,
        k: int = 4,
        with_sim_scores: bool = False
    ) -> list[str] | tuple[list[str], list[float]]:
        collection = self.get_langchain_chroma(collection_name)
        if with_sim_scores:
            docs_with_scores = collection.similarity_search_with_score(query, k)
            docs, sim_scores = ([doc.page_content for doc, score in docs_with_scores],
                                [score for doc, score in docs_with_scores])
            return docs, sim_scores
        else:
            docs = collection.similarity_search(query, k)
            return [doc.page_content for doc in docs]

    def get_sim_scores(self, collection_name: str, query: str, k: int = 4):
        sim_scores = self.sim_search(collection_name, query, k, with_sim_scores=True)[1]
        return sim_scores

    def add_data(self, collection_name: str, texts: list[str]) -> None:
        collection = self.get_langchain_chroma(collection_name)
        collection.add_texts(texts)
        return

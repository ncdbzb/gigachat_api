from redisvl.extensions.llmcache import SemanticCache
from redisvl.utils.vectorize.text.custom import CustomTextVectorizer
from gigachatAPI.config_data.config import load_config, Config
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from typing import Optional, Callable, List


def init_llmcache(distance_threshold: float):

    config: Config = load_config()
    gigachat_embeddings = GigaChatEmbeddings(credentials=config.GIGA_CREDENTIALS,
                                             verify_ssl_certs=False)

    class NewCustomTextVectorizer(CustomTextVectorizer):
        def embed(
                self,
                text: str,
                preprocess: Optional[Callable] = None,
                as_buffer: bool = False,
                **kwargs,
        ) -> List[float]:
            """Embed a chunk of text using the provided function.

            Args:
                text (str): Chunk of text to embed.
                preprocess (Optional[Callable], optional): Optional preprocessing callable to
                    perform before vectorization. Defaults to None.
                as_buffer (bool, optional): Whether to convert the raw embedding
                    to a byte string. Defaults to False.

            Returns:
                List[float]: Embedding.

            Raises:
                TypeError: If the wrong input type is passed in for the text.
            """
            if not isinstance(text, str):
                raise TypeError("Must pass in a str value to embed.")

            if preprocess:
                text = preprocess(text)
            else:
                result = self._embed_func(text)
            return self._process_embedding(result, as_buffer, **kwargs)


    custom_vectorizer = NewCustomTextVectorizer(
        embed = gigachat_embeddings.embed_query
    )

    llmcache = SemanticCache(
        name="llmcache",
        redis_url="redis://redis:6379/0",
        distance_threshold=distance_threshold,
        vectorizer=custom_vectorizer,
    )

    return llmcache

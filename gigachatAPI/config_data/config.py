from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    GIGA_CREDENTIALS: str
    PERSIST_DIRECTORY: str
    CHROMA_SERVER_AUTHN_PROVIDER: str
    CHROMA_SERVER_AUTHN_CREDENTIALS: str
    CHROMA_CLIENT_AUTH_PROVIDER: str
    USE_SEMANTIC_CACHE: bool

def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        GIGA_CREDENTIALS=env('AU_DATA'),
        PERSIST_DIRECTORY=env('PERSIST_DIRECTORY'),
        CHROMA_SERVER_AUTHN_PROVIDER=env('CHROMA_SERVER_AUTHN_PROVIDER'),
        CHROMA_SERVER_AUTHN_CREDENTIALS=env('CHROMA_SERVER_AUTHN_CREDENTIALS'),
        CHROMA_CLIENT_AUTH_PROVIDER=env('CHROMA_CLIENT_AUTH_PROVIDER'),
        USE_SEMANTIC_CACHE=env('USE_SEMANTIC_CACHE')
    )

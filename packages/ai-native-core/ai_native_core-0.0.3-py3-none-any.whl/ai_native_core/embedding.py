import os
from typing import List

from langchain_core.embeddings import Embeddings
from tang_yuan_mlops_sdk.llm.embedding import EmbeddingClient


class BCEEmbeddings(Embeddings):
    def __init__(
            self,
            base_url: str = os.getenv('EMBEDDING_BASE_URL'),  # 使用配置文件中的值
            token: str = os.getenv('EMBEDDING_TOKEN'),  # 使用配置文件中的值
    ):
        self.client = EmbeddingClient(base_url=base_url, token=token)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        return [[0.5, 0.6, 0.7] for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous Embed search docs."""
        return await self.client.get_embeddings(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        embeddings = await self.client.get_embeddings([text])
        return embeddings[0]


embedding = BCEEmbeddings()

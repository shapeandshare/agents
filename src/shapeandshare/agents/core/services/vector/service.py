from chromadb import ClientAPI
from langchain_chroma.vectorstores import Chroma
from langchain_core.embeddings.embeddings import Embeddings
from pydantic import BaseModel


class VectorService(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    client: ClientAPI
    embedder: Embeddings

    def get_vectorstore(self, collection_id: str) -> Chroma:
        return Chroma(client=self.client, collection_name=collection_id, embedding_function=self.embedder)

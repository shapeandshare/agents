import os
from typing import Sequence

import chromadb
from chromadb import ClientAPI
from chromadb.api.models.Collection import Collection

from .....git.sdk.contracts.dtos.chat import BaseChatRequest
from .....git.sdk.contracts.dtos.git_metadata import GitMetadata
from .....git.services.metadata.service import MetadataService
from ....services.vector.service import VectorService


class ChromaUtils:
    @staticmethod
    def exists(
        vector_service: VectorService, metadata_service: MetadataService, request: BaseChatRequest
    ) -> str | None:
        metadata: GitMetadata = metadata_service.get(request=request)

        if metadata is None or (metadata and metadata.col_id is None):
            return None

        collections: Sequence[Collection] = vector_service.client.list_collections()
        for col in collections:
            if metadata.col_id == col.name:
                return metadata.col_id
        return None


def get_chroma_client() -> ClientAPI:
    return chromadb.HttpClient(
        host=os.environ.get("CHROMADB_HOSTNAME", "localhost"), port=int(os.environ.get("CHROMADB_PORT", 8000))
    )

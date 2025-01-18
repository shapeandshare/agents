import secrets
import string

from pydantic import BaseModel

from ....core.framework.common.utils.hash import hash_it
from ....core.framework.contracts.errors.dao.doesnotexist import DaoDoesNotExistError
from ....core.framework.contracts.types.dao_document import DaoDocumentType
from ....core.infrastructure.persistence.mongodb.dao_legacy import MongoDaoLegacy
from ...sdk.contracts.dtos.chat import BaseChatRequest, ChatRequest
from ...sdk.contracts.dtos.git_metadata import GitMetadata
from ...sdk.contracts.types.processing_status import ProcessingStatus


class MetadataService(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    dao: MongoDaoLegacy

    def delete(self, request: BaseChatRequest) -> None:
        storage_id: str = hash_it(payload=f"{request.id}:{request.url}")
        self.dao.delete(document_type=DaoDocumentType.METADATA, document_id=storage_id)

    def get(self, request: BaseChatRequest) -> GitMetadata | None:
        storage_id: str = hash_it(payload=f"{request.id}:{request.url}")
        document = self.dao.get(document_type=DaoDocumentType.METADATA, document_id=storage_id)
        if document is None:
            return None
        return GitMetadata.model_validate(document)

    def get_by_id(self, storage_id: str) -> GitMetadata | None:
        document = self.dao.get(document_type=DaoDocumentType.METADATA, document_id=storage_id)
        if document is None:
            return None
        return GitMetadata.model_validate(document)

    def create(self, request: ChatRequest) -> GitMetadata:
        storage_id: str = hash_it(payload=f"{request.id}:{request.url}")

        ## store and return chroma id
        alphabet = string.ascii_lowercase
        new_id: str = "".join(secrets.choice(alphabet) for _ in range(32))
        metadata: GitMetadata = GitMetadata(
            id=storage_id, col_id=new_id, conversation_id=request.conversation_id, status=ProcessingStatus.SUBMITTED
        )
        result = self.dao.insert(document_type=DaoDocumentType.METADATA, document=metadata.model_dump())
        print(result)
        return metadata

    def update(self, request: BaseChatRequest, metadata_partial: dict) -> GitMetadata:
        storage_id: str = hash_it(payload=f"{request.id}:{request.url}")
        metadata: GitMetadata | None = self.get_by_id(storage_id=storage_id)
        if metadata is None:
            raise DaoDoesNotExistError(f"Document with id {storage_id} does not exist")

        new_document: dict = {
            **metadata.model_dump(),
            **metadata_partial,
            **{"id": metadata.id, "col_id": metadata.col_id, "conversation_id": metadata.conversation_id},
        }
        metadata: GitMetadata = GitMetadata.model_validate(new_document)
        self.dao.update(document_type=DaoDocumentType.METADATA, document=new_document)
        return metadata

    def update_by_id(self, storage_id: str, metadata_partial: dict) -> GitMetadata:
        metadata: GitMetadata | None = self.get_by_id(storage_id=storage_id)
        if metadata is None:
            raise DaoDoesNotExistError(f"Document with id {storage_id} does not exist")

        new_document: dict = {
            **metadata.model_dump(),
            **metadata_partial,
            **{"id": metadata.id, "col_id": metadata.col_id, "conversation_id": metadata.conversation_id},
        }
        metadata: GitMetadata = GitMetadata.model_validate(new_document)
        self.dao.update(document_type=DaoDocumentType.METADATA, document=new_document)
        return metadata

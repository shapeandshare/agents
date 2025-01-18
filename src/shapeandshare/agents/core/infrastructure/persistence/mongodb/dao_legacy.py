import os
from urllib.parse import quote_plus

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult

from ....framework.contracts.errors.dao.conflict import DaoConflictError
from ....framework.contracts.types.dao_document import DaoDocumentType


def get_mongodb() -> Database:
    username: str = os.environ["MONGODB_USERNAME"]
    password: str = os.environ["MONGODB_PASSWORD"]
    hostname: str = os.environ["MONGODB_HOSTNAME"]
    port: int = int(os.environ["MONGODB_PORT"])
    database: str = os.environ["MONGODB_DATABASE"]

    uri: str = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{hostname}"
    return MongoClient(host=uri, port=int(port))[database]


class MongoDaoLegacy(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    database: Database
    collections: dict[DaoDocumentType, Collection] = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # our collections will match our document types
        for member in DaoDocumentType:
            # Create a collection for each document type
            self.collections[DaoDocumentType[member.name]] = self.database[member.value]

            # We add a single column index on the business logic layer `id` for our lookups:
            # db.<collection>.createIndex( { <field>: <sortOrder> } )
            self.collections[DaoDocumentType[member.name]].create_index({"id": 1})

    def delete(self, document_type: DaoDocumentType, document_id: str) -> None:
        self.collections[document_type].delete_one({"id": document_id})

    def get(self, document_type: DaoDocumentType, document_id: str) -> dict | None:
        return self.collections[document_type].find_one({"id": document_id})

    def insert(self, document_type: DaoDocumentType, document: dict) -> InsertOneResult:
        if self.get(document_type=document_type, document_id=document["id"]) is not None:
            raise DaoConflictError(f"Document with id {document['id']} already exists")
        return self.collections[document_type].insert_one(document)

    def update(self, document_type: DaoDocumentType, document: dict, upsert: bool = False) -> UpdateResult:
        return self.collections[document_type].update_one(
            filter={"id": document["id"]}, update={"$set": document}, upsert=upsert
        )

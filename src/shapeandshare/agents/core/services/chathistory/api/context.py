import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..sdk.storage.mongodb import MongoDBStorage
from ..service import ChatHistoryService

logger = logging.getLogger()

context = {}


@asynccontextmanager
# pylint: disable-next=unused-argument
async def lifespan(app: FastAPI):
    logger.info("[ContextManager] Building Context")
    context["chathistory_service"] = ChatHistoryService(storage=MongoDBStorage())
    logger.info("[ContextManager] Done")
    yield

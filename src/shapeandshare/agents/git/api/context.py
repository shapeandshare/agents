import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..context import build_runtime_context

logger = logging.getLogger()


@asynccontextmanager
# pylint: disable-next=unused-argument
async def lifespan(app: FastAPI):
    #  https://openai.com/api/pricing/
    # model="gpt-4o"
    # model="o1-mini"

    logger.info("[ContextManager] Building Git Agent Runtime Context")
    build_runtime_context()
    logger.info("[ContextManager] Done")
    yield

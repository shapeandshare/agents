import logging

from fastapi import APIRouter, BackgroundTasks, Depends, status

from ....sdk.contracts.dtos.response import Response
from ...agent import GitAgent
from ...context import context
from ...sdk.contracts.dtos.chat import BaseChatRequest, ChatRequest
from ...sdk.contracts.dtos.git_metadata import GitMetadata
from ...sdk.contracts.dtos.status_update import RepositoryStatusUpdateRequest
from ...services.metadata.service import MetadataService
from ..middleware.error import error_handler

router: APIRouter = APIRouter(
    prefix="/git",
    tags=["chat"],
)

logger = logging.getLogger()


async def get_agent() -> GitAgent:
    return context["agent"]


async def get_metadata_service() -> MetadataService:
    return context["metadata_service"]


async def delete_repository_context(request: BaseChatRequest, agent: GitAgent) -> None:
    msg: str = f"Deleting repository context: {request.model_dump()}"
    logger.info(msg)
    await agent.delete_context(request=request)
    msg = f"Done deleting repository context {request.model_dump()}"
    logger.info(msg)


# start a new session
@router.post("/question")
@error_handler
async def create_chat(request: ChatRequest, agent: GitAgent = Depends(get_agent)) -> Response[dict]:
    msg: str = f"Creating chat: {request.model_dump()}"
    logger.info(msg)
    result: dict = await agent.generate_chat_response(request=request)
    return Response[dict](data=result)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@error_handler
async def ingest_repository(request: BaseChatRequest, agent: GitAgent = Depends(get_agent)) -> Response[GitMetadata]:
    metadata: GitMetadata = await agent.process_repository(request)
    return Response[GitMetadata](data=metadata)


@router.delete("", status_code=status.HTTP_202_ACCEPTED)
@error_handler
async def delete_repository(
    request: BaseChatRequest, background_tasks: BackgroundTasks, agent: GitAgent = Depends(get_agent)
) -> None:
    background_tasks.add_task(delete_repository_context, request, agent)


@router.put("", status_code=status.HTTP_200_OK)
@error_handler
async def update_repository_status(
    request: RepositoryStatusUpdateRequest, service: MetadataService = Depends(get_metadata_service)
) -> Response[GitMetadata]:
    metadata: GitMetadata = service.update_by_id(
        storage_id=request.repository_id, metadata_partial={"status": request.status}
    )
    return Response[GitMetadata](data=metadata)

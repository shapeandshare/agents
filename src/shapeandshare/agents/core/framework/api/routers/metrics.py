from fastapi import APIRouter

from .....sdk.contracts.dtos.response import Response

router: APIRouter = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/health")
async def health_get() -> Response[dict]:
    response: Response[dict] = Response[dict](data={"healthy": True})
    return response

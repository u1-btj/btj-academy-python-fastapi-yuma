from fastapi import APIRouter, Response

from .base_schemas import BaseResponse
router = APIRouter(prefix="/health")
tag = "Health"

@router.get(
    path="",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_model=BaseResponse,
)
def get_health(response: Response) -> BaseResponse:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return BaseResponse(message="OK")
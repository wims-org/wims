from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="")


@router.get("/openapi.json", include_in_schema=False)
async def custom_openapi(request: Request):
    """
    Serve the OpenAPI spec for frontend code generation.
    """
    return JSONResponse(request.app.openapi())

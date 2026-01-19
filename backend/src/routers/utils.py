from fastapi import Request

from dependencies.backend_service import BackendService


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service

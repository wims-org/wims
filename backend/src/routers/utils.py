from fastapi import Request
from pydantic_core import ValidationError

from dependencies.backend_service import BackendService


def get_bs(request: Request) -> BackendService:
    """
    Return the backend service
    """
    return request.app.state.backend_service

def get_db(request: Request) -> BackendService:
    """
    Return the DB object for MongoDB
    """
    return request.app.state.backend_service.dbc.db


def parse_pydantic_errors(err: ValidationError) -> list[str]:
    """
    Take a Pydantic ValidationError and render them into acceptable strings to print
    """
    x = []
    for e in err.errors():
        fields = ", ".join(map(str,e['loc']))
        errorstring = f"{ fields } - { e['msg'] } "
        x.append(errorstring)
    return x

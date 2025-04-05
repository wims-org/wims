import os
import sys
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient


# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from main import app  # Import your FastAPI app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url="http://localhost:5005") as ac:
        yield ac

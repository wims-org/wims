
import pytest
from fastapi import status
from httpx import AsyncClient

import main  # Import your FastAPI app


@pytest.mark.asyncio
async def test_read_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_test_db_connection_success(async_client: AsyncClient, mocker):
    mocker.patch("main.app.state.backend_service.db.connect",
                 return_value=None)
    mocker.patch("main.app.state.backend_service.db.disconnect",
                 return_value=None)
    response = await async_client.get("/test-db")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Database connection successful"}


@pytest.mark.asyncio
async def test_test_db_connection_failure(async_client: AsyncClient, mocker):
    mocker.patch("main.app.state.backend_service.db.connect",
                 side_effect=Exception("Connection failed"))
    response = await async_client.get("/test-db")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Database connection failed: Connection failed"}


@pytest.mark.asyncio
async def test_message_stream(async_client: AsyncClient, mocker):
    mocker.patch("main.app.state", mocker.Mock())
    main.app.state.backend_service.readers = {"test_reader": []}
    response = await async_client.get("/stream?reader=test_reader")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_handle_message(async_client: AsyncClient, mocker):
    mocker.patch("main.logger.debug")
    await main.handle_message("test_message", "test_topic")
    main.logger.debug.assert_called_with(
        "Handle message: test_message on topic test_topic")


@pytest.mark.asyncio
async def test_lifespan(async_client: AsyncClient, mocker):
    mocker.patch("main.config", {"database": {}, "mqtt": {}, "frontend": {}})
    mocker.patch("main.BackendService")
    async with main.lifespan(main.app):
        assert main.app.state.config == {
            "database": {}, "mqtt": {}, "frontend": {}}
        assert isinstance(main.app.state.backend_service, mocker.Mock)


@pytest.mark.asyncio
async def test_get_message():
    message = main.get_message()
    assert isinstance(message, str)
    assert len(message) > 0


@pytest.mark.asyncio
async def test_setup_middleware(mocker):
    mock_app = mocker.Mock()
    mocker.patch("main.config", {"frontend": {
                 "host": "localhost", "port": "8080"}})
    main.setup_middleware(mock_app)
    mock_app.add_middleware.assert_called_once_with(
        main.CORSMiddleware,
        allow_origins=[
            "http://localhost:5000",
            "http://localhost:5002",
            "http://localhost:5005",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://localhost",
            "https://localhost",
            "http://localhost:8080",
            "http://localhost:8080"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@pytest.mark.asyncio
async def test_event_generator(mocker):
    mock_request = mocker.Mock()
    mock_request.is_disconnected = mocker.AsyncMock(return_value=False)
    mocker.patch("main.MESSAGE_STREAM_DELAY", 0.1)


@pytest.mark.asyncio
async def test_handle_message(async_client: AsyncClient, mocker):
    mocker.patch("main.logger.debug")
    await main.handle_message("test_message", "test_topic")
    main.logger.debug.assert_called_with(
        "Handle message: test_message on topic test_topic")


@pytest.mark.asyncio
async def test_lifespan(async_client: AsyncClient, mocker):
    mocker.patch("main.config", {"database": {}, "mqtt": {}, "frontend": {}})
    mocker.patch("main.BackendService")
    async with main.lifespan(main.app):
        assert main.app.state.config == {
            "database": {}, "mqtt": {}, "frontend": {}}
        assert isinstance(main.app.state.backend_service, mocker.Mock)


@pytest.mark.asyncio
async def test_get_message():
    message = main.get_message()
    assert isinstance(message, str)
    assert len(message) > 0

import asyncio
import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request

from dependencies import settings
from modules.chatgpt import ChatGPT

wims_config = settings.get_settings()


class LLMFactory:
    _instance: ChatGPT | None = None

    @classmethod
    def get_instance(cls) -> ChatGPT:
        if cls._instance is None:
            # Read the schema from the file
            with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
                schema = json.load(schema_file)

            cls._instance = ChatGPT(api_key=wims_config.features_openai_api_key, response_schema=schema)
        return cls._instance


# Dependency
async def event_handler_dependency() -> AsyncGenerator[ChatGPT]:
    async with asyncio.Lock():
        yield LLMFactory.get_instance()


LLMDep = Annotated[ChatGPT, Depends(event_handler_dependency)]


async def get_event_handler(request: Request, event_handler: LLMDep) -> None:
    return event_handler

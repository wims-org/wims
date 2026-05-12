import base64

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

_SYSTEM_PROMPT = (
    "You are an expert at identifying items found in a makerspace (electronics, tools, hardware, "
    "consumables, etc.) from photos and text descriptions. "
    "Use all provided information to fill every requested field as accurately and completely as possible. "
    "For prices, estimate in euro cents based on current market prices if not clearly visible."
)


class LLMIdentification(BaseModel):
    pass


class ChatGPT(LLMIdentification):
    model_config: dict = {"arbitrary_types_allowed": True}
    client: OpenAI | None = None
    response_schema: dict | None = None

    def __init__(self, api_key: str, response_schema: dict):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.response_schema = response_schema

    def identify_object(
        self,
        query: str | None = None,
        images: list[tuple[bytes, str]] | None = None,
    ) -> ChatCompletion:
        content: list[dict] = []
        if query:
            content.append({"type": "text", "text": query})
        for image_bytes, mime_type in images or []:
            b64 = base64.b64encode(image_bytes).decode()
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{b64}", "detail": "high"},
                }
            )
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_schema", "json_schema": self.response_schema},
            temperature=0,
            max_completion_tokens=1024,
        )

    def identify_string(self, query: str):
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": [{"type": "text", "text": query}]},
            ],
            response_format={"type": "json_schema", "json_schema": self.response_schema},
            temperature=0,
            max_completion_tokens=1024,
        )

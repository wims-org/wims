from openai import OpenAI
from pydantic import BaseModel


class IdentificationRequest(BaseModel):
    photo: bytes


class LLMCompletion(BaseModel):
    pass


class ChatGPT(LLMCompletion):
    model_config: dict = {"arbitrary_types_allowed": True}
    client: OpenAI | None = None
    response_schema: dict | None = None

    def __init__(self, api_key: str, response_schema: dict):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.response_schema = response_schema

    def identify_object(self, query: str = None, imageUrls: list[str] = None):
        image_url = imageUrls[0] if imageUrls else None
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Du bist ein Experte im Identifizieren von Dingen im Kontext eines "
                            "Makerspacers, u.a. Elektronik, Fahrrad, Werkzeuge, anhand von Fotos und St"
                            "ichworten. Nutze die gegebenen Informationen, um alle angeforderten Daten "
                            "so präzise und vollständig wie möglich zusammenzutragen.",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                },
            ],
            response_format={"type": "json_schema", "json_schema": self.response_schema},
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

    def identify_string(self, query: str):
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Du bist ein Experte im Identifizieren von Dingen im Kontext eines "
                            "Makerspacers, u.a. Elektronik, Fahrrad, Werkzeuge, anhand von Fotos und St"
                            "ichworten. Nutze die gegebenen Informationen, um alle angeforderten Daten "
                            "so präzise und vollständig wie möglich zusammenzutragen.",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": query,
                    },
                },
            ],
            response_format={"type": "json_schema", "json_schema": self.response_schema},
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

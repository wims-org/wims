import json
from pathlib import Path

import yaml
from openai import OpenAI
from pydantic import BaseModel

# Load the configuration file
with open(Path(__file__).parent.parent / "config.yml") as config_file:
    config = yaml.safe_load(config_file)

# Initialize the OpenAI client with the API key from the configuration file
client = OpenAI(api_key=config["features"]["openai"]["api_key"])


class IdentificationRequest(BaseModel):
    photo: bytes


# Read the schema from the file
with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
    schema = json.load(schema_file)


def identify_object(query: str = None, files: list[bytes] = None):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "Du bist ein Experte im Identifizieren von Dingen im Kontext eines Makerspacers, u.a. "
                        "Elektronik, Fahrrad, Werkzeuge, anhand von Fotos und Stichworten. Nutze die gegebenen Informa"
                        "tionen, um alle angeforderten Daten so präzise und vollständig wie möglich zusammenzutragen.",
                    }
                ],
            },
            {"role": "user", "content": files},
            {"role": "user", "content": [{"type": "text", "text": query}]},
        ],
        response_format={"type": "json_schema", "json_schema": schema},
        temperature=0,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )


def identify_string(query: str):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "Du bist ein Experte im Identifizieren von Dingen im Kontext eines Makerspacers, u.a. "
                        "Elektronik, Fahrrad, Werkzeuge, anhand von Fotos und Stichworten. Nutze die gegebenen Informa"
                        "tionen, um alle angeforderten Daten so präzise und vollständig wie möglich zusammenzutragen.",
                    }
                ],
            },
        ],
        response_format={"type": "json_schema", "json_schema": schema},
        temperature=0,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

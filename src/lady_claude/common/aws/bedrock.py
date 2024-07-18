import json
from typing import Dict, List

import boto3


def converse(
    message: str,
    model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature: float = 0.1,
    system_message: str | None = None,
    tool_config: Dict | None = None,
) -> dict:
    bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

    params = {
        "modelId": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": message,
                    }
                ],
            }
        ],
        "inferenceConfig": {
            "maxTokens": 4096,
            "temperature": temperature,
        },
    }

    if system_message is not None:
        params["system"] = [
            {
                "text": system_message,
            }
        ]

    if tool_config is not None:
        params["toolConfig"] = tool_config

    return bedrock_client.converse(**params)


def embed(
    text: str,
    embedding_model: str = "cohere.embed-multilingual-v3",
) -> List[float]:
    bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

    response = bedrock_client.invoke_model(
        body=json.dumps(
            {
                "texts": [text],
                "input_type": "search_document",
            }
        ),
        modelId=embedding_model,
    )
    response_body = json.loads(response["body"].read())

    return response_body["embeddings"][0]

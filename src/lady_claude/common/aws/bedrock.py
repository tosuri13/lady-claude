import boto3


def invoke_claude(
    message: str,
    model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
    system_message: str | None = None,
    temperature: float = 0.1,
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

    return bedrock_client.converse(**params)

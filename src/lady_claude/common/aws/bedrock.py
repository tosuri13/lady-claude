import boto3
import json


def get_text(
    message: str,
    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
    system_message: str = "",
) -> str:
    bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message,
                            }
                        ],
                    }
                ],
                "system": system_message,
                "temperature": 0.2,
            }
        ),
    )
    reslut = json.loads(response.get("body").read())

    return reslut["content"][0]["text"]

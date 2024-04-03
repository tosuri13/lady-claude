import json
import requests

from penguinator.common.aws.ssm import get_parameter
from penguinator.common.event.penguinator import PenguinatorCommand


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != PenguinatorCommand.ASK.value:
                raise ValueError(
                    f"This Lambda only supports '/ask' [command: /{command}]"
                )

            request = json.loads(message)
            content = _handle_request(request)
            _respond_discord(content, token=request["token"])

    except Exception as exception:
        raise exception

    return None


def _handle_request(request: dict) -> str:
    return "へろ〜"


def _respond_discord(content: str, token: str) -> None:
    application_id = get_parameter(key="/PENGUINATOR/DISCORD_APPLICATION_ID")

    requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{token}",
        data=json.dumps(
            {
                "content": content,
            }
        ),
        headers={
            "Authorization": f"Bot {get_parameter(key='/PENGUINATOR/DISCORD_BOT_TOKEN')}",
            "Content-Type": "application/json",
        },
    )

    return None

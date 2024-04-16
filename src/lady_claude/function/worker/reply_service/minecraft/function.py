import json

from lady_claude.common.aws.ec2 import get_instance_public_ip, start_instance
from lady_claude.common.aws.ssm import get_parameter
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.util import get_lady_error_comment
from lady_claude.common.event.lady_claude import (
    LadyClaudeCommand,
    LadyClaudeMinecraftOptionCommand,
)


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != LadyClaudeCommand.MINECRAFT.value:
                raise ValueError(
                    f"This Lambda only supports '/{LadyClaudeCommand.MINECRAFT.value}' [command: /{command}]"
                )

            request = json.loads(message)
            content = _handle_request(request)
            respond_interaction(content, interaction_token=request["token"])

    except Exception as exception:
        respond_interaction(
            get_lady_error_comment(exception),
            interaction_token=request["token"],
        )

    return None


def _handle_request(request: dict) -> str:
    options = get_option_dict(request["data"]["options"])
    instance_id = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT_SERVER_INSTANCE_ID"
    )

    match options["action"]:
        case LadyClaudeMinecraftOptionCommand.START.value:
            start_instance(instance_id)
            public_ip = get_instance_public_ip(instance_id)

            content = f"IPアドレスですわ!!: {public_ip}"
        case _:
            content = "未実装ですわ!!"

    return content

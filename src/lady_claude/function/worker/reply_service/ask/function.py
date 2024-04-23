import json

from lady_claude.common.ai.lady_claude import ask_lady
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.event.lady_claude import LadyClaudeCommand
from lady_claude.common.util import get_lady_error_comment


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != LadyClaudeCommand.ASK.value:
                raise ValueError(
                    f"This Lambda only supports '/{LadyClaudeCommand.ASK.value}' [command: /{command}]"
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

    return ask_lady(message=options["question"])

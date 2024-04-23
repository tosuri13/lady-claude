import json

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from lady_claude.common.aws.sns import publish_message
from lady_claude.common.aws.ssm import get_parameter
from lady_claude.common.event.discord import InteractionResponseType, InteractionType
from lady_claude.common.event.lady_claude import LadyClaudeCommand


def handler(event: dict, context: dict) -> dict:
    try:
        headers = {key.lower(): value for key, value in event["headers"].items()}

        if not _validate(headers, event["body"]):
            return {
                "statusCode": 401,
            }

        request = json.loads(event["body"])
        interaction_type = InteractionType(request["type"])

        if "name" in request["data"]:
            _publish_to_replyservice(
                message=json.dumps(request),
                command=LadyClaudeCommand(request["data"]["name"]),
            )

        return {
            "statusCode": 200,
            "body": json.dumps(_handle_interaction(interaction_type)),
            "headers": {
                "Content-Type": "application/json",
            },
        }

    except Exception as exception:
        return {
            "statusCode": 500,
            "body": f"{type(exception).__name__}: {exception}",
        }


def _validate(headers: dict, raw_body: str) -> bool:
    smessage = f"{headers['x-signature-timestamp']}{raw_body}".encode()
    signature = bytes.fromhex(headers["x-signature-ed25519"])

    verify_key = VerifyKey(
        bytes.fromhex(get_parameter(key="/LADY_CLAUDE/DISCORD/PUBLIC_KEY"))
    )

    try:
        verify_key.verify(smessage, signature)

    except BadSignatureError:
        return False

    return True


def _handle_interaction(interaction_type: InteractionType) -> dict:
    match interaction_type:
        case InteractionType.PING:
            return {
                "type": InteractionResponseType.PONG.value,
            }
        case InteractionType.APPLICATION_COMMAND:
            return {
                "type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE.value,
            }
        case _:
            raise ValueError()


def _publish_to_replyservice(message: str, command: LadyClaudeCommand) -> None:
    publish_message(
        topic_arn=get_parameter(key="/LADY_CLAUDE/REPLY_SERVICE/TOPIC_ARN"),
        message=message,
        message_attributes={
            "command": {
                "DataType": "String",
                "StringValue": command.value,
            }
        },
    )

    return None

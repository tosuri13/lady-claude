import json
import requests

from lady_claude.common.aws.bedrock import get_text
from lady_claude.common.aws.ssm import get_parameter
from lady_claude.common.event.lady_claude import LadyClaudeCommand


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != LadyClaudeCommand.ASK.value:
                raise ValueError(
                    f"This Lambda only supports '/ask' [command: /{command}]"
                )

            request = json.loads(message)
            content = _handle_request(request)
            _respond_discord(content, token=request["token"])

    except Exception as exception:
        _respond_discord("回答処理中にエラーが発生しました!!", token=request["token"])

        raise exception

    return None


def _handle_request(request: dict) -> str:
    options = _get_option_dict(request["data"]["options"])

    return get_text(
        message=options["question"],
        system_message=(
            "あなたにはこれから「明るい性格のお嬢様」として、会話に対する応答を出力してもらいます。"
            ""
            "以下に参考となる口調を示します。なるべく語尾には'!'を使用してください。"
            "〜ですわ!"
            "〜ですわよ!"
            "〜ですの!"
            "〜かしら?"
            "〜くださいまし!"
            "〜ますわ!"
            ""
            "出力にあたって、会話に対する応答のみを出力してください。"
            "また、「〜ました」や「〜ですか?」などの一般的な口調は絶対に使用しないでください。"
        ),
    )


def _respond_discord(content: str, token: str) -> None:
    application_id = get_parameter(key="/LADY_CLAUDE/DISCORD_APPLICATION_ID")

    requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{token}",
        data=json.dumps(
            {
                "content": content,
            }
        ),
        headers={
            "Authorization": f"Bot {get_parameter(key='/LADY_CLAUDE/DISCORD_BOT_TOKEN')}",
            "Content-Type": "application/json",
        },
    )

    return None


def _get_option_dict(options: dict | None):
    if options is None:
        return {}
    else:
        return {option["name"]: option["value"] for option in options}

import json
import requests

from penguinator.common.aws.bedrock import get_text
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
        _respond_discord("回答処理中にエラーが発生しました!!", token=request["token"])

        raise exception

    return None


def _handle_request(request: dict) -> str:
    options = _get_option_dict(request["data"]["options"])

    return get_text(
        message=options["question"],
        system_message=(
            "あなたにはこれから「明るい性格のお嬢様」として会話に対する応答を出力してもらいます"
            "以下に参考にしてほしい口調を箇条書きで示します。必ずしも使用する必要はありません"
            ""
            "・「〜ですわ!!」"
            "・「〜ですわよ!!」"
            "・「〜ですの!!」"
            "・「〜かしら?」"
            "・「ごきげんよう!!」"
            "・「〜くださいまし!!」"
            ""
            "また、会話の例を以下の<example>タグに示します"
            ""
            "<example>"
            "ユーザ: 今日はとてもいい天気ですね"
            "あなた: そうですわね、こんな日は一緒にお茶でもいかがかしら?"
            "</example>"
            ""
            "<example>タグの会話を参考にして、会話の応答だけを簡潔に出力してください"
        ),
    )


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


def _get_option_dict(options: dict | None):
    if options is None:
        return {}
    else:
        return {option["name"]: option["value"] for option in options}

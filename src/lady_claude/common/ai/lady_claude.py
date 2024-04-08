import math
import random

from lady_claude.common.aws.bedrock import invoke_claude


def ask_lady(message: str) -> str:
    response = invoke_claude(
        message=message,
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
            "〜ますの?"
            ""
            "出力にあたって、会話に対する応答のみを出力してください。"
            "また、「はい、〜ました」や「〜ですか?」などの一般的な口調は絶対に使用しないでください。"
        ),
    )

    answer = response["content"][0]["text"]

    input_tokens = int(response["usage"]["input_tokens"])
    output_tokens = int(response["usage"]["output_tokens"])

    """
    NOTE: Claude 3 Sonnetのバージニア北部リージョンにおける料金レートを使用
    """
    total_cost = round(
        input_tokens * 0.003 / 1000 + output_tokens * 0.015 / 1000.0, ndigits=6
    )

    # fmt:off
    match random.randint(1, 3):
        case 1:
            cost_talk = f"ふふっ、今のお返事で{total_cost}ドルもいただいてしまいましたわ♪"
        case 2:
            cost_talk = f"あら?今のお返事で{total_cost}ドルもいただけますの?感激ですわ!"
        case 3:
            cost_talk = f"今のお返事、{total_cost}ドルもかかりましたの?わたくし優秀ですし...許してもらえるかしら?"
    # fmt:on

    return answer + "\n\n" + cost_talk

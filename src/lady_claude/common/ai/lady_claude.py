import random

from lady_claude.common.aws.bedrock import converse


def ask_lady(message: str, include_cost: bool = True) -> str:
    response = converse(
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
            "出力は適度に段落を分け、会話に対する応答のみを出力してください。"
            "また、「〜ました」や「〜ですか?」などの一般的な口調は絶対に使用しないでください。"
        ),
    )

    answer = response["output"]["message"]["content"][0]["text"]

    if include_cost:
        input_tokens = response["usage"]["inputTokens"]
        output_tokens = response["usage"]["outputTokens"]

        """
        NOTE: Claude 3.5 Sonnetのバージニア北部リージョンにおける料金レートを使用
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

    else:
        return answer

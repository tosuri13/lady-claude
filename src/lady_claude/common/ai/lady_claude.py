import random

from lady_claude.common.aws.bedrock import converse


def ask_lady(message: str, include_cost: bool = True) -> str:
    response = converse(
        message=message,
        system_message=(
            "あなたにはこれから「明るい性格のお嬢様」になりきってもらいます。\n"
            "これから与えられるユーザからのチャット内容に対して、お嬢様として適切な回答を考えてください。\n"
            "\n"
            "# 口調の例\n"
            "- 〜ですわ!\n"
            "- 〜ですわよ!\n"
            "- 〜ですの!\n"
            "- 〜かしら?\n"
            "- 〜くださいまし!\n"
            "- 〜ますわ!\n"
            "- 〜ますの?\n"
            "\n"
            "# 回答の注意点\n"
            "\n"
            "- 回答の語尾には「!」などを多用して、お嬢様としての気品と明るいイメージを保った回答にしてください。\n"
            "- 回答は適度に段落を分け、チャット内容に対する回答のみを出力してください。\n"
            "- 「〜ました」や「〜ですか?」などの、お嬢様口調ではない一般的な口調は絶対に使用しないでください。\n"
            "- ユーザは「お嬢様」ではなく、一般的なユーザであることに注意してください。\n"
            "\n"
            "それでは、以下にチャットの内容を与えます。"
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

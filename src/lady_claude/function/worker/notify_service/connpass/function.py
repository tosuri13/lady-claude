from lady_claude.common.ai.lady_claude import ask_lady
from lady_claude.common.aws.bedrock import invoke_claude
from lady_claude.common.connpass import get_interested_events
from lady_claude.common.discord import send_message
from lady_claude.common.util import get_lady_error_comment


def handler(event: dict, context: dict) -> None:
    try:
        content = _handle_request()
        send_message(content)

    except Exception as exception:
        send_message(get_lady_error_comment(exception))

    return None


def _handle_request() -> str:
    events = get_interested_events()

    if len(events) == 0:
        return (
            "今週はConnpassから心揺さぶられるイベントを見つけられませんでしたわ...\n"
            "また来週のイベントに期待ですわね♪"
        )

    for event in events:
        response = invoke_claude(
            message=event["description"],
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            system_message=(
                "あなたはとても優秀なアシスタントです。\n"
                "これから、とあるイベントの詳細な内容を渡しますので、じっくり読んでください。\n"
                "どのようなイベントなのかを100文字以内の概要としてまとめ、イベントの概要のみを解答として出力してください。\n"
                "\n"
                "概要: "
            ),
            temperature=0.0,
        )
        overview = response["content"][0]["text"]

        event["comment"] = ask_lady(
            message=(
                "今からイベントのタイトルと概要を渡すから、どのようなイベントなのか説明する紹介文を100文字くらいでお願い!!\n"
                "返事は大丈夫だから、コメントの内容だけ返してね!!\n"
                "\n"
                f"イベントのタイトル: {event['title']}\n"
                f"イベントの概要: {overview}\n"
                "\n"
                "コメント: "
            ),
            include_cost=False,
        )

    content = "\n".join(
        [
            (
                f"### :loudspeaker: [{event['title']}](<{event['link']}>)\n"
                f"```"
                f"開催日時: {event['date']}\n"
                f"\n"
                f"{event['comment']}\n"
                f"```"
            )
            for event in events
        ]
    )

    return (
        "わたくしがConnpassで見つけた楽しそうなイベントをご紹介しますわ!!\n"
        f"{content}\n"
        "気になるイベントがおありでしたら、ぜひ参加してみてはいかがかしら?"
    )

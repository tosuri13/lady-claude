from datetime import datetime, timedelta, timezone

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
    day_texts = {
        0: (
            "明日は燃えるものを捨てる日ですわ!!\n"
            "9時までにお運びになるのを忘れないでくださいまし!!"
        ),
        1: (
            "明日は缶・びん・ペットボトルを捨てる日ですわ!!\n"
            "9時までにお運びになるのを忘れないでくださいまし!!"
        ),
        3: (
            "明日は燃えるものを捨てる日ですわ!!\n"
            "9時までにお運びになるのを忘れないでくださいまし!!"
        ),
        4: (
            "明日はダンボールを捨てる日ですわ!!\n"
            "毎週土曜とは限りませんので、雰囲気で近隣住民の皆様に合わせてくださいまし!!"
        ),
    }

    return day_texts[datetime.now(timezone(timedelta(hours=9))).weekday()]

import traceback


def get_lady_error_comment(exception: Exception) -> str:
    comment = (
        "あら?どこかでエラーが発生しているみたいですわね...セバスチャン(開発者)に連絡してくださる?\n"
        "```\n"
        f"{type(exception).__name__}: {exception}\n"
        f"{traceback.format_exc()}"
        "```\n"
    )

    return comment

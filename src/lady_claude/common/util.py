def get_lady_error_comment(exception: Exception) -> str:
    comment = (
        "あら?どこかでエラーが発生しているみたいですわね...セバスチャン(開発者)に聞いてくださる?\n"
        "```\n"
        f"{type(exception).__name__}: {exception}\n"
        "```\n"
    )

    return comment

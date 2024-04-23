import json

import requests

from lady_claude.common.aws.ssm import get_parameter


def respond_interaction(content: str, interaction_token: str) -> None:
    application_id = get_parameter(key="/LADY_CLAUDE/DISCORD/APPLICATION_ID")

    requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}",
        data=json.dumps(
            {
                "content": content,
            }
        ),
        headers={
            "Authorization": f"Bot {get_parameter(key='/LADY_CLAUDE/DISCORD/BOT_TOKEN')}",
            "Content-Type": "application/json",
        },
    )

    return None


def get_option_dict(options: dict | None):
    if options is None:
        return {}
    else:
        return {option["name"]: option["value"] for option in options}

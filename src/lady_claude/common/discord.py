import json
import os

import requests

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]


def respond_interaction(content: str, interaction_token: str) -> None:
    response = requests.post(
        url=f"https://discord.com/api/v10/webhooks/{DISCORD_APPLICATION_ID}/{interaction_token}",
        data=json.dumps(
            {
                "content": content,
            }
        ),
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code != 200:
        raise ValueError(
            f"Communication to Discord API failed. [reason: {response.text}]"
        )

    return None


def send_message(content: str) -> None:
    response = requests.post(
        url=f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages",
        data=json.dumps(
            {
                "content": content,
            }
        ),
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code != 200:
        raise ValueError(
            f"Communication to Discord API failed. [reason: {response.text}]"
        )

    return None


def get_option_dict(options: dict | None):
    if options is None:
        return {}
    else:
        return {option["name"]: option["value"] for option in options}

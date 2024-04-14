import json
import requests

from src.lady_claude.common.aws.ssm import get_parameter

APPLICATION_ID = get_parameter(key="/LADY_CLAUDE/DISCORD/APPLICATION_ID")
GUILD_ID = get_parameter(key="/LADY_CLAUDE/DISCORD/GUILD_ID")

AUTH_HEADERS = {
    "Authorization": f"Bot {get_parameter(key='/LADY_CLAUDE/DISCORD/BOT_TOKEN')}",
    "Content-Type": "application/json",
}


if __name__ == "__main__":
    response = requests.get(
        url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands",
        headers=AUTH_HEADERS,
    )

    for command in response.json():
        command_id = command["id"]

        requests.delete(
            url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands/{command_id}",
            headers=AUTH_HEADERS,
        )

    commands = [
        {
            "name": "ask",
            "description": "Claudeお嬢様に質問してみよう!!",
            "options": [
                {
                    "type": 3,
                    "name": "question",
                    "description": "質問したい内容を書いてね!!",
                    "required": True,
                }
            ],
        }
    ]

    for command in commands:
        response = requests.post(
            url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands",
            headers=AUTH_HEADERS,
            data=json.dumps(command),
        )

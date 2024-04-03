import json
import requests

from src.penguinator.common.aws.ssm import get_parameter

APPLICATION_ID = get_parameter(key="/PENGUINATOR/DISCORD_APPLICATION_ID")
GUILD_ID = get_parameter(key="/PENGUINATOR/DISCORD_GUILD_ID")

AUTH_HEADERS = {
    "Authorization": f"Bot {get_parameter(key='/PENGUINATOR/DISCORD_BOT_TOKEN')}",
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
            "description": "Ask something...",
        }
    ]

    for command in commands:
        response = requests.post(
            url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands",
            headers=AUTH_HEADERS,
            data=json.dumps(command),
        )

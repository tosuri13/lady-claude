import json
import requests

from src.penguinator.common.aws.ssm import get_parameter


def main():
    application_id = get_parameter("/PENGUINATOR/DISCORD_APPLICATION_ID")
    guild_id = get_parameter("/PENGUINATOR/DISCORD_GUILD_ID")

    endpoint_url = f"https://discord.com/api/v10/applications/{application_id}/guilds/{guild_id}/commands"
    headers = {
        "Authorization": f'Bot {get_parameter("/PENGUINATOR/DISCORD_BOT_TOKEN")}',
        "Content-Type": "application/json",
    }

    commands = [
        {
            "name": "hello",
            "description": "Hello Discord Slash Commands!",
        }
    ]

    for command in commands:
        response = requests.post(
            url=endpoint_url,
            headers=headers,
            data=json.dumps(command),
        )
        print(response)


if __name__ == "__main__":
    main()

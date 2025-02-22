import json
import os

import requests

from src.lady_claude.common.event.discord import ApplicationCommandOptionType
from src.lady_claude.common.event.lady_claude import LadyClaudeMinecraftOptionCommand

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

AUTH_HEADERS = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
}
COMMANDS_ENDPOINT_URL = (
    f"https://discord.com/api/v10/applications/{DISCORD_APPLICATION_ID}/commands"
)


if __name__ == "__main__":
    response = requests.get(
        url=COMMANDS_ENDPOINT_URL,
        headers=AUTH_HEADERS,
    )

    for command in response.json():
        command_id = command["id"]

        requests.delete(
            url=f"{COMMANDS_ENDPOINT_URL}/{command_id}",
            headers=AUTH_HEADERS,
        )

    commands = [
        {
            "name": "ask",
            "description": "Claudeお嬢様に質問してみよう!!",
            "options": [
                {
                    "name": "question",
                    "description": "質問したい内容を書いてね!!",
                    "required": True,
                    "type": ApplicationCommandOptionType.STRING.value,
                }
            ],
        },
        {
            "name": "minecraft",
            "description": "Claudeお嬢様にMinecraftサーバを操作してもらおう!!",
            "options": [
                {
                    "name": "action",
                    "choices": [
                        {
                            "name": "サーバを起動しますわ!!",
                            "value": LadyClaudeMinecraftOptionCommand.START.value,
                        },
                        {
                            "name": "サーバを停止しますわ!!",
                            "value": LadyClaudeMinecraftOptionCommand.STOP.value,
                        },
                        {
                            "name": "サーバの状態を確認いたしますわ!!",
                            "value": LadyClaudeMinecraftOptionCommand.STATUS.value,
                        },
                        {
                            "name": "ワールドのバックアップを取りますわ!!",
                            "value": LadyClaudeMinecraftOptionCommand.BACKUP.value,
                        },
                    ],
                    "description": "サーバへのアクションを選んでね!!",
                    "required": True,
                    "type": ApplicationCommandOptionType.STRING.value,
                }
            ],
        },
        {
            "name": "recipe",
            "description": "Claudeお嬢様にお料理のレシピを教えてもらおう!!",
            "options": [
                {
                    "name": "order",
                    "description": "レシピに関するお嬢様への命令を書いてね!!",
                    "required": True,
                    "type": ApplicationCommandOptionType.STRING.value,
                },
            ],
        },
    ]

    for command in commands:
        response = requests.post(
            url=COMMANDS_ENDPOINT_URL,
            headers=AUTH_HEADERS,
            data=json.dumps(command),
        )
        if response.status_code == 201:
            print(f'"{command["name"]}"コマンドの追加に成功しましたわ!!')
        else:
            print(f'"{command["name"]}"コマンドの追加に失敗してしまいましたわ...')

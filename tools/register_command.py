import json
import requests

from src.lady_claude.common.aws.ssm import get_parameter
from src.lady_claude.common.event.discord import ApplicationCommandOptionType
from src.lady_claude.common.event.lady_claude import LadyClaudeMinecraftOptionCommand

APPLICATION_ID = get_parameter(key="/LADY_CLAUDE/DISCORD/APPLICATION_ID")
AUTH_HEADERS = {
    "Authorization": f"Bot {get_parameter(key='/LADY_CLAUDE/DISCORD/BOT_TOKEN')}",
    "Content-Type": "application/json",
}


if __name__ == "__main__":
    response = requests.get(
        url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands",
        headers=AUTH_HEADERS,
    )

    for command in response.json():
        command_id = command["id"]

        requests.delete(
            url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands/{command_id}",
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
    ]

    for command in commands:
        response = requests.post(
            url=f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands",
            headers=AUTH_HEADERS,
            data=json.dumps(command),
        )
        if response.status_code == 201:
            print(f"\"{command['name']}\"コマンドの追加に成功しましたわ!!")
        else:
            print(f"\"{command['name']}\"コマンドの追加に失敗してしまいましたわ...")

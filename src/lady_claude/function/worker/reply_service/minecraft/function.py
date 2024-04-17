import json
import time

from lady_claude.common.aws.ec2 import describe_instance, start_instance
from lady_claude.common.aws.ssm import (
    get_command_invocation,
    get_parameter,
    send_command,
)
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.util import get_lady_error_comment
from lady_claude.common.event.lady_claude import (
    LadyClaudeCommand,
    LadyClaudeMinecraftOptionCommand,
)


def handler(event: dict, context: dict) -> None:
    try:
        for record in event["Records"]:
            message = record["Sns"]["Message"]
            message_attributes = record["Sns"]["MessageAttributes"]
            command = message_attributes["command"]["Value"]

            if command != LadyClaudeCommand.MINECRAFT.value:
                raise ValueError(
                    f"This Lambda only supports '/{LadyClaudeCommand.MINECRAFT.value}' [command: /{command}]"
                )

            request = json.loads(message)
            content = _handle_request(request)
            respond_interaction(content, interaction_token=request["token"])

    except Exception as exception:
        respond_interaction(
            get_lady_error_comment(exception),
            interaction_token=request["token"],
        )

    return None


def _handle_request(request: dict) -> str:
    options = get_option_dict(request["data"]["options"])
    instance_id = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT_SERVER_INSTANCE_ID"
    )

    match options["action"]:
        case LadyClaudeMinecraftOptionCommand.START.value:
            return _handle_start_action(instance_id)
        case _:
            return "未実装ですわ!!"


def _handle_start_action(instance_id: str) -> str:
    state = describe_instance(instance_id)["State"]["Name"]
    if state != "stopped":
        return "あら?インスタンスが「停止中」ではないみたいですわ...インスタンスの状態を確認してくださる?"

    start_instance(instance_id)
    public_ip = describe_instance(instance_id)["PublicIpAddress"]

    server_version = "1.20.4-forge"
    command_id = send_command(
        instance_id,
        commands=[
            f"cd /home/ec2-user/minecraft/servers/{server_version}",
            "nohup bash run.sh > nohup.log 2>&1 &",
        ],
    )

    status = get_command_invocation(command_id, instance_id)["Status"]
    if status != "Success":
        return "あら?コマンドの実行に失敗したみたいですわ...コマンドの履歴を確認してくださる?"

    """
    NOTE: Minecraftサーバにログインできるようになるまでタイムラグがあるため、サーバを起動してから20秒間待機する
    """
    time.sleep(20)

    return (
        f"Minecraftサーバ({server_version})を起動しましたわ!!\n"
        f"今回のIPアドレスは「{public_ip}」ですわよ。わたくしに感謝して存分に遊んでくださいまし!!"
    )

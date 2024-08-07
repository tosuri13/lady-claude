import json
import time
from datetime import datetime

from lady_claude.common.aws.ec2 import describe_instance, start_instance, stop_instance
from lady_claude.common.aws.ssm import (
    get_command_invocation,
    get_parameter,
    send_command,
)
from lady_claude.common.discord import get_option_dict, respond_interaction
from lady_claude.common.event.lady_claude import (
    LadyClaudeCommand,
    LadyClaudeMinecraftOptionCommand,
)
from lady_claude.common.util import get_lady_error_comment

MINECRAFT_INSTANCE_REGION = "ap-south-1"


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
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/SERVER_INSTANCE_ID"
    )

    match options["action"]:
        case LadyClaudeMinecraftOptionCommand.START.value:
            return _handle_start_action(instance_id)
        case LadyClaudeMinecraftOptionCommand.STOP.value:
            return _handle_stop_action(instance_id)
        case LadyClaudeMinecraftOptionCommand.STATUS.value:
            return _handle_status_action(instance_id)
        case LadyClaudeMinecraftOptionCommand.BACKUP.value:
            return _handle_backup_action(instance_id)
        case _:
            return (
                "わたくしそのようなアクションには対応しておりませんわ...セバスチャン(開発者)に聞いてくれるかしら?\n"
                "(どうやってわたくしに命じたのですの...?)"
            )


def _handle_start_action(instance_id: str) -> str:
    response = describe_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    state = response["State"]["Name"]
    if state != "stopped":
        return "あら?インスタンスが「停止済み」ではないみたいですわ...インスタンスの状態を確認してくださる?"

    start_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    response = describe_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    public_ip = response["PublicIpAddress"]

    server_version = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/SERVER_VERSION"
    )
    command_id = send_command(
        instance_id,
        commands=[
            f"export HOME=/root",
            f"source ~/.bashrc",
            f"cd /opt/minecraft/servers/{server_version}",
            f"nohup bash run.sh > nohup.log 2>&1 &",
        ],
        region_name=MINECRAFT_INSTANCE_REGION,
    )

    time.sleep(20)

    response = get_command_invocation(
        command_id,
        instance_id,
        region_name=MINECRAFT_INSTANCE_REGION,
    )
    status = response["Status"]
    if status != "Success":
        return "あら?コマンドの実行に失敗したみたいですわ...コマンドの履歴を確認してくださる?"

    return (
        f"Minecraftサーバ({server_version})を起動しましたわ!!\n"
        f"今回のIPアドレスは「{public_ip}」ですわ♪\n"
        f"最後にサーバを停止するのをお忘れないようにしてくださいまし!!"
    )


def _handle_stop_action(instance_id: str) -> str:
    response = describe_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    state = response["State"]["Name"]
    if state != "running":
        return "あら?インスタンスが「実行中」ではないみたいですわ...インスタンスの状態を確認してくださる?"

    bucket_name = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/BUCKUP_BUCKET_NAME"
    )
    server_version = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/SERVER_VERSION"
    )
    upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    command_id = send_command(
        instance_id,
        commands=[
            f"export HOME=/root",
            f"source ~/.bashrc",
            f"cd /opt/minecraft/servers/{server_version}",
            f"aws s3 cp world s3://{bucket_name}/{server_version}/{upload_time}/world --recursive",
            f"mcrcon -w 5 stop",
        ],
        region_name=MINECRAFT_INSTANCE_REGION,
    )

    time.sleep(15)

    response = get_command_invocation(
        command_id, instance_id, region_name=MINECRAFT_INSTANCE_REGION
    )
    status = response["Status"]
    if status != "Success":
        return "あら?コマンドの実行に失敗したみたいですわ...コマンドの履歴を確認してくださる?"

    stop_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)

    return (
        f"Minecraftサーバ({server_version})を停止しましたわ!!\n"
        f"自動でバックアップも保存しておりますわよ!!"
        f"また遊びたくなったら、いつでもわたくしをお呼びくださいまし!!\n"
    )


def _handle_status_action(instance_id: str) -> str:
    response = describe_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    state = response["State"]["Name"]
    match state:
        case "running":
            return (
                "Minecraftサーバは「実行中」ですわ!!\n"
                "誰も遊んでおられないのなら、わたくしにサーバの停止を命じてくださいまし!!"
            )
        case "stopped":
            return (
                "Minecraftサーバは「停止済み」ですわ!!\n"
                "ふふっ、遊びたいのかしら?でしたら、わたくしにサーバの起動を命じてくださいまし!!"
            )
        case _:
            return (
                "あら?Minecraftサーバは「実行中」でも「停止済み」でもないみたいですわ...\n"
                "少し時間をおいて、もう一度わたくしにサーバの確認を命じてもらえるかしら?"
            )


def _handle_backup_action(instance_id: str) -> str:
    response = describe_instance(instance_id, region_name=MINECRAFT_INSTANCE_REGION)
    state = response["State"]["Name"]
    if state != "running":
        return "あら?インスタンスが「実行中」ではないみたいですわ...インスタンスの状態を確認してくださる?"

    bucket_name = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/BUCKUP_BUCKET_NAME"
    )
    server_version = get_parameter(
        key="/LADY_CLAUDE/REPLY_SERVICE/MINECRAFT/SERVER_VERSION"
    )
    upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    command_id = send_command(
        instance_id,
        commands=[
            f"export HOME=/root",
            f"source ~/.bashrc",
            f"cd /opt/minecraft/servers/{server_version}",
            f"aws s3 cp world s3://{bucket_name}/{server_version}/{upload_time}/world --recursive",
        ],
        region_name=MINECRAFT_INSTANCE_REGION,
    )

    response = get_command_invocation(
        command_id, instance_id, region_name=MINECRAFT_INSTANCE_REGION
    )
    status = response["Status"]
    if status != "Success":
        return "あら?コマンドの実行に失敗したみたいですわ...コマンドの履歴を確認してくださる?"

    return (
        "ワールドのバックアップを取得しましたわ!!\n"
        "ワールドの復旧は、わたくしではなくセバスチャン(開発者)に命令してくださいまし!!"
    )

import boto3

from typing import List


def get_parameter(key: str) -> str:
    ssm_client = boto3.client("ssm", region_name="ap-northeast-1")

    response = ssm_client.get_parameter(Name=key)

    return response["Parameter"]["Value"]


def send_command(instance_id: str, commands: List[str]) -> str:
    ssm_client = boto3.client("ssm", region_name="ap-northeast-1")

    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": commands,
        },
    )
    command_id = response["Command"]["CommandId"]

    ssm_waiter = ssm_client.get_waiter("command_executed")
    ssm_waiter.wait(
        CommandId=command_id,
        InstanceId=instance_id,
    )

    return command_id


def get_command_invocation(command_id: str, instance_id: str) -> dict:
    ssm_client = boto3.client("ssm", region_name="ap-northeast-1")

    return ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )

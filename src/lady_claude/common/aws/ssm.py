from typing import List

import boto3


def get_parameter(key: str, region_name: str = "ap-northeast-1") -> str:
    ssm_client = boto3.client("ssm", region_name)

    response = ssm_client.get_parameter(Name=key)

    return response["Parameter"]["Value"]


def send_command(
    instance_id: str, commands: List[str], region_name: str = "ap-northeast-1"
) -> str:
    ssm_client = boto3.client("ssm", region_name)

    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": commands,
        },
    )
    command_id = response["Command"]["CommandId"]

    return command_id


def get_command_invocation(
    command_id: str, instance_id: str, region_name: str = "ap-northeast-1"
) -> dict:
    ssm_client = boto3.client("ssm", region_name)

    return ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )

import boto3


def get_parameter(key: str) -> str:
    ssm_client = boto3.client("ssm", region_name="ap-northeast-1")

    response = ssm_client.get_parameter(Name=key)

    return response["Parameter"]["Value"]

import boto3


def start_instance(instance_id: str) -> None:
    ec2_client = boto3.client("ec2", region_name="ap-northeast-1")

    ec2_client.start_instances(InstanceIds=[instance_id])

    ec2_waiter = ec2_client.get_waiter("instance_running")
    ec2_waiter.wait(InstanceIds=[instance_id])

    return None


def get_instance_public_ip(instance_id: str) -> str:
    ec2_client = boto3.client("ec2", region_name="ap-northeast-1")

    response = ec2_client.describe_instances(InstanceIds=[instance_id])

    return response["Reservations"][0]["Instances"][0]["PublicIpAddress"]

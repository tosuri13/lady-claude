import boto3


def publish_message(topic_arn: str, message: str, message_attributes: dict) -> None:
    sns_client = boto3.client("sns", region_name="ap-northeast-1")

    sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        MessageAttributes=message_attributes,
    )

    return None

import boto3


def upload(
    bucket_name: str,
    object_name: str,
    file_name: str,
    region_name: str = "ap-northeast-1",
) -> None:
    s3_client = boto3.client("s3", region_name)

    s3_client.upload_file(
        Filename=file_name,
        Bucket=bucket_name,
        Key=object_name,
    )

    return None


def download(
    bucket_name: str,
    object_name: str,
    file_name: str,
    region_name: str = "ap-northeast-1",
) -> None:
    s3_client = boto3.client("s3", region_name)

    s3_client.download_file(
        Bucket=bucket_name,
        Key=object_name,
        Filename=file_name,
    )

    return None

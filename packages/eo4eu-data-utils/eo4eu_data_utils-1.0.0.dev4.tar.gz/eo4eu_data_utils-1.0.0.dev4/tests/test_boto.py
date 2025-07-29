import os
import time
import boto3
import botocore
import logging
from pathlib import Path
from pprint import pprint


logger = logging.getLogger("test")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


boto_config = {
    "region_name": "us-east-1",
    "endpoint_url": os.environ["S3_ENDPOINT_URL"],
    "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
    "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
}


if __name__ == "__main__":
    resource = boto3.resource(
        "s3",
        **boto_config,
        config = botocore.config.Config(
            request_checksum_calculation = "when_required",
        )
    )
    bucket = resource.Bucket("test_pre_pro-base")
    bucket.put_object(
        Key = "logs/dummy.txt",
        Body = bytes("dummy", "utf-8"),
    )

from eo4eu_data_utils.drivers import S3Driver
from eo4eu_data_utils.config import ConfigBuilder, Try
from eo4eu_data_utils.pipeline import Pipeline, then
from pprint import pprint
from pathlib import Path
try:
    from typing import Self
except Exception:
    from typing_extensions import Self
from enum import Enum
import logging
import re
import os

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = {
    "boto": {
        "region_name": "us-east-1",
        "endpoint_url": os.environ["S3_ENDPOINT_URL"],
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    },
    "bucket": "apollo-test"
}

if __name__ == "__main__":
    s3_driver = S3Driver(
        config = config["boto"],
        bucket = config["bucket"]
    )

    pipeline = Pipeline(
        logger = logger,
        summary = logger,
    )

    result = (pipeline
        .source(s3_driver)
        .download("download")
        .exec()
    )

    pprint(result)
